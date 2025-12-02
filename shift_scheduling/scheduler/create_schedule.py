import datetime
import calendar
from ortools.sat.python import cp_model
import math

def create_schedule(schedule_period: datetime.date, employees):
    model = cp_model.CpModel()

    num_days = calendar.monthrange(schedule_period.year, schedule_period.month)[1]
    shift_interval = math.floor(num_days/math.ceil((num_days*2)/employees.count()))
    shift_interval_violations = []

    month_cal = calendar.monthcalendar(schedule_period.year, schedule_period.month)
    weekends = []
    for week in month_cal:
        for i, day in enumerate(week):
            if i >= 5 and day != 0:
                weekends.append(day)

    # decision variables
    decision_vars = {}
    
    # auxiliary variables
    employee_shift_count = {}
    employee_wknd_shift_count = {}
    max_shifts = model.new_int_var(0, num_days, 'max_shifts')
    min_shifts = model.new_int_var(0, num_days, 'min_shifts')
    min_wknd_shifts = model.new_int_var(0, len(weekends), 'min_wknd_shifts')
    max_wknd_shifts = model.new_int_var(0, len(weekends), 'max_wknd_shifts')

    for e in employees:
        decision_vars[e.id] = {}
        employee_shift_count[e.id] = model.new_int_var(0, num_days, f'{e.id}_shift_count')
        employee_wknd_shift_count[e.id] = model.new_int_var(0, len(weekends), f'{e.id}_wknd_shift_count')

        for day in range(1, num_days + 1):
            decision_vars[e.id][day] = model.new_bool_var(f'empl_{e.id}_on_{day}')
            cur_date = datetime.date(schedule_period.year, schedule_period.month, day).strftime("%Y-%m-%d") # a date string in 'YYY-MM-DD' format, same as the e.unavailable_dates list elements

            if cur_date in e.unavailable_dates:
                model.add(decision_vars[e.id][day] == 0)
                    
        model.add(employee_shift_count[e.id] == sum(decision_vars[e.id][day] for day in range(1, num_days + 1)))
        model.add(employee_wknd_shift_count[e.id] == sum(decision_vars[e.id][day] for day in weekends))

        if shift_interval >= 2:
            for interval_start in range(1, num_days - shift_interval + 2):
                interval_end = interval_start + shift_interval - 1

                violation = model.new_bool_var(f'interval_violation_for_{e.id}_from_{interval_start}_to_{interval_end}')
                
                model.add(sum(decision_vars[e.id][day] for day in range(interval_start, interval_end + 1)) >= 2).only_enforce_if(violation)
                model.add(sum(decision_vars[e.id][day] for day in range(interval_start, interval_end + 1)) < 2).only_enforce_if(violation.Not())

                shift_interval_violations.append(violation)
        
    for day in range(1, num_days + 1):
        model.add(sum(decision_vars[e.id][day] for e in employees) == 2)
    
    model.add_min_equality(min_shifts, employee_shift_count.values())
    model.add_max_equality(max_shifts, employee_shift_count.values())
    model.add_min_equality(min_wknd_shifts, employee_wknd_shift_count.values())
    model.add_max_equality(max_wknd_shifts, employee_wknd_shift_count.values())
    
    obj_1 = max_shifts - min_shifts
    obj_2 = max_wknd_shifts - min_wknd_shifts
    obj_3 = sum(shift_interval_violations)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 5
    
    model.minimize(obj_1)
    solver.solve(model)
    model.add(obj_1 == int(solver.objective_value))

    model.minimize(obj_2)
    solver.solve(model)
    model.add(obj_2 == int(solver.objective_value))

    if shift_interval_violations:
        model.minimize(obj_3)
        solver.solve(model)
    
    status = solver.Solve(model)

    if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        return None
    
    per_day_schedule = []
    per_employee_schedule = []

    employee_day_map = {}
    for day in range(1, num_days + 1):
        iso_date = datetime.date(schedule_period.year, schedule_period.month, day).strftime('%Y-%m-%d')
        day_data = {'iso_date': iso_date, 'daily_employees': []}

        for e in employees:
            if solver.value(decision_vars[e.id][day]) == 1:
                day_data['daily_employees'].append({'id': e.id, 'name': str(e)})
                
                if e.id not in employee_day_map:
                    employee_day_map[e.id] = []
                
                employee_day_map[e.id].append(iso_date)
        
        per_day_schedule.append(day_data)

    for e in employees:
        per_employee_schedule.append({'id': e.id, 'name': str(e), 'days': employee_day_map[e.id]})

    interval_violations = []
    for i in range(len(shift_interval_violations)):
        if solver.value(shift_interval_violations[i]) == 1:
            interval_violations.append(shift_interval_violations[i].Name())        
    
    schedule_stats = {
        'max_shifts_min_shifts': solver.value(obj_1),
        'max_wknd_shifts_min_wknd_shifts': solver.value(obj_2),
        'interval_violations': interval_violations,
        'theoretical_intervals': solver.value(shift_interval),
    }
            
    return per_day_schedule, per_employee_schedule, schedule_stats
