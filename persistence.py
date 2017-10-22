import csv
import random
from itertools import groupby, tee
from collections import defaultdict
from datetime import datetime, timedelta
from faker import Faker

from wage import parse_time, daily_pay

fake = Faker()


def reset_data(db):
    with db:
        db.execute("DELETE FROM work_session")
        db.execute("DELETE FROM employee")


def prefill_data(db):
    reset_data(db)

    employees = [(str(i), fake.name()) for i in range(1, random.randint(5, 15))]
    sessions = []

    start_date, end_date = datetime(2014, 3, 1), datetime(2014, 5, 1)

    for person_id, name in employees:
        session_start = start_date + timedelta(hours=random.randint(0, 72))
        while session_start < end_date:
            session_end = session_start + timedelta(hours=random.randint(1, 12))

            print(session_start, session_end, session_end > session_start)

            sessions.append((person_id, session_start, session_end))

            session_start = session_end + timedelta(hours=random.randint(1, 72))

    random.shuffle(sessions)

    with db:
        db.executemany("INSERT INTO employee (employee_id, name) VALUES (?, ?)", employees)
        db.executemany("INSERT INTO work_session (employee_id, start_time, end_time) VALUES (?, ?, ?)", sessions)


def import_from_csv(csv_file):
    pass


def get_reports(db):
    reports = []
    for row in db.execute("SELECT DISTINCT strftime('%Y %m', start_time) FROM work_session"):
        year, month = row[0].split(" ")
        reports.append((int(year), int(month)))

    print(reports)

    return reports

def get_report(year, month):
    pay = defaultdict(lambda: {
        "month_total": 0, 
        "base_total": 0, 
        "evening_total": 0, 
        "overtime_total": 0
    })

    with open("HourList{}{}.csv".format(year, str(month).zfill(2)), "r") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        person_id = lambda rec: rec["Person ID"]
        
        for key, group in groupby(sorted(reader, key=person_id), person_id):
            group, g_temp = tee(group)
            pay[key]["name"] = next(g_temp)["Person Name"]
            sessions = [parse_time(rec["Date"], rec["Start"], rec["End"]) for rec in group]
            pay[key]["sessions"] = sessions

            for start_time, end_time in sessions:
                day_pay, base_pay, evening_pay, overtime_pay = daily_pay(start_time, end_time)
                pay[key]["month_total"] += day_pay
                pay[key]["base_total"] += base_pay
                pay[key]["evening_total"] += evening_pay
                pay[key]["overtime_total"] += overtime_pay
    
    return pay