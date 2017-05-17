#coding: utf-8
from flask_login import UserMixin, AnonymousUserMixin
from .. import db, login_manager, app
from datetime import datetime

class Permission:
    REQUEST = 0x01
    APPROVE = 0x02
    CLASS_OP = 0x04
    USE_OP = 0x08
    ACCOUNT_OP = 0x10
    ROOT = 0xff

Type = {
    1: 'Class Room',
    2: 'Meeting Room',
    3: 'Lecture Hall',
}

Segment = {
    1: '08:00 - 09:35',
    2: '09:55 - 11:30',
    3: '13:30 - 15:05',
    4: '15:20 - 16:55',
    5: '17:10 - 18:45',
    6: '19:30 - 21:05',
}

class A_R:
    roles = ['User', 'Moderator', 'Admin']

class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    actor = db.Column(db.String(128), unique=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role')

    @staticmethod
    def init_roles():
        roles = {
            'User': Permission.REQUEST,
            'Moderator': Permission.APPROVE,
            'Admin': 0xff,
        }
        for (k, v) in roles.items():
            role = Role.query.filter_by(actor=k).first()
            if role is None:
                role = Role(actor=k)
            role.permissions = v
            db.session.add(role)
        db.session.commit()

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False
    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    acc_num = db.Column(db.String(64), unique=True, index=True)
    name = db.Column(db.String(64))
    password = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    requests = db.relationship('Request', backref='user')

    @staticmethod
    def create_admin():
        role = Role.query.filter_by(actor='Admin').first()
        user = User(acc_num=app.config['ADMIN']['acc_num'],
                    name=app.config['ADMIN']['name'],
                    password=app.config['ADMIN']['password'],
                    role=role)
        db.session.add(user)
        db.session.commit()

    def can(self, permissions):
        return self.role is not None and (self.role.permissions & permissions) == permissions

    def is_root(self):
        return self.can(Permission.ROOT)

class Room(db.Model):
    __tablename__ = 'rooms'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, index=True)
    floor = db.Column(db.Integer)
    tpe = db.Column(db.Integer)
    num = db.Column(db.Integer)
    requests = db.relationship('Request', backref='room')
    uses = db.relationship('Use', backref='room')

State = {
    0: 'under approval',
    1: 'succeeded',
    2: 'failed',
}

class Request(db.Model):
    __tablename__ = 'requests'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'))
    seg = db.Column(db.Integer)
    date = db.Column(db.Date())
    state = db.Column(db.Integer, default=0)
    reason = db.Column(db.Text())
    stamp = db.Column(db.DateTime(), default=datetime.now)
    approval_id = db.Column(db.Integer)

class Use(db.Model):
    __tablename__ = 'uses'

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'))
    seg = db.Column(db.Integer)
    date = db.Column(db.Date())
    reason = db.Column(db.Text())