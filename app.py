from flask import Flask
app = Flask(__name__)

from flask import render_template

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/signup')
def signup():
    return render_template("signup.html")

@app.route('/teams')
def teams():
    return render_template("teams.html")

@app.route('/events')
def events():
    return render_template("events.html")

@app.route('/myProfile')
def myProfile():
    return render_template("myProfile.html")

