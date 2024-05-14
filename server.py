from flask import Flask, render_template, url_for, send_file, request, redirect
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import psycopg2

admin_password = 'jegan'

def send_email(recipient_email, subject, body):
    sender_email = 'thedummyboss@gmail.com'
    sender_password='vvflxrjbgeaysest'
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587  
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()  
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, recipient_email, msg.as_string())
    server.quit()

def get_projects_html():
    try:
        with psycopg2.connect(
                dbname="transpower",
                user="sirppi",
                password="incorrect",
                host="127.0.0.1",
                port="5432"
            ) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM project")
                return cursor.fetchall()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return "</p>Failed to fetch data </p>"

def query_projects_html(query):
    try:
        with psycopg2.connect(
                dbname="transpower",
                user="sirppi",
                password="incorrect",
                host="127.0.0.1",
                port="5432"
            ) as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT * FROM project WHERE LOWER(name) LIKE '%{query.lower()}%' or LOWER(description) LIKE '%{query.lower()}%'")
                return cursor.fetchall()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return "</p>Failed to fetch data </p>"

def add_project(name, description):
    try:
        with psycopg2.connect(
                dbname="transpower",
                user="sirppi",
                password="incorrect",
                host="127.0.0.1",
                port="5432"
            ) as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"INSERT INTO project VALUES ('{name}', '{description}')")
    except (Exception, psycopg2.DatabaseError) as error:
        pass

def delete_project(name):
    try:
        with psycopg2.connect(
                dbname="transpower",
                user="sirppi",
                password="incorrect",
                host="127.0.0.1",
                port="5432"
            ) as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"DELETE FROM project WHERE name = '{name}'")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        pass

def auth(name, password):
    try:
        with psycopg2.connect(
                dbname="transpower",
                user="sirppi",
                password="incorrect",
                host="127.0.0.1",
                port="5432"
            ) as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT * FROM admin WHERE name = '{name}' and password = '{password}'")
                return len(cursor.fetchall()) != 0
    except Exception as error:
        print(error)
        return False

app = Flask('Transpower')
@app.route('/')
def index():
    return render_template('index.html', projects=get_projects_html())

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/<path:path>')
def file(path):
    return send_file(f'/home/woxtoxfox/transpower/{path}')

@app.route('/sendmail', methods=['POST'])
def sendmail():
    send_email('softwaresirppi@gmail.com', f'Customer: {request.form["name"]}, {request.form["phone"]}, {request.form["email"]}', request.form['message'])
    return redirect('/')

@app.route('/add_project_api', methods=['POST'])
def add_project_api():
    username = request.form['username']
    password = request.form['password']
    if auth(username, password):
        add_project(request.form['name'], request.form['description'])
    return redirect(f'/projects?username={username}&password={password}')

@app.route('/delete_project_api', methods=['GET'])
def delete_project_api():
    username = request.args.get('username')
    password = request.args.get('password')
    if auth(username, password):
        delete_project(request.args.get('name'))
    return redirect(f'/projects?username={username}&password={password}')

@app.route('/edit_project_api', methods=['GET'])
def edit_project_api():
    username = request.args.get('username')
    password = request.args.get('password')
    if auth(username, password):
        delete_project(request.args.get('name'))
        add_project(request.args.get('new_name'), request.args.get('new_description'))
    return redirect(f'/projects?username={username}&password={password}')

@app.route('/projects', methods=['POST', 'GET'])
def projects_page():
    if request.method == 'GET':
        username = request.args.get('username')
        password = request.args.get('password')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
    if auth(username, password):
        return render_template('projects.html', title='projects', projects=get_projects_html(), username=username, password=password)
    return 'ACCESS DENIED'

@app.route('/query_projects', methods=['POST', 'GET'])
def query_page():
    if request.method == 'GET':
        query = request.args.get('query')
    elif request.method == 'POST':
        query = request.form['query']
    return render_template('query.html', title=f'Showing results for "{query}"', projects=query_projects_html(query))

app.run()
