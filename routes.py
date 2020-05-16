from app import app, login, stu, teach, misc
from app.users import User
from flask_login import current_user, login_user, logout_user
from app.form import SignupForm, LoginForm
from flask import url_for, redirect, flash, render_template, get_flashed_messages, request

@app.route('/', methods = ["GET", "POST"])
@app.route('/login', methods = ["GET", "POST"])
def logview():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    l1 = LoginForm()
    if l1.validate_on_submit():
        user = teach.find_one({"_id": l1.id.data})
        if user is not None and l1.password.data == user.get("password"):
            t = User(id = user.get("_id"), password = user.get("password"), type = "T")
            login_user(user)
            return redirect(url_for('profhome'))
        elif user is not None:
            flash('Invalid username/password combination.')
        else:
            user = stu.find_one({"_id": l1.id.data})
            if user is not None and l1.password.data == user.get("password"):
                t = User(id = user.get("_id"), password = user.get("password"), type = "S")
                login_user(user)
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
    s2  = CodeForm()
    if s1.validate_on_submit():
        existing_user = user = teach.find_one({"_id": s1.id.data})
        if existing_user is None:
            existing_user = stu.find_one({"_id": s1.id.data})
            if existing_user is None:
                if 
                user = User(id = s1.id.data,
                            password = s1.password.data,
                            type = 'S')
                login_user(user)
                return redirect(url_for(''))
            flash('A user already exists with that email address.')
        flash('A user already exists with that email address.')
    return render_template('signup.html',
                           title = 'Create an Account.',
                           form = s1,
                           template = 'signup-page',
                           body = "Sign up for an user account.")
    
    
@login.user_loader
def load_user(id):
    a = teach.find_one({"_id" : id})
    if a is not None:
        return User(id = a.get("_id"), password = a.get("password"), type = "T")
    else:
        a = stu.find_one({"_id" : id})
        return User(id = a.get("_id"), password = a.get("password"), type = "S")