import sqlite3
from flask import Flask, render_template, abort, url_for, g, redirect
from datetime import timedelta


import persistence

app = Flask(__name__)

DATABASE = 'wage.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def list_reports():
    return render_template("list_reports.html", reports=persistence.get_reports(get_db()))


@app.route('/data/reset', methods=["POST"])
def reset_data():
    persistence.reset_data(get_db())
    return redirect(url_for('list_reports'))

@app.route('/data/prefill', methods=["POST"])
def prefill_data():
    persistence.prefill_data(get_db())
    return redirect(url_for('list_reports'))

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

    # normalize to the largest value
    if max_value > 0:
        for day in range(0, 7):
            for hour in range(0, 24):
                matrix[day][hour] /= max_value

    return matrix


@app.route("/report/<int:year>/<int:month>")
def view_report(year, month):
    if (year, month) not in persistence.get_reports(get_db()):
        abort(404)

    pay = persistence.get_report(get_db(), year, month)
    punchcard_matrices = {
        person_id: generate_punchcard_matrix(pay[person_id]["sessions"]) 
            for person_id in pay
    }

    return render_template("view_report.html", 
        report_name="{}/{}".format(year, str(month).zfill(2)),
        year=year,
        month=month,
        wage=sorted(pay.items(), key=lambda t: t[0]),
        wage_json=pay,
        punchcards=punchcard_matrices)