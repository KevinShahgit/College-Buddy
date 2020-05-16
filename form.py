from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional


class SignupForm(FlaskForm):
    fname = StringField('First Name',
                       validators=[DataRequired()])
    lname = StringField('Last Name', validators = [DataRequired()])
    roll = IntegerField('Roll Number', validators = [DataRequired()])
    year = SelectField('Year of Study', choices = [("SY", "S.Y."), ('text', 'Plain Text')])
    branch = SelectField('Branch', choices = [("Comps", "Computer Engineering"), ('text', 'Plain Text')])
    division = SelectField('Division', choices = [("A"), ("B"), ('text', 'Plain Text')])
    id = StringField('Email(A code will be sent to this email for verification)',
                        validators=[Length(min = 6),
                                    Email(message='Enter a valid email.'),
                                    DataRequired()])
    password = PasswordField('Password',
                             validators=[DataRequired(),
                                         Length(min=6, message='Select a stronger password. Minimum length of password should be 6')])
    confirm = PasswordField('Confirm Your Password',
                            validators=[DataRequired(),
                                        EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    id = StringField('Email', validators=[DataRequired(),
                                             Email(message='Enter a valid email.')])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')
    
class CodeForm(FlaskForm):
    code = IntegerField('Code(that was sent to your email', validators = [DataRequired()])