from flask import Flask, render_template
import json
import csv
from itertools import groupby, tee
from collections import defaultdict

from wage import parse_time, daily_pay
from persistence import get_reports

app = Flask(__name__)


@app.route('/')
def list_reports():
    return render_template("list_reports.html", reports=get_reports())

@app.route("/report/<report_name>")
def view_report(report_name):
    pay = defaultdict(lambda: {
        "month_total": 0, 
        "base_total": 0, 
        "evening_total": 0, 
        "overtime_total": 0
    })

    with open(report_name, "r") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        person_id = lambda rec: rec["Person ID"]
        
        for key, group in groupby(sorted(reader, key=person_id), person_id):
            group, g_temp = tee(group)
            pay[key]["name"] = next(g_temp)["Person Name"]
            times = (parse_time(rec["Date"], rec["Start"], rec["End"]) for rec in group)

            for start_time, end_time in times:
                day_pay, base_pay, evening_pay, overtime_pay = daily_pay(start_time, end_time)
                pay[key]["month_total"] += day_pay
                pay[key]["base_total"] += base_pay
                pay[key]["evening_total"] += evening_pay
                pay[key]["overtime_total"] += overtime_pay

    return render_template("view_report.html", 
        report_name=report_name,
        wage=sorted(pay.items(), key=lambda t: t[0]))