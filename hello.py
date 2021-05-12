from flask import Flask
from flask import request

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/newtable')
def query_example():
    # if key doesn't exist, returns None
    language = request.args.get('table')

    return '''<h1>The table name is: {}</h1>'''.format(language)