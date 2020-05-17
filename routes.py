from app import app, login, stu, teach, misc
from app.users import User
from flask_login import current_user, login_user, logout_user, login_required
from app.form import SignupForm, LoginForm, CodeForm
from flask import url_for, redirect, flash, render_template, get_flashed_messages, request
import math, random, requests, json, jsonify, datetime, bson.objectid

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
            login_user(t, duration=datetime.timedelta(hours=1))
            return redirect(url_for('profhome'))
        elif user is not None:
            flash('Invalid username/password combination.')
        else:
            user = stu.find_one({"_id": l1.id.data})
            if user is not None and l1.password.data == user.get("pword"):
                t = User(id = user.get("_id"), password = user.get("pword"), type = "S")
                login_user(t, duration=datetime.timedelta(hours=1))
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
                    'email' : s1.id.data,
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
                x = misc.insert_one(temp)
                return redirect("http://localhost:5000/verify/" + str(x.inserted_id))
            # flash('A user already exists with that email address')
        flash('A user already exists with that email address')
    return render_template('signup.html',
                           title = 'Create an Account.',
                           form = s1,
                           template = 'signup-page',
                           body = "Sign up for an user account.")
                           
@app.route('/verify/<s>', methods=["GET", "POST"])
def verify(s):
    s2  = CodeForm()
    temp = misc.find_one({"_id" : bson.objectid.ObjectId(s)})
    if s2.validate_on_submit():
        if temp.get("code") == s2.code.data:
            temp.pop("code")
            x = temp.pop("email")
            temp["_id"] = x
            stu.insert_one(temp)
            misc.delete_one({'_id': bson.objectid.ObjectId(s)})
            user = User(id = temp.get("_id"), password = temp.get("pword"), type = 'S')
            login_user(user, duration=datetime.timedelta(hours=1))
            return redirect(url_for("stuhome"))
        flash("Incorrect code entered")
    return render_template('check.html', title = 'Email Verification', form = s2, template = 'signup-page', body = 'Verify your email.')    



@app.route('/stuhome', methods = ["GET", "POST"])
@login_required
def stuhome():
    if current_user.type == 'T':
        return redirect(url_for('profhome'))
    i = stu.find_one({"_id": current_user.id})
    j = misc.find_one({"_id": i.get("division")})
    #[subject, attended, missed, total, percentage]
    l = []
    for k in j.items():
        if(k[0] == "_id"):
            continue
        l1 = []
        l1.append(k[0])
        z = i.get(k[0])
        l1.append(z.count('1'))
        l1.append(z.count('0'))
        l1.append(int(k[1]))
        if(l1[-1] == 0):
            l1.append('0%')
        else:
            l1.append(str(round((l1[1] / l1[-1]) * 100, 2)) + "%")
        l.append(l1)
        print(l)
    return render_template('attendance.html', data = l)
    
@app.route('/profhome', methods = ["GET", "POST"])
@login_required
def profhome():
    if current_user.type == "S":
        return redirect(url_for("stuhome"))
    return render_template('prof.html')
    
@app.route('/feedback', methods = ["GET", "POST"])
@login_required
def feedback():
    return render_template('feedback.html')
    
   
@app.route("/timetable", methods = ["GET", "POST"])
@login_required
def timetable():
    if current_user.type == 'T':
        return redirect(url_for('profhome'))
    temp = stu.find_one({"_id" : current_user.id})
    branch = temp.get("branch")
    division = temp.get("division")
    return render_template('time-table.html', d = division, b = branch)
    
@app.route('/stuatt', methods = ["GET", "POST"])
@login_required
def attend():
    pass

@app.route('/profatt', methods = ["GET", "POST"]) 
@login_required
def tatt():
    pass
    

@login.user_loader
def load_user(id):
    a = teach.find_one({"_id" : id})
    if a is not None:
        return User(id = a.get("_id"), password = a.get("pword"), type = "T")
    else:
        a = stu.find_one({"_id" : id})
        return User(id = a.get("_id"), password = a.get("pword"), type = "S")
        
@app.route('/logout', methods = ["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("logview"))