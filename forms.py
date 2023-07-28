from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class LoginForm(FlaskForm):
    username = StringField("Login:")
    password = PasswordField("Pass:", validators=[Length(min=4, max=100)])
    remember = BooleanField("Remember", default=False)
    submit = SubmitField("Log in")


class RegisterForm(FlaskForm):
    username = StringField("Login:")
    key = StringField("Key:")
    password = PasswordField("Pass:", validators=[Length(min=4, max=100)])
    submit = SubmitField("Register")