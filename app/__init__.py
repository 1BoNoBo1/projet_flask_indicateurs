from flask import Flask

app = Flask(__name__, template_folder='../templates')
app = Flask(__name__, static_folder='../static', template_folder='../templates')
app.config.from_object('config')

app.secret_key = app.config['SECRET_KEY']

from app import routes