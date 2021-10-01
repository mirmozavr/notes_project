from wtforms import StringField, SubmitField, TextAreaField, BooleanField, PasswordField, SelectField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Email, InputRequired, EqualTo, Length


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField()


class SignUpForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[Email()])
    password = PasswordField("Password",
                             validators=[InputRequired(), EqualTo('password_confirm', message='Passwords must match'),
                                         Length(3)])
    password_confirm = PasswordField("Confirm password", validators=[DataRequired()])
    submit = SubmitField()


class NoteForm(FlaskForm):
    title = StringField("Title", validators=[Length(max=100)])
    content = TextAreaField("Content", validators=[DataRequired()])
    color = SelectField("Color", choices=[("white", "White"), ("red", "Red"), ("blue", "Blue"), ("green", "Green"),
                                          ("yellow", "Yellow"), ("orange", "Orange")])
    save = SubmitField()


class DeleteForm(FlaskForm):
    delete = SubmitField(label="Delete")
