import csv
import random
from itertools import groupby, tee
from collections import defaultdict
from datetime import datetime, timedelta
from faker import Faker

from wage import parse_time, daily_pay
from util import split_iter

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
            sessions.append((person_id, session_start, session_end))
            session_start = session_end + timedelta(hours=random.randint(1, 72))

    random.shuffle(sessions)

    with db:
        db.executemany("INSERT INTO employee (employee_id, name) VALUES (?, ?)", employees)
        db.executemany("INSERT INTO work_session (employee_id, start_time, end_time) VALUES (?, ?, ?)", sessions)


def import_from_csv(db, csv_file):
    reader = csv.DictReader(csv_file, delimiter=",")
    employees = defaultdict(dict)
    sessions = []

    with db:
        for row in reader:
            pid = row["Person ID"]
            employees[pid]["name"] = row["Person Name"]
            start_time, end_time = parse_time(row["Date"], row["Start"], row["End"])
            sessions.append((pid, start_time, end_time))
        
        for employee_id, employee in employees.items():
            has_employee = db.execute(
                    "SELECT 1 FROM employee WHERE employee_id = ?", 
                    (employee_id,)).fetchone()

            if not has_employee:
                db.execute(
                    "INSERT INTO employee (employee_id, name) VALUES (?, ?)", 
                    (employee_id, employee["name"]))

        db.executemany(
            "INSERT INTO work_session (employee_id, start_time, end_time) VALUES (?, ?, ?)",
            sessions)


def get_reports(db):
    reports = []
    for row in db.execute("SELECT DISTINCT strftime('%Y %m', start_time) FROM work_session"):
        year, month = row[0].split(" ")
        reports.append((int(year), int(month)))

    return reports

def get_report(db, year, month):
    pay = defaultdict(lambda: {
        "month_total": 0, 
        "base_total": 0, 
        "evening_total": 0, 
        "overtime_total": 0
    })

    # this query will create rows of this format:
    # 8|Gregory Francis|2014-03-01 10:00:00,2014-03-03 11:00:00,2014-03-05 14:00|2014...
    # 9|Pamela Wells|2014-03-01 09:00:00,2014-03-04 01:00:00,2014-03-06 13:00:00|2014...
    query = """
    SELECT employee_id, name, group_concat(start_time) AS start_times, group_concat(end_time) AS end_times 
        FROM employee NATURAL JOIN work_session
        WHERE strftime("%Y %m", start_time) = ?
        GROUP BY employee_id
    """

    padded_month = str(month).zfill(2)

    for row in db.execute(query, ("{} {}".format(year, padded_month),)):
        key = row["employee_id"]
        pay[key]["name"] = row["name"]
        # 2014-03-11 23:00:00
        parse_func = lambda timestr: datetime.strptime(timestr, "%Y-%m-%d %H:%M:%S")
        start_datetimes = map(parse_func, split_iter(row["start_times"], r"[^,]+"))
        end_datetimes = map(parse_func, split_iter(row["end_times"], r"[^,]+"))

        sessions = list(zip(start_datetimes, end_datetimes))
        pay[key]["sessions"] = sessions
        for start_time, end_time in sessions:
            day_pay, base_pay, evening_pay, overtime_pay = daily_pay(start_time, end_time)
            pay[key]["month_total"] += day_pay
            pay[key]["base_total"] += base_pay
            pay[key]["evening_total"] += evening_pay
            pay[key]["overtime_total"] += overtime_pay

    return pay