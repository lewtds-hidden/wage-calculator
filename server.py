from flask import Flask, render_template, abort
from datetime import timedelta 

from persistence import get_reports, get_report

app = Flask(__name__)

@app.route('/')
def list_reports():
    return render_template("list_reports.html", reports=get_reports())

def upload_data():
    pass


def generate_punchcard_matrix(work_sessions):
    matrix = [[0 for hour in range(0, 24)] for day in range(0, 7)]
    max_value = 0
    for start, end in work_sessions:
        day = start.weekday()
        while start < end:
            matrix[day][start.hour] += 1
            if matrix[day][start.hour] > max_value:
                max_value = matrix[day][start.hour]
            
            start += timedelta(hours=1)


    print(max_value)
    # normalize to the largest value
    if max_value > 0:
        for day in range(0, 7):
            for hour in range(0, 24):
                matrix[day][hour] /= max_value

    return matrix


@app.route("/report/<int:year>/<int:month>")
def view_report(year, month):
    if (year, month) not in get_reports():
        abort(404)

    pay = get_report(year, month)
    punchcard_matrices = {person_id: generate_punchcard_matrix(pay[person_id]["sessions"]) for person_id in pay}

    return render_template("view_report.html", 
        report_name="{}/{}".format(year, str(month).zfill(2)),
        year=year,
        month=month,
        wage=sorted(pay.items(), key=lambda t: t[0]),
        wage_json=pay,
        punchcards=punchcard_matrices)