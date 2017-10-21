import csv
from itertools import groupby
from datetime import time, datetime, timedelta
from collections import defaultdict

BASE_RATE = 3.75
EVENING_EXTRA_RATE = 1.15
OVERTIME_STOPS = [8, 2, 2]
OVERTIME_RATES = [p * BASE_RATE for p in [0, 0.25, 0.5, 1]]

def parse_time(date, start_time, end_time):
    start_time = datetime.strptime(date + " " + start_time, "%d.%m.%Y %H:%M")
    end_time = datetime.strptime(date + " " + end_time, "%d.%m.%Y %H:%M")

    if end_time < start_time:
        # crosses day boundary
        end_time += timedelta(days=1)
        
    return (start_time, end_time)


assert parse_time("6.3.2014","5:00","10:00") == \
    (datetime(2014, 3, 6, 5, 0), datetime(2014, 3, 6, 10, 0))
assert parse_time("6.3.2014","15:00","2:00") == \
    (datetime(2014, 3, 6, 15, 0), datetime(2014, 3, 7, 2, 0))
assert parse_time("6.3.2014","15:00","0:0") == \
    (datetime(2014, 3, 6, 15, 0), datetime(2014, 3, 7, 0, 0))
assert parse_time("06.03.2014","15:00","17:00") == \
    (datetime(2014, 3, 6, 15, 0), datetime(2014, 3, 6, 17, 0))
assert parse_time("06.03.2014","15:00","17:12") == \
    (datetime(2014, 3, 6, 15, 0), datetime(2014, 3, 6, 17, 12))


def evening_hours(start_datetime, end_datetime):
    # do a shift backward by 18 hours so that start and end time stay 
    # always in one day, to ease calculation.
    s = start_datetime - timedelta(hours=18)
    e = end_datetime - timedelta(hours=18)

    if e.day != start_datetime.day:
        e = e.replace(day=start_datetime.day, hour=0, minute=0)
    elif e.hour > 12 or (e.hour == 12 and e.minute != 0):
        e = e.replace(hour=12, minute=0)

    if s.day != start_datetime.day:
        s = s.replace(day=start_datetime.day, hour=0, minute=0)

    return (e - s).total_seconds() / 3600

# not evening
assert evening_hours(datetime(2014, 3, 6, 7, 0), \
                     datetime(2014, 3, 6, 8, 0)) == 0
assert evening_hours(datetime(2014, 3, 6, 7, 0), \
                     datetime(2014, 3, 6, 18, 0)) == 0
assert evening_hours(datetime(2014, 3, 6, 6, 0), \
                     datetime(2014, 3, 6, 18, 0)) == 0
# evening
assert evening_hours(datetime(2014, 3, 6, 18, 0), \
                     datetime(2014, 3, 6, 19, 0)) == 1
# crossing day boundary
assert evening_hours(datetime(2014, 3, 6, 23, 0), \
                     datetime(2014, 3, 7, 1, 0)) == 2
assert evening_hours(datetime(2014, 3, 6, 18, 0), \
                     datetime(2014, 3, 7, 1, 0)) == 7
assert evening_hours(datetime(2014, 3, 6, 18, 0), \
                     datetime(2014, 3, 7, 6, 0)) == 12
# not whole hours
assert evening_hours(datetime(2014, 3, 6, 18, 0), \
                     datetime(2014, 3, 7, 1, 15)) == 7.25
assert evening_hours(datetime(2014, 3, 6, 18, 15), \
                     datetime(2014, 3, 7, 1, 15)) == 7
# passing 6:00
assert evening_hours(datetime(2014, 3, 6, 18, 0), \
                     datetime(2014, 3, 7, 6, 15)) == 12
# before 18:00
assert evening_hours(datetime(2014, 3, 6, 15, 0), \
                     datetime(2014, 3, 7, 6, 0)) == 12

def overtime(total_hours, stops):
    for stop in stops:
        if total_hours <= 0:
            yield 0
        elif total_hours > stop:
            yield stop
        else:
            yield total_hours
        
        total_hours -= stop

    yield total_hours if total_hours > 0 else 0
        
assert list(overtime(0, [8, 2, 2])) == [0, 0, 0, 0]
assert list(overtime(6, [8, 2, 2])) == [6, 0, 0, 0]
assert list(overtime(8, [8, 2, 2])) == [8, 0, 0, 0]
assert list(overtime(9, [8, 2, 2])) == [8, 1, 0, 0]
assert list(overtime(10, [8, 2, 2])) == [8, 2, 0, 0]
assert list(overtime(11, [8, 2, 2])) == [8, 2, 1, 0]
assert list(overtime(12, [8, 2, 2])) == [8, 2, 2, 0]
assert list(overtime(17, [8, 2, 2])) == [8, 2, 2, 5]


def overtime_pay(total_hours, stops, rates):
    payments = (hours * rate for hours, rate in zip(overtime(total_hours, stops), rates))
    return sum(payments)


assert overtime_pay(8, OVERTIME_STOPS, OVERTIME_RATES) == 0
assert overtime_pay(9, OVERTIME_STOPS, OVERTIME_RATES) == 0.9375
assert overtime_pay(10, OVERTIME_STOPS, OVERTIME_RATES) == 1.875
assert overtime_pay(11, OVERTIME_STOPS, OVERTIME_RATES) == 3.75
assert overtime_pay(12, OVERTIME_STOPS, OVERTIME_RATES) == 5.625
assert overtime_pay(13, OVERTIME_STOPS, OVERTIME_RATES) == 9.375


def total_pay(start_datetime, end_datetime):
    delta = end_datetime - start_datetime
    total_hours = delta.total_seconds() / 3600
    base_pay = total_hours * BASE_RATE
    evening_pay = evening_hours(start_datetime, end_datetime) * EVENING_EXTRA_RATE

    return base_pay + \
        evening_pay + \
        overtime_pay(total_hours, OVERTIME_STOPS, OVERTIME_RATES)

assert total_pay(datetime(2014, 3, 6, 7, 0), 
                 datetime(2014, 3, 6, 10, 0)) == 11.25

# night shift
assert total_pay(datetime(2014, 3, 6, 18, 0), 
                 datetime(2014, 3, 6, 19, 0)) == 4.9


# pay = {}
with open("HourList201403.csv", "r") as csvfile:
    reader = csv.DictReader(csvfile, delimiter=",")

    # for rec in reader:
    #     start_time, end_time = parse_time(rec["Date"], rec["Start"], rec["End"])
    #     if rec['Person ID'] not in pay:
    #         pay[rec['Person ID']] = {
    #             "name": rec["Person Name"],
    #             "monthly_pay": 0
    #         }

    #     pay[rec['Person ID']]["monthly_pay"] += total_pay(start_time, end_time)

    # print (pay)

    person_id = lambda rec: rec["Person ID"]

    for k, g in groupby(sorted(reader, key=person_id), person_id):
        times = (parse_time(rec["Date"], rec["Start"], rec["End"]) for rec in g)
        month_total = sum(map(lambda args: total_pay(*args), times))

        print(k, month_total)

