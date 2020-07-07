#!/usr/bin/python
# coding=utf-8
from flask import Flask,Response,jsonify, render_template ,flash, redirect, url_for, session,logging,request, make_response, request
from flask_mysqldb import MySQL
import pusher

app = Flask(__name__)

pusher_client = pusher.Pusher(
  app_id='',
  key='',
  secret='',
  cluster='us2',
  ssl=True
)

mysql=MySQL(app)
app.config['SECRET_KEY'] = 'secret!'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = ''
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'hackathon'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'


@app.route('/nurse')
def nurseView():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM patients")
    patients = cur.fetchall()
    return render_template('nurse.html',patients=patients)

@app.route('/')
def patient():
    return render_template('patient.html')

@app.route('/getAssistance')
def getAssistance():
    return render_template('assistance.html')

@app.route('/addPatient', methods=['GET', 'POST'])
def addPatient():
    name = request.form['name']
    age = int(request.form['age'])
    roomNumber = request.form['roomNumber']
    conditions = request.form['conditions']

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO patients(name,roomNumber,age,conditions) VALUES(%s,%s,%s,%s)", (name,roomNumber,age,conditions))
    mysql.connection.commit()
    return render_template('nurse.html')

@app.route('/answerQuestion', methods=['GET', 'POST'])
def answerQuestion():
    answer = request.form['answer']
    roomNumber = request.form['roomNumber']

    cur = mysql.connection.cursor()
    cur.execute("SELECT name from patients WHERE roomNumber = %s", (roomNumber,))
    name = cur.fetchone()
    name = str(name)[11:]
    name = name.replace("'","")
    name = name.replace('}',"")

    print(name)
    pusher_client.trigger('responses', 'questionResponse', {'type':'response','answer': answer,'roomNumber':roomNumber,'name':name})
    return render_template('patient.html')


@app.route('/emergency', methods=['GET', 'POST'])
def emergency():
    roomNumber = request.form['roomNumber']
    print(roomNumber)

    cur = mysql.connection.cursor()
    cur.execute("SELECT name from patients WHERE roomNumber = %s", (roomNumber,))
    name = cur.fetchone()
    name = str(name)[11:]
    name = name.replace("'","")
    name = name.replace('}',"")

    pusher_client.trigger('responses', 'questionResponse', {'type':'emergency', 'roomNumber':roomNumber,'name':name})

    return render_template('patient.html')



@app.route('/deletePatient', methods=['GET', 'POST'])
def deletePatient():
    roomNumber = request.form['roomNumber']
    print(roomNumber)

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM patients WHERE roomNumber = %s", (roomNumber,))
    mysql.connection.commit()
    cur.close()

    return render_template('patient.html')



@app.route('/assistance', methods=['GET', 'POST'])
def assistance():
    roomNumber = request.form['roomNumber']
    nurseRequest = request.form['nurseRequest']
    painLevel = request.form['painLevel']
    reasoningText = request.form['reasoningText']
    print(roomNumber)
    print(nurseRequest)
    print(painLevel)
    print(reasoningText)

    cur = mysql.connection.cursor()
    cur.execute("SELECT name from patients WHERE roomNumber = %s", (roomNumber,))
    name = cur.fetchone()
    name = str(name)[11:]
    name = name.replace("'","")
    name = name.replace('}',"")

    pusher_client.trigger('responses', 'questionResponse', {'type':'assistance', 'roomNumber':roomNumber,'name':name,'painLevel':painLevel,"nurseRequest":nurseRequest,"reasoningText":reasoningText})

    return render_template('patient.html')



@app.route('/askQuestion', methods=['GET', 'POST'])
def askQuestion():
    question = request.form['question']
    options = request.form['options']
    roomNumber = request.form['roomNumber']

    print(options)
    print(roomNumber)
    pusher_client.trigger('room' + roomNumber, 'my-event', {'question': question,'options':options})
    return render_template('nurse.html')

#run server
if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(host='0.0.0.0', port=4004, threaded=True,debug='True')
