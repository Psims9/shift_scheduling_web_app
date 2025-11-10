import datetime
import calendar
from ortools.sat.python import cp_model
import math

def create_schedule(schedule_period: datetime.date, employee_ids: list[int]):
    model = cp_model.CpModel()

    num_days = calendar.monthrange(schedule_period.year, schedule_period.month)[1]

    decision_vars = {id: {day: model.new_bool_var(f'employee_{id}_on_day_{day}') for day in range(1, num_days + 1)} for id in employee_ids}

    for day in range(1, num_days + 1):
        model.add(sum(decision_vars[id][day] for id in employee_ids) == 2)

    # employee_shift_count = {id: int model variable for employee's montlhy shift count}
    employee_shift_count = {id: model.new_int_var(0, num_days, f'{id}_shift_count') for id in employee_ids}

    for id in employee_ids:
        model.add(employee_shift_count[id] == sum(decision_vars[id][day] for day in range(1, num_days + 1)))
    
    min_shifts = model.new_int_var(0, num_days, 'min_shifts')
    model.add_min_equality(min_shifts, employee_shift_count.values())

    max_shifts = model.new_int_var(0, num_days, 'max_shifts')
    model.add_max_equality(max_shifts, employee_shift_count.values())

    shift_interval = math.floor(num_days/math.ceil((num_days*2)/len(employee_ids)))

    shift_interval_violations = []

    for id in employee_ids:
        # number of interval start days = num_days - shift_interval + 1 (we stop when the end day equals the end of the month).
        for interval_start in range(1, num_days - shift_interval + 2):
            # the interval includes the starting day, so the interval end is = interval_start + interval - 1
            interval_end = interval_start + shift_interval - 1

            # violation = 1 if the employee works more than 2 shifts in the given interval, 0 otherwise
            violation = model.new_bool_var(f'too_many_shifts_for_{id}_from_{interval_start}_to_{interval_end}')

            # force violation = 1 if employee works more than 2 shifts in the current interval
            model.add(sum(decision_vars[id][day] for day in range(interval_start, interval_end + 1)) >= 2).only_enforce_if(violation)

            # force violation = 0 if employee does not work more than 2 shifts in the current interval
            model.add(sum(decision_vars[id][day] for day in range(interval_start, interval_end + 1)) < 2).only_enforce_if(violation.Not())

            shift_interval_violations.append(violation)
        
    obj_func = max_shifts - min_shifts + sum(shift_interval_violations)
    model.minimize(obj_func)
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        return None
    
    solution = {}
    for day in range(1, num_days + 1):
        assigned_employees = tuple(id for id in employee_ids if solver.Value(decision_vars[id][day]) == 1)
        solution[datetime.date(schedule_period.year, schedule_period.month, day)] = assigned_employees
    
    return solution
