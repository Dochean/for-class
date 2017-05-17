from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object('config')
app.config['BOOTSTRAP_SERVE_LOCAL'] = True

bootstrap = Bootstrap(app)
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.session_protection = 'strong'
login_manager.login_view = 'main.login'

from main import main as main_blueprint
app.register_blueprint(main_blueprint)

# @app.route('/')
# def index():
#     return 'hello'

if __name__ == '__main__':
    app.run(debug=True)