from flask import Flask, render_template, url_for, redirect, request, session, flash, get_flashed_messages
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "Pembroke"
app.permanent_session_lifetime = timedelta(days=1)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
with app.app_context():
        db.create_all()
        print("Database tables created")

class users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def __repr__(self):
        return '<users {}>'.format(self.fullname)
    
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = users.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['fullname'] = user.fullname  # Store fullname in session
            session['email'] = user.email  # Store email in session
            session.permanent = True
            return redirect(url_for("home"))
        else:
            return render_template("login.html", message="Invalid email or password.")
    return render_template("login.html")


@app.route("/user")
def user():
    if 'user_id' in session:
        user = session['user_id']
        return redirect(url_for(""))
    else:
        return redirect(url_for("login"))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        password = request.form['password']

        user = users.query.filter_by(email=email).first()
        if user:
            return 'Email already exists.'

        new_user = users(fullname=fullname, email=email)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id
        session['fullname'] = fullname  # Store fullname in session
        session['email'] = email  # Store email in session
        return redirect(url_for('home'))

    return render_template('signup.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/teams')
def teams():
    return render_template("teams.html")

@app.route('/events')
def events():
    return render_template("events.html")

@app.route('/myProfile')
def myProfile():
    if 'user_id' not in session:
        flash("You must be logged in to view your profile.", "error")
        return redirect(url_for('login'))
    
    fullname = session.get('fullname')
    email = session.get('email')
    return render_template("myProfile.html", fullname=fullname, email=email)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Database tables created")
    app.run(debug=True)


