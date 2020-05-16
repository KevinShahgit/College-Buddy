from app import app, login, stu, teach, misc
from app.users import User
from flask_login import current_user, login_user, logout_user
from app.form import SignupForm, LoginForm, CodeForm
from flask import url_for, redirect, flash, render_template, get_flashed_messages, request
import math, random, requests, json, jsonify, bcrypt

def generateOTP() :   # 4 digit OTP
    digits = "0123456789"
    OTP = "" 
    for i in range(4) : 
        OTP += digits[math.floor(random.random() * 10)] 
    return int(float(OTP))

@app.route('/', methods = ["GET", "POST"])
@app.route('/login', methods = ["GET", "POST"])
def logview():
    if current_user.is_authenticated:
        if current_user.type == 'S':
            return redirect(url_for('stuhome'))
        else:
            return redirect(url_for('profhome'))
    l1 = LoginForm()
    if l1.validate_on_submit():
        user = teach.find_one({"_id": l1.id.data})
        if user is not None and l1.password.data == user.get("pword"):
            t = User(id = user.get("_id"), password = user.get("pword"), type = "T")
            login_user(t)
            return redirect(url_for('profhome'))
        elif user is not None:
            flash('Invalid username/password combination.')
        else:
            user = stu.find_one({"_id": l1.id.data})
            if user is not None and l1.password.data == user.get("pword"):
                t = User(id = user.get("_id"), password = user.get("pword"), type = "S")
                login_user(t)
                return redirect(url_for('stuhome'))
            else:
                flash('Invalid username/password combination.')
    return render_template('login.html',
                            form = l1,
                            title = 'Log in.',
                            template ='login-page',
                            body = "Log in with your User account.")
                            

@app.route('/signup', methods = ["GET", "POST"])
def sign():
    s1 = SignupForm()
    if s1.validate_on_submit():
        existing_user = teach.find_one({"_id": s1.id.data})
        if existing_user is None:
            existing_user = stu.find_one({"_id": s1.id.data})
            if existing_user is None:
                c = generateOTP()
                requests.post("https://us-central1-dbcheck-ff691.cloudfunctions.net/sendMail", data=json.dumps({"check":1,"email": s1.id.data,"code": c}),headers={'Content-Type': 'application/json'})
                temp = {
                    '_id' : s1.id.data,
                    'name' : s1.fname.data + " " + s1.lname.data,
                    'pword' : s1.password.data,
                    'roll' : s1.roll.data,
                    'year' : s1.year.data,
                    'branch' : s1.branch.data,
                    'division' : s1.division.data,
                    'AOA' : [],
                    'PSOT' : [],
                    'RDBMS' : [],
                    'TACD' : [],
                    'OSTPL' : [],
                    "code" : c
                }
                misc.insert_one(temp)
                return redirect("http://localhost:5000/verify/" + s1.id.data)
            flash('A user already exists with that email address.')
        flash('A user already exists with that email address.')
    return render_template('signup.html',
                           title = 'Create an Account.',
                           form = s1,
                           template = 'signup-page',
                           body = "Sign up for an user account.")
                           
@app.route('/verify/<s>', methods=["GET", "POST"])
def verify(s):
    s2  = CodeForm()
    temp = misc.find_one({"_id" : s})
    if s2.validate_on_submit():
        print(temp.get("code"))
        if temp.get("code") == s2.code.data:
            temp.pop("code")
            stu.insert_one(temp)
            misc.delete_one({'_id': s})
            user = User(id = temp.get("_id"), password = temp.get("pword"), type = 'S')
            login_user(user)
            return redirect(url_for("stuhome"))
        flash("Incorrect code entered")
    return render_template('check.html', title = 'Email Verification', form = s2, template = 'signup-page', body = 'Verify your email.')    



@app.route('/stuhome', methods = ["GET", "POST"])
def stuhome():
    
    return render_template('attendance.html')
  
@login.user_loader
def load_user(id):
    a = teach.find_one({"_id" : id})
    if a is not None:
        return User(id = a.get("_id"), password = a.get("pword"), type = "T")
    else:
        a = stu.find_one({"_id" : id})
        return User(id = a.get("_id"), password = a.get("pword"), type = "S")