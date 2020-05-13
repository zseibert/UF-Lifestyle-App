import re

from flask import Flask, render_template, request, jsonify, make_response
from backend import authentication as Auth
app = Flask(__name__)

auth = Auth.AuthDatabase()

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def auth_user():
    response = ""
    token = ""
    email = request.form['email']
    password = request.form['password']
    try:
        token = auth.authenticate_user(email, password)
    except Exception as e:
        return jsonify({"success": False})
    response = make_response(render_template('home.html'))
    response.set_cookie('token', token)
    return response

@app.route('/create_account')
def create_account():
    return render_template('create_account.html')

@app.route('/create_account', methods=['POST'])
def create_account_post():
    account = ""
    response = ""
    email = request.form['email']
    password = request.form['password']

    if len(password) < 7:
        jsonify({"success" : False, "short" : True})
    try:
        account = auth.create_new_user(email, password)
    except Exception as e:
        return jsonify({"success" : False, "short" : False})
    response = make_response(render_template('home.html'))
    response.set_cookie('token', account)
    return response

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/entries')
def entries():
    token = request.cookies.get('token')
    if token is None:
        #placeholder
        return 'Need a token'
    return render_template('entries.html')

@app.route('/entries/submit_daily_entry', methods=['POST'])
def submit_daily_entry():
    date = request.form['date']
    clss = request.form['class']
    study = request.form['study']
    social = request.form['social']
    exercise = request.form['exercise']
    leisure = request.form['leisure']
    sleep = request.form['sleep']
    other = request.form['other']
    stress = request.form['stress']

    data = {"class" : clss, 
            "study" : study,
            "social" : social,
            "exercise" : exercise,
            "leisure" : leisure,
            "sleep" : sleep,
            "other" : other,
            "stress" : stress}
    token = request.cookies.get('token')
    if token is None:
        #placeholder
        return "Please log in"
    auth.add_daily_entry(token, date, data)
    return jsonify({"success": True})

@app.route('/entries/get_daily_entry', methods=['POST'])
def get_daily_entry():
    datepicker = request.form['datepicker']
    date = datepicker.replace(r'/', ":")
    date = date[:-2]
    if(len(date) < 3):
        return jsonify({"success": False})
    token = request.cookies.get('token')
    if token is None:
        #placeholder
        return "Please log in"
    daily_entry = auth.get_daily_entry(token, date)
    if daily_entry is None:
        # nothing was entered for this date
        data = {"class" : 0, 
            "study" : 0,
            "social" : 0,
            "exercise" : 0,
            "leisure" : 0,
            "sleep" : 0,
            "other" : 0,
            "stress" : 0}
        return data
    ret = {}
    for key, value in daily_entry.items():
        ret.update({key : value})
    ret.update({"date" : date})
    return ret

@app.route('/reports/get_report_data', methods=['POST'])
def get_report_data():
    token = request.cookies.get('token')
    if token is None:
        #placeholder
        return 'Need a token'
    start = request.form['startDate']
    end = request.form['endDate']
    ret = auth.get_report_data(token, start, end)
    return ret

@app.route('/reports')
def load_reports():
    token = request.cookies.get('token')
    if token is None:
        #placeholder
        return 'Need a token'
    return render_template('reports.html')
    
@app.route('/goals')
def set_goals():
    return render_template('goals.html')

if __name__ == '__main__':
	app.run(debug=True)