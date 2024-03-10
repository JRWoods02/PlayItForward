from flask import Flask, render_template, url_for, redirect, request, session, flash, get_flashed_messages
from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from flask_migrate import Migrate


app = Flask(__name__)
app.secret_key = "Pembroke"
app.permanent_session_lifetime = timedelta(days=1)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), unique=False, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def __repr__(self):
        return '<users {}>'.format(self.fullname)
    
class Post(db.Model):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)  # New column for category
    user_id = Column(Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=db.func.current_timestamp())

    user = db.relationship('users', backref=db.backref('posts', lazy=True))

# End of database and start of routing functions
    
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
            return redirect(url_for("myProfile"))
        else:
            return render_template('login.html', invalid=True)
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
    errors = {}  # Initialize an empty dictionary for collecting potential errors
    
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        password = request.form.get('password')

        # Basic validation example
        if not fullname:
            errors['fullname'] = 'Full name is required.'
        if not email:
            errors['email'] = 'Email is required.'
        if not password:
            errors['password'] = 'Password is required.'

        user = users.query.filter_by(email=email).first()
        if user:
            errors['email'] = 'Email already exists.'

        if errors:
            # If there are any errors, re-render the signup page with error messages
            return render_template('signup.html', errors=errors)
        else:
            # If validation passes, proceed to create a new user
            new_user = users(fullname=fullname, email=email)
            new_user.set_password(password)

            db.session.add(new_user)
            db.session.commit()

            # You might want to log the user in immediately after signing up
            # For example, by setting session variables as below
            session['user_id'] = new_user.id
            session['fullname'] = fullname
            session['email'] = email

            return redirect(url_for('home'))

    # For a GET request, or if there were errors with the form submission
    return render_template('signup.html', errors={})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/teams')
def teams():
    team_posts = Post.query.filter_by(category='team').order_by(Post.created_at.desc()).all()
    return render_template("teams.html", team_posts=team_posts)

@app.route('/events')
def events():
    event_posts = Post.query.filter_by(category='event').order_by(Post.created_at.desc()).all()
    return render_template("events.html", event_posts=event_posts)

@app.route('/myProfile')
def myProfile():
    if 'user_id' not in session:
        flash("You must be logged in to view your profile.", "error")
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    user_posts = Post.query.filter_by(user_id=user_id).order_by(Post.created_at.desc()).all()

    fullname = session.get('fullname')
    email = session.get('email')
    return render_template("myProfile.html", fullname=fullname, email=email, posts=user_posts)

@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')  # Get the category from the form
        current_user_id = session.get('user_id')  # Ensure you have logic to handle user identification

        if not category in ['team', 'event']:
            flash('Invalid category selected.', 'error')
            return redirect(url_for('create_post'))

        # Create and save the new post
        new_post = Post(title=title, description=description, category=category, user_id=current_user_id)
        db.session.add(new_post)
        db.session.commit()

        flash('Post created successfully!', 'success')
        return redirect(url_for('myProfile'))
    
    # For a GET request, render the form
    return render_template('create_post.html')

@app.route('/user_profile/<int:user_id>')
def user_profile(user_id):
    user = users.query.get_or_404(user_id)
    # Assuming you have a template named user_profile.html to display the user's profile
    return render_template('user_profile.html', user=user)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Database tables created")
    app.run(debug=True)