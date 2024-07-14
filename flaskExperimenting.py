from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
	return "<p>Hi, World! <a href='hello'>9</a></p>"

@app.route("/hello")
def hello():
	return "<p>Who are you, what are you doing in my house?!</p>"