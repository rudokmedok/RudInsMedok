from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField
from wtforms.validators import DataRequired, Length, EqualTo
from flask_wtf.file import FileAllowed, MultipleFileField



class RegistrationForm(FlaskForm):
    nickname = StringField('Nickname', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    avatar = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    nickname = StringField('Nickname', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = StringField('Content', validators=[DataRequired()])
    tags = StringField('Tags')
    images = MultipleFileField('Add Images', validators=[FileAllowed(['jpg', 'png'])])
    videos = MultipleFileField('Add Videos', validators=[FileAllowed(['mp4', 'mov'])])
    submit = SubmitField('Post')

class SearchForm(FlaskForm):
    search = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')

class ChangeNicknameForm(FlaskForm):
    nickname = StringField('New Nickname', validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Update Nickname')

class ChangePasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Update Password')

class ChangeAvatarForm(FlaskForm):
    avatar = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update Avatar')

