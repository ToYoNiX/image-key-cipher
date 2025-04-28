from flask import Flask, render_template

app = Flask(__name__)

confusion = []
diffusion = []

@app.route("/", methods = ['GET', 'POST'])
def index():
    return render_template("home.html")

@app.route("/encrypt", methods = ['GET', 'POST'])
def encrypt():
    ...

@app.route("/decrypt", methods = ['GET', 'POST'])
def decrypt():
    ...