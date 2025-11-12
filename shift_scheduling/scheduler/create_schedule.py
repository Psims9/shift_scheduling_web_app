import datetime
import calendar
from ortools.sat.python import cp_model
import math

def create_schedule(schedule_period: datetime.date, employee_data: dict):
    model = cp_model.CpModel()

    num_days = calendar.monthrange(schedule_period.year, schedule_period.month)[1]

    decision_vars = {e: {day: model.new_bool_var(f'employee_{e}_on_day_{day}') for day in range(1, num_days + 1)} for e in employee_data}

    for day in range(1, num_days + 1):
        model.add(sum(decision_vars[e][day] for e in employee_data) == 2)
    
    for e in employee_data:
        if employee_data[e]['unavailable_dates']:
            for date in employee_data[e]['unavailable_dates']:
                day = datetime.datetime.strptime(date, "%Y-%m-%d").day
                model.add(decision_vars[e][day] == 0)
                
    # employee_shift_count = {id: int model variable for employee's montlhy shift count}
    employee_shift_count = {e: model.new_int_var(0, num_days, f'{e}_shift_count') for e in employee_data}

    for e in employee_data:
        model.add(employee_shift_count[e] == sum(decision_vars[e][day] for day in range(1, num_days + 1)))
    
    min_shifts = model.new_int_var(0, num_days, 'min_shifts')
    model.add_min_equality(min_shifts, employee_shift_count.values())

    max_shifts = model.new_int_var(0, num_days, 'max_shifts')
    model.add_max_equality(max_shifts, employee_shift_count.values())

    month_cal = calendar.monthcalendar(schedule_period.year, schedule_period.month)
    weekends = []
    for week in month_cal:
        for i, day in enumerate(week):
            if i >= 5 and day != 0:
                weekends.append(day)

    employee_wknd_shift_count = {e: model.new_int_var(0, len(weekends), f'{e}_wknd_shift_count') for e in employee_data}
    
    for e in employee_data:
        model.add(employee_wknd_shift_count[e] == sum(decision_vars[e][day] for day in weekends))
    
    min_wknd_shifts = model.new_int_var(0, len(weekends), 'min_wknd_shifts')
    model.add_min_equality(min_wknd_shifts, employee_wknd_shift_count.values())

    max_wknd_shifts = model.new_int_var(0, len(weekends), 'max_wknd_shifts')
    model.add_max_equality(max_wknd_shifts, employee_wknd_shift_count.values())

    shift_interval = math.floor(num_days/math.ceil((num_days*2)/len(employee_data)))

    shift_interval_violations = []

    for e in employee_data:
        # number of interval start days = num_days - shift_interval + 1 (we stop when the end day equals the end of the month).
        for interval_start in range(1, num_days - shift_interval + 2):
            # the interval includes the starting day, so the interval end is = interval_start + interval - 1
            interval_end = interval_start + shift_interval - 1

            # violation = 1 if the employee works more than 2 shifts in the given interval, 0 otherwise
            violation = model.new_bool_var(f'too_many_shifts_for_{e}_from_{interval_start}_to_{interval_end}')

            # force violation = 1 if employee works more than 2 shifts in the current interval
            model.add(sum(decision_vars[e][day] for day in range(interval_start, interval_end + 1)) >= 2).only_enforce_if(violation)

            # force violation = 0 if employee does not work more than 2 shifts in the current interval
            model.add(sum(decision_vars[e][day] for day in range(interval_start, interval_end + 1)) < 2).only_enforce_if(violation.Not())

            shift_interval_violations.append(violation)
        
    obj_func = max_shifts - min_shifts + max_wknd_shifts - min_wknd_shifts + sum(shift_interval_violations)
    model.minimize(obj_func)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10
    status = solver.Solve(model)

    if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        return None
    
    schedule = {}
    employee_stats = {}   

    for day in range(1, num_days + 1):
        employees_by_names = [employee_data[e]['full_name'] for e in employee_data if solver.value(decision_vars[e][day]) == 1]
        schedule[day] = tuple(employees_by_names)
        
        for employee_name in employees_by_names:
            if employee_name not in employee_stats:
                employee_stats[employee_name] = {
                    'days': [],
                    'weekends': 0
                }

            employee_stats[employee_name]['days'].append(day)

            if day in weekends:
                employee_stats[employee_name]['weekends'] += 1
            
    return schedule, employee_stats
