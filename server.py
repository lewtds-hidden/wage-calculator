from flask import Flask, render_template, abort

from persistence import get_reports, get_report

app = Flask(__name__)

@app.route('/')
def list_reports():
    return render_template("list_reports.html", reports=get_reports())

def upload_data():
    pass

@app.route("/report/<int:year>/<int:month>")
def view_report(year, month):
    if (year, month) not in get_reports():
        abort(404)

    pay = get_report(year, month)

    return render_template("view_report.html", 
        report_name="{}/{}".format(year, month),
        wage=sorted(pay.items(), key=lambda t: t[0]),
        wage_json=pay)