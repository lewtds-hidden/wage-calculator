import sqlite3
from io import TextIOWrapper
from flask import Flask, render_template, abort, url_for, g, redirect, request, flash
from datetime import timedelta

import persistence

app = Flask(__name__)

app.config["DATABASE"] = "wage_dev.db"
app.config["SECRET_KEY"] = "lol"
app.config.from_envvar('APPLICATION_SETTINGS_FILE', silent=True)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = sqlite3.connect(app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        g._database = db
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.before_first_request
def setup():
    persistence.do_migration(get_db())


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500

@app.route('/500')
def trigger500():
    abort(500, "hihi")

@app.route('/')
def list_reports():
    return render_template("list_reports.html")


@app.route('/data/reset', methods=["POST"])
def reset_data():
    persistence.reset_data(get_db())
    flash("The database was reset.", "menu/info")
    return redirect(url_for('list_reports'))

@app.route('/data/prefill', methods=["POST"])
def prefill_data():
    start_date, end_date = persistence.prefill_data(get_db())
    time_format = "%d %b %Y"
    flash("Fake data for the period from {} to {} was generated."
            .format(start_date.strftime(time_format), end_date.strftime(time_format)),
        "menu/info")
    return redirect(url_for('list_reports'))

@app.route('/data/import_from_csv', methods=["POST"])
def import_from_csv():
    if 'csv' not in request.files:
        flash("Cannot upload file. Please double check!", "menu/error")
    elif request.files["csv"].filename == "":
        flash("No file selected!", "menu/error")
    else:
        try:
            file = request.files["csv"]
            text_file = TextIOWrapper(file)
            persistence.import_from_csv(get_db(), text_file)
            flash("File {} uploaded successfully!".format(file.filename), "menu/info")
        except persistence.WrongFileFormat:
            flash("Wrong file format. Please double check!", "menu/error")
        except persistence.InconsistentData:
            flash("The data you try to upload is either duplicating existing data or \
                is inconsistent. Please double check!", "menu/error")

    return redirect(url_for('list_reports'))

@app.route('/data/import_HourList201403_csv', methods=["POST"])
def import_from_HourList201403_csv():
    persistence.reset_data(get_db())
    with open("HourList201403.csv", "r") as csv_file:
        persistence.import_from_csv(get_db(), csv_file)

    flash("The example data set from HourList201403.csv was loaded.", "menu/info")
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


@app.context_processor
def menu_data():
    return {
        "menu": {
            "reports": persistence.get_reports(get_db())
        }
    }