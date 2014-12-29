#-*- encoding: utf-8
from flask import Flask, render_template, request, session
from flask import redirect, url_for
from lxml import etree
import requests
import json
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

session_pool = {}

week = ["M", "第一節", "第二節", "第三節", "第四節", "A", "第五節", "第六節", "第七節",\
         "第八節", "B", "第十一節", "第十二節", "第十三節", "第十四節"]

host_url = "http://mss.kuas.edu.tw/api/%s"
login_url = "http://140.127.113.231/kuas/perchk.jsp"
course_url = "http://140.127.113.231/kuas/ag_pro/ag222.jsp"
search_url = "Course/GetCourse"

API_KEY = "5Dcb9a^J5ULIR^e"

@app.route("/", methods=['POST', 'GET'])
def index():
    return render_template('index.html')

@app.route("/Simulation")
def simulation():
    if not 'uid' in session:
        return redirect(url_for('index'))
    return render_template('simulate.html')

@app.route("/SearchResult", methods=['POST'])
def search():
    if request.method == 'POST':
        message = {
            'success': True
        }
        payload = {
            'apiKey': API_KEY,
            'academicYear': 103,
            'academicSms': 2,
            'courseName': '%' + request.form['key'] + '%',
            'degreeId': '14',
        }
        if request.form['unit'] != '%' :
            payload['unitId'] = request.form['unit']
        s = session_pool[session['uid']]
        data = json.loads(s.post(host_url % search_url, data=payload).content)['data']
        return_data = []
        for i in data:
            d = {}
            courseTime = i['courseTime'].replace("(", ",").replace(")", ",")
            d['className'] = i['className']
            d['courseName'] = i['courseName']
            d['courseTeacher'] = i['courseTeacher']
            d['Time'] = i['courseTime']
            d['courseRoom'] = i['courseRoom']
            d['courseTime'] = courseTime
            return_data.append(d);
        message['data'] = return_data
        return json.dumps(message)
    else:
        return "ERROR"

@app.route("/check_login", methods=['POST'])
def login():
    if request.method == 'POST':
        message = {}
        message['success'] = False
        username = request.form['username']
        password = request.form['password']
        if len(username) != 10:
            message['message'] = "帳號跟你一樣短不好哦"
            return json.dumps(message)
        login_status = login(username, password)
        if login_status:
            session['uid'] = username
            message['success'] = True
            message['redirect_url'] = '/Simulation'
            return json.dumps(message)
        else:
            message['message'] = "登入失敗\n\r帳號或密碼有錯誤"
            return json.dumps(message)

def login(username, password):
    if not username in session_pool:
        session_pool[username] = requests.session()
    s = session_pool[username]
    payload = {
        'uid': username,
        'pwd': password
    }
    resp = s.post(login_url, data=payload).content
    return 'f_index.html' in resp

@app.route("/getCourse", methods=['GET'])
def getCourse():
    payload = {
        "yms":"103,2",
        "spath":"ag_pro/ag222.jsp?",
        "arg01":"103",
        "arg02":"2"
    }
    s = session_pool[session['uid']]
    resp = etree.HTML(s.post("http://140.127.113.231/kuas/ag_pro/ag222.jsp", data=payload).content)
    table = resp.xpath('//table')
    td = table[1].xpath('//td[@bgcolor="#FFFcee"]')
    grid = []
    count = 0
    format = "<td width='200' align='center'>%s</td>"
    row = []
    for i in td:
        row = [format % week[count / 7]] if count % 7 == 0 else row
        content = i.text.replace(' ', '').replace('\n', '').replace('\r', '')
        row.append(format % content)
        count += 1
        if count % 7 == 0:
            grid.append(row)
            row = []
    return json.dumps(grid)


if __name__ == '__main__':
    app.run(host='localhost', debug=True, port=35189)
