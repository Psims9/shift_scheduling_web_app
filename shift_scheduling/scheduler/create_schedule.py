import datetime
import calendar
from ortools.sat.python import cp_model
import math

def create_schedule(schedule_period: datetime.date, employee_data: dict):
    model = cp_model.CpModel()

    num_days = calendar.monthrange(schedule_period.year, schedule_period.month)[1]
    shift_interval = math.floor(num_days/math.ceil((num_days*2)/len(employee_data)))
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

    for id in employee_data:
        decision_vars[id] = {}
        employee_shift_count[id] = model.new_int_var(0, num_days, f'{id}_shift_count')
        employee_wknd_shift_count[id] = model.new_int_var(0, len(weekends), f'{id}_wknd_shift_count')

        for day in range(1, num_days + 1):
            decision_vars[id][day] = model.new_bool_var(f'empl_{id}_on_{day}')

            if datetime.date(schedule_period.year, schedule_period.month, day).strftime("%Y-%m-%d") in employee_data[id]['unavailable_dates']:
                model.add(decision_vars[id][day] == 0)
            
            if day != 1:
                model.add(decision_vars[id][day - 1] + decision_vars[id][day] <= 1)
        
        model.add(employee_shift_count[id] == sum(decision_vars[id][day] for day in range(1, num_days + 1)))
        model.add(employee_wknd_shift_count[id] == sum(decision_vars[id][day] for day in weekends))

        for interval_start in range(1, num_days - shift_interval + 2):
            interval_end = interval_start + shift_interval - 1

            violation = model.new_bool_var(f'interval_violation_for_{id}_from_{interval_start}_to_{interval_end}')
            
            model.add(sum(decision_vars[id][day] for day in range(interval_start, interval_end + 1)) >= 2).only_enforce_if(violation)
            model.add(sum(decision_vars[id][day] for day in range(interval_start, interval_end + 1)) < 2).only_enforce_if(violation.Not())

            shift_interval_violations.append(violation)
        
    for day in range(1, num_days + 1):
        model.add(sum(decision_vars[id][day] for id in employee_data) == 2)
    
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

    model.minimize(obj_3)
    solver.solve(model)
    
    status = solver.Solve(model)

    if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        return None
    
    schedule = {}
    employee_stats = {}

    for day in range(1, num_days + 1):
        employees_by_names = [employee_data[e]['full_name'] + f' (id: {e})' for e in employee_data if solver.value(decision_vars[e][day]) == 1]

        date = datetime.date(schedule_period.year, schedule_period.month, day)
        month = f'{date.strftime('%a')} - {date.day}/{date.month}/{date.year}'
        
        schedule[month] = tuple(employees_by_names)
        
        for employee_name in employees_by_names:
            if employee_name not in employee_stats:
                employee_stats[employee_name] = {
                    'days': [],
                    'weekends': 0
                }

            employee_stats[employee_name]['days'].append(month)

            if day in weekends:
                employee_stats[employee_name]['weekends'] += 1
    
    interval_violations = []
    for i in range(len(shift_interval_violations)):
        if solver.value(shift_interval_violations[i]) == 1:
            interval_violations.append(shift_interval_violations[i].Name())

    
    schedule_stats = {
        'max_shifts_min_shifts': solver.value(obj_1),
        'max_wknd_shifts_min_wknd_shifts': solver.value(obj_2),
        'obj_function_value': solver.ObjectiveValue(),
        'status': solver.StatusName(),
        'theoretical_intervals': solver.value(shift_interval),
        'interval_violations': interval_violations

    }
            
    return schedule, schedule_stats, employee_stats
