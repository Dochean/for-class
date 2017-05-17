import os

SECRET_KEY = '88df2819253c3aa679ab5cb49947e5'

basedir = os.path.abspath(os.path.dirname(__file__))

DATABASE_USER = 'qianyi'
DATABASE_KEY = 'cccc'
DATABASE_HOST = 'localhost'
DATABASE_DATABASE = 'yo'

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + DATABASE_USER + ':'  + DATABASE_KEY + '@' + DATABASE_HOST + '/' + DATABASE_DATABASE
SQLALCHEMY_COMMIT_ON_TEARDOWN = True
SQLALCHEMY_TRACK_MODIFICATIONS = True

ADMIN = {
    'acc_num': '41455026',
    'password': 'cccc',
    'name': 'Chii',
}