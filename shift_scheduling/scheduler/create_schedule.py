import datetime
import calendar
from ortools.sat.python import cp_model

def create_schedule(schedule_period: datetime.date, employee_ids: list[int]):
    model = cp_model.CpModel()

    num_days = calendar.monthrange(schedule_period.year, schedule_period.month)[1]

    decision_vars = {id: {day: model.new_bool_var(f'employee_{id}_on_day_{day}') for day in range(1, num_days + 1)} for id in employee_ids}
    