#coding: utf-8
from flask_wtf import Form
from .models import User, Room, Segment
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, SelectField, TextField
from wtforms.validators import Required, Length, Regexp
from wtforms import ValidationError
from datetime import date

class LoginForm(Form):
    acc_num = StringField('Account Number', validators=[Required(), Length(1, 64)])
    password = PasswordField('Password', validators=[Required()])
    #date = DateField('date', format='%Y-%m-%d')
    remember_me = BooleanField('keep me logged in')
    submit = SubmitField('Log In')

class CreateAccountForm(Form):
    acc_num = StringField('Account Number', validators=[Required(), Length(1, 64)])
    name = StringField('Account Name', validators=[Required()])
    password = StringField('Password', validators=[Required()])
    select = SelectField('Role', choices=[('User', 'User'), ('Moderator', 'Moderator')], validators=[Required()])
    submit = SubmitField('Create')

    def validate_acc_num(self, field):
        if User.query.filter_by(acc_num=field.data).first():
            raise ValidationError('Account Number already created.')

class EditAccountForm(Form):
    acc_num = StringField('Account Number', validators=[Required(), Length(1, 64)])
    name = StringField('Name', validators=[Required()])
    password = StringField('Password', validators=[Required()])
    select = SelectField('Role', choices=[('User', 'User'), ('Moderator', 'Moderator')], validators=[Required()])
    submit = SubmitField('Edit')

class CreateRoomForm(Form):
    name = StringField('Room Name', validators=[Required(), Length(1, 64)])
    floor = StringField('Floor Number', validators=[Required(), Regexp('^[1-9][0-9]*$', 0, 'only Number')])
    num = StringField('Capacity', validators=[Required(), Regexp('^[1-9][0-9]*$', 0, 'only Number')])
    select = SelectField('Type', choices=[('1', 'Class Room'), ('2', 'Meeting Room'), ('3', 'Lecture Hall')], validators=[Required()])
    submit = SubmitField('Create')

    def validate_name(self, field):
        if Room.query.filter_by(name=field.data).first():
            raise ValidationError('Room name already created.')

class EditRoomForm(Form):
    name = StringField('Room Name', validators=[Required(), Length(1, 64)])
    floor = StringField('Floor Number', validators=[Required()])
    num = StringField('Capacity')
    select = SelectField('Type', choices=[('1', 'Class Room'), ('2', 'Meeting Room'), ('3', 'Lecture Hall')], validators=[Required()])
    submit = SubmitField('Edit')

class CreateUseForm(Form):
    room = StringField('Room Name', validators=[Required()])
    select = SelectField('Segment', choices=[(str(k), v) for k, v in Segment.items()])
    date = DateField('date')
    reason = TextField('Reason')
    submit = SubmitField('Create')

    def validate_date(self, field):
        if field.data <= date.today():
            raise ValidationError('You should choose a date after today.')

class CreateRequestForm(Form):
    room = StringField('Room Name', validators=[Required()])
    select = SelectField('Segment', choices=[(str(k), v) for k, v in Segment.items()])
    date = DateField('date')
    reason = TextField('Reason')
    submit = SubmitField('Create')

    def validate_date(self, field):
        if field.data <= date.today():
            raise ValidationError('You should choose a date after today.')