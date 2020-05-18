
from flask import Flask
from src.FlaskHealthAppBackend import FlaskHealthAppBackend

app = Flask(__name__)

FlaskHealthAppBackend.register(app, route_base='/')

if __name__ == '__main__':
    app.run()