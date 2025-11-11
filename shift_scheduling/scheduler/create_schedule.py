import datetime
import calendar
from ortools.sat.python import cp_model
import math
from .types import EmployeeData

def create_schedule(schedule_period: datetime.date, employee_data: list[EmployeeData]):
    model = cp_model.CpModel()

    num_days = calendar.monthrange(schedule_period.year, schedule_period.month)[1]

    decision_vars = {e['id']: {day: model.new_bool_var(f'employee_{e['id']}_on_day_{day}') for day in range(1, num_days + 1)} for e in employee_data}

    for day in range(1, num_days + 1):
        model.add(sum(decision_vars[e['id']][day] for e in employee_data) == 2)
    
    for e in employee_data:
        if e['avail']:
            for date in e['avail']:
                day = datetime.datetime.strptime(date, "%Y-%m-%d").day
                model.add(decision_vars[e['id']][day] == 0)
                
    # employee_shift_count = {id: int model variable for employee's montlhy shift count}
    employee_shift_count = {e['id']: model.new_int_var(0, num_days, f'{e['id']}_shift_count') for e in employee_data}

    for e in employee_data:
        model.add(employee_shift_count[e['id']] == sum(decision_vars[e['id']][day] for day in range(1, num_days + 1)))
    
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

    employee_wknd_shift_count = {e['id']: model.new_int_var(0, len(weekends), f'{e['id']}_wknd_shift_count') for e in employee_data}
    
    for e in employee_data:
        model.add(employee_wknd_shift_count[e['id']] == sum(decision_vars[e['id']][day] for day in weekends))
    
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
            violation = model.new_bool_var(f'too_many_shifts_for_{e['id']}_from_{interval_start}_to_{interval_end}')

            # force violation = 1 if employee works more than 2 shifts in the current interval
            model.add(sum(decision_vars[e['id']][day] for day in range(interval_start, interval_end + 1)) >= 2).only_enforce_if(violation)

            # force violation = 0 if employee does not work more than 2 shifts in the current interval
            model.add(sum(decision_vars[e['id']][day] for day in range(interval_start, interval_end + 1)) < 2).only_enforce_if(violation.Not())

            shift_interval_violations.append(violation)
        
    obj_func = max_shifts - min_shifts + max_wknd_shifts - min_wknd_shifts + sum(shift_interval_violations)
    model.minimize(obj_func)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10
    status = solver.Solve(model)

    if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        return None
    
    schedule = {}
    for day in range(1, num_days + 1):
        assigned_employees = tuple(e['id'] for e in employee_data if solver.value(decision_vars[e['id']][day]) == 1)
        schedule[datetime.date(schedule_period.year, schedule_period.month, day)] = assigned_employees
    
    stats = {
        'max_shifts_employees': [e['id'] for e in employee_data if solver.value(employee_shift_count[e['id']]) == solver.value(max_shifts)],
        'min_shifts_employees': [e['id'] for e in employee_data if solver.value(employee_shift_count[e['id']]) == solver.value(min_shifts)],
        'max_wknd_shifts_employees': [e['id'] for e in employee_data if solver.value(employee_wknd_shift_count[e['id']]) == solver.value(max_wknd_shifts)],
        'min_wknd_shifts_employees': [e['id'] for e in employee_data if solver.value(employee_wknd_shift_count[e['id']]) == solver.value(min_wknd_shifts)],
        'shift_interval_solved': solver.value(shift_interval),
        'solver_status': solver.status_name(status),
        'solve_time': solver.wall_time,
        'max_shifts_solved': solver.value(max_shifts),
        'min_shifts_solved': solver.value(min_shifts), 
    }

    return schedule, stats
