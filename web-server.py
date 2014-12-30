#-*- encoding: utf-8
from flask import Flask, render_template, request, session
from flask import redirect, url_for
from lxml import etree
import requests
import MySQLdb
import json
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
db = MySQLdb.connect("localhost", "Simulate", "Simulate", "simulate", charset="utf8")
cursor = db.cursor()

insert_sql = "insert into course_store value('%s', '%s')"
insert_comment_sql = "insert into teacher_comment value('%s', '%s', '%s')"
select_sql = "select * from course_store where course_uid = '%s'"
select_comment_sql = "select * from teacher_comment where teacher_name='%s' && teacher_class='%s'"
delete_sql = "delete from course_store where course_uid = '%s'"

session_pool = {}
public_session = requests.session()

week = ["M", "第一節", "第二節", "第三節", "第四節", "A", "第五節", "第六節", "第七節",\
         "第八節", "B", "第十一節", "第十二節", "第十三節", "第十四節"]

times = [
            "<br/>0730<br/>-<br/>0800",
            "<br/>0810<br/>-<br/>0900",
            "<br/>0910<br/>-<br/>1000",
            "<br/>1010<br/>-<br/>1100",
            "<br/>1110<br/>-<br/>1200",
            "",
            "<br/>1330<br/>-<br/>1420",
            "<br/>1430<br/>-<br/>1520",
            "<br/>1530<br/>-<br/>1620",
            "<br/>1630<br/>-<br/>1720",
            "",
            "<br/>1810<br/>-<br/>1900",
            "<br/>1910<br/>-<br/>2000",
            "<br/>2010<br/>-<br/>2100",
            "<br/>2110<br/>-<br/>2200",
        ]

host_url = "http://mss.kuas.edu.tw/api/%s"
login_url = "http://140.127.113.231/kuas/perchk.jsp"
course_url = "http://140.127.113.231/kuas/ag_pro/ag222.jsp"
search_url = "Course/GetCourse"

API_KEY = "5Dcb9a^J5ULIR^e"

files = open('teacher', 'rb')
content = files.read()
content = json.loads(content)

@app.errorhandler(500)
def page_not_found(error):
    return redirect(url_for('index'))

@app.route("/", methods=['POST', 'GET'])
def index():
    return render_template('index.html')

@app.route("/Teacher")
def teacher():
    return render_template('teacher_commit.html')

@app.route("/addComment", methods=['POST'])
def addComment():
    if request.method == 'POST':
        courseName = request.form['courseName'].split(",")
        comment = request.form['data']
        cursor.execute(insert_comment_sql % (courseName[1], courseName[0], comment))
        db.commit()
        return json.dumps({"success": True})

@app.route("/getUnit", methods=['POST'])
def getUnit():
    if request.method == 'POST':
        return_string = u"<option value='%'>所有科系</option>"
        html = "<optgroup label='%s'>"
        for i in content:
            return_string += html % i
            option = "<option value='%s'>%s</option>"
            for j in content[i]:
                return_string += option % (content[i][j], j) 
        return return_string

@app.route("/getTeacherList", methods=['POST'])
def getTeacher():
    if request.method == 'POST':
        message = {
            'success': True
        }
        key = "%"
        for n in xrange(0, len(request.form['keys'])):
            key += request.form['keys'][n:n+1] + "%"
        payload = {
            'apiKey': API_KEY,
            'academicYear': 103,
            'academicSms': 2,
            'courseName': key,
            'degreeId': '14',
        }
        if request.form['unit'] != '%' :
            payload['unitId'] = request.form['unit']
        data = json.loads(public_session.post(host_url % search_url, data=payload).content)['data']
        return_data = {}
        for i in data:
            if not i['courseTeacher'] == " ":
                if not i['courseTeacher'] in return_data:
                    return_data[i['courseTeacher']] = {}
                    return_data[i['courseTeacher']]['open_class'] = []
                    return_data[i['courseTeacher']]['comment'] = []
                    return_data[i['courseTeacher']]['courseName'] = i['courseName']
                return_data[i['courseTeacher']]['open_class'].append(i['className'])
                cursor.execute(select_comment_sql % (i['courseTeacher'], i['courseName']))
                print select_comment_sql % (i['courseTeacher'], i['courseName'])
                result = cursor.fetchall()
                print len(result)
                if len(result) != 0:
                    for j in result:
                        courseName, courseClass, comment = j
                        return_data[i['courseTeacher']]['comment'].append(comment)
        message['data'] = return_data
        return json.dumps(message)
    else:
        return "ERROR"            

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
        types = request.form['type']
        key = "%"
        for n in xrange(0, len(request.form['key'])):
            key += request.form['key'][n:n+1] + "%"
        payload = {
            'apiKey': API_KEY,
            'academicYear': 103,
            'academicSms': 2,
            'courseName': key,
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
            check = ('MA' in d['courseRoom'] or 'MB' in d['courseRoom'] or u'燕巢' in d['className'])
            if types == '1':
                if not check:
                    return_data.append(d);
            elif types == '2':
                if check:
                    return_data.append(d);
            else:
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
    format = "<td width='200' align='center' tags='%s'>%s</td>"
    row = []
    for i in td:
        row = [format % (week[count / 7] + times[count / 7], week[count / 7])] if count % 7 == 0 else row
        content = i.text.replace(' ', '').replace('\n', '').replace('\r', '')
        row.append(format % ('', content))
        count += 1
        if count % 7 == 0:
            grid.append(row)
            row = []
    return json.dumps(grid)

@app.route("/restore", methods=['POST'])
def restore():
    if request.method == 'POST':
        msg = {}
        msg['success'] = True
        if check(session['uid']) :
            cursor.execute(select_sql % session['uid'])
            result = cursor.fetchall()
            uid, table = result[0]
            msg['table'] = table
        else:
            msg['success'] = False

        return json.dumps(msg)


@app.route("/store", methods=['POST'])
def store():
    if request.method == 'POST':
        data = request.form['data']
        if check(session['uid']):
            cursor.execute( delete_sql % session['uid'])
            db.commit()
        if data != "":
            if data.find("script") != -1: 
                return json.dumps({"success": False})
            cursor.execute( insert_sql % (session['uid'], data))
            db.commit()
        return json.dumps({"success": True})
    return "Error"

def check(uid):
    sql = select_sql % uid
    cursor.execute(sql)
    result = cursor.fetchall()
    return not len(result) == 0

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=35189)
