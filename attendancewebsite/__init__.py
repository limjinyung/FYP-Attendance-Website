import os
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping": True}
app.config['SECRET_KEY'] = '25e01a84c93d97366d83e08cbf23aa2c'
aws_username = os.environ['AWS_USERNAME']
aws_password = os.environ['AWS_PASSWORD']
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://{}:{}@attendance-database.cdnz9bo65s1b.ap-southeast-1.rds.amazonaws.com:5432/postgres'.format(aws_username, aws_password)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_message_category = 'info'
login_manager.refresh_view = "auth.reauth"
socketio = SocketIO(app)


@socketio.on('disconnect')
def disconnect_user():
    return redirect(url_for('logout'))

from attendancewebsite import routes