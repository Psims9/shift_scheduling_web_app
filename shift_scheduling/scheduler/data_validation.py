from datetime import date, timedelta
from collections import defaultdict


# First check if there are enough employees to satisfy the shift constraints,
# which in this case means that for every day there must be at least 2 available
# employees, even the same 2.

# First check if there are at least 2 employees in the DB.
# Then go through each day and check that the number of available
# employees is at least 2.

def data_validation(employees, schedule_period):

    employees_num = employees.count()

    # Test 1: are there enough employees in the db to begin with
    if employees_num < 2:
        return {'code': 1, 'msg': 'not enough employees in the DB'}
    
    # compute first day of next month
    if schedule_period.month == 12:
        next_month = date(schedule_period.year + 1, 1, 1)
    
    else:
        next_month = date(schedule_period.year, schedule_period.month + 1, 1)
    
    # Pre-build a counter for unavailable employees per date in the month
    unavailable_count = defaultdict(int) # date -> count
    
    start = schedule_period
    end = next_month

    unavailable_dates_lists = employees.values_list('unavailable_dates', flat=True)

    for unavailable_dates_list in unavailable_dates_lists:
        if not unavailable_dates_list:
            continue
    
        dataset = set() # a set of date objects within the schedule period e is unavailable
        
        for iso_date in unavailable_dates_list:
            dt = date.fromisoformat(iso_date)
            if start <= dt < end:
                dataset.add(dt)
            
        for dt in dataset:
            unavailable_count[dt] += 1
    
    current = start

    while current < end:
        unavailable = unavailable_count.get(current, 0)
        if employees_num - unavailable < 2:
            return {'code': 2, 'msg': f'not enough available employees on {current.isoformat()}'}
        
        current += timedelta(days=1)

    return {'code': 0, 'msg': 'tests_succesfull'}