from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello():
    return '<h1>Check your files for mentions of People/Companies on the US Sanctions List</h1>'