#-*- encoding: utf-8

import os
import json
import sqlite3
import requests

from flask import Flask, render_template, request, session
from flask import redirect, url_for
from lxml import etree


app = Flask(__name__)
app.secret_key = os.urandom(24)

insert_sql = "insert into course_store values('%s', '%s')"
insert_comment_sql = "insert into teacher_comment values('%s', '%s', '%s')"
select_sql = "select * from course_store where course_uid = '%s'"
select_comment_sql = "select * from teacher_comment where teacher_name='%s' and teacher_class='%s'"
delete_sql = "delete from course_store where course_uid = '%s'"

session_pool = {}
public_session = requests.Session()


weekday = [u"時間", u"一", u"二", u"三", u"四", u"五", u"六", u"日"]
class_session = [u"M", u"第一節", u"第二節", u"第三節", u"第四節", u"A", u"第五節", u"第六節", u"第七節",\
                u"第八節", u"B", u"第十一節", u"第十二節", u"第十三節", u"第十四節"]

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

files = open('teacher', 'r')
content = files.read()
content = json.loads(content)

@app.errorhandler(500)
def page_not_found(error):
    return redirect(url_for('simulation'))

@app.route("/", methods=['POST', 'GET'])
def index():
    return redirect(url_for('simulation'))

@app.route("/Teacher")
def teacher():
    return render_template('teacher_commit.html')

@app.route("/addComment", methods=['POST'])
def addComment():
    if request.method == 'POST':
        courseName = request.form['courseName'].split(",")
        comment = request.form['data']
        connects(insert_comment_sql % (courseName[1], courseName[0], comment))
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
                result = connects(select_comment_sql % (i['courseTeacher'], i['courseName']))
                if lens(result) != 0:
                    result = connects(select_comment_sql % (i['courseTeacher'], i['courseName']))
                    for j in result:
                        print(j)
                        courseName, courseClass, comment = j
                        return_data[i['courseTeacher']]['comment'].append(comment)
                        print(return_data[i['courseTeacher']]['comment'])
        message['data'] = return_data
        return json.dumps(message)
    else:
        return "ERROR"            

@app.route("/Simulation")
def simulation():
    return render_template('simulate.html', class_session=class_session, weekday=weekday)


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
        s = public_session
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
        row = [format % (class_session[count / 7] + times[count / 7], class_session[count / 7])] if count % 7 == 0 else row
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
            result = connects(select_sql % session['uid'])
            for row in result:
                uid, table = row
                msg['table'] = table
        else:
            msg['success'] = False

        return json.dumps(msg)


@app.route("/store", methods=['POST'])
def store():
    if request.method == 'POST':
        data = request.form['data']
        if check(session['uid']):
            connects( delete_sql % session['uid'])
        if data != "":
            if data.find("script") != -1: 
                return json.dumps({"success": False})
            connects( insert_sql % (session['uid'], data))
        return json.dumps({"success": True})
    return "Error"

def check(uid):
    sql = select_sql % uid
    result = connects(sql)
    return not lens(result) == 0

def connects(sql):
    db = sqlite3.connect("./Course_DB")
    cursor = db.cursor()
    if 'select' in sql:
        cursor.execute(sql)
        return cursor
    else:
        try:
            with db:
                db.execute(sql)
                return True
        except Exception as e:
            return False
    db.close()

def lens(result):
    count = 0
    for i in result:
        count += 1
    return count

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=35189)