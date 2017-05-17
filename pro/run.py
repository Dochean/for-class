from myapp import app, db
from myapp.main.models import User, Role
import os

def db_handle(db):
    db.drop_all()
    db.create_all()

if __name__ == '__main__':
    db.drop_all()
    db.create_all()
    Role.init_roles()
    User.create_admin()
    app.run(debug=True)
