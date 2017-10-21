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


def overtime_pay(total_hours, stops, rates):
    payments = (hours * rate for hours, rate in zip(overtime(total_hours, stops), rates))
    return sum(payments)


def total_pay(start_datetime, end_datetime):
    delta = end_datetime - start_datetime
    total_hours = delta.total_seconds() / 3600
    base_pay = total_hours * BASE_RATE
    evening_pay = evening_hours(start_datetime, end_datetime) * EVENING_EXTRA_RATE

    return base_pay + \
        evening_pay + \
        overtime_pay(total_hours, OVERTIME_STOPS, OVERTIME_RATES)


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
