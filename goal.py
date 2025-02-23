from urllib import request
from flask import Flask, render_template, request, redirect, session, url_for
from urllib.parse import quote_plus
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import logging



app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    goal = db.Column(db.Text, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

@app.route("/", methods=['GET', 'POST'])
def signup():

    # if request.method=='GET':
    #     return render_template('login.html')
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        repassword = request.form.get('repassword')

        if password != repassword:
            return "Passwords do not match! Try again."

        existing_user = User.query.filter_by(email=email).first()
        app.logger.info(existing_user)
        if existing_user == True:
            app.logger.info(existing_user)
            #print(f"existing user : {existing_user}")
            #message = "Already have a account?."
            return render_template('login.html')
   

        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return render_template('login.html')
    
    return render_template('register.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # user = User.query.filter_by(email=email, password=password).first()
        return redirect('/dashboard')
        if user:
            session['user_id'] = user.id
            return redirect('/dashboard')
        else:
            return "Invalid credentials. Try again."

    return render_template('login.html')

@app.route("/dashboard",methods=['GET','POST'])
def dashboard():

    if 'user_id' not in session:
       return redirect('login')
    
    user_id = session['user_id']
    goals = Goal.query.filter_by(user_id=user_id).all()
    return render_template('dashboard.html', goals=goals)

@app.route("/add_goal", methods=['GET','POST'])
def add_goal():
    if 'user_id' in session:
        goal_text = request.form.get('goal')
        new_goal = Goal(user_id=session['user_id'], goal=goal_text)
        db.session.add(new_goal)
        db.session.commit()
    return redirect('dashboard')

@app.route("/complete_goal/<int:goal_id>")
def complete_goal(goal_id):
    if 'user_id' in session:
        goal = Goal.query.get(goal_id)
        if goal and goal.user_id == session['user_id']:
            goal.completed = True
            db.session.commit()
    return redirect('dashboard')

@app.route("/delete_goal/<int:goal_id>")
def delete_goal(goal_id):
    if 'user_id' in session:
        goal = Goal.query.get(goal_id)
        if goal and goal.user_id == session['user_id']:
            db.session.delete(goal)
            db.session.commit()
    return redirect('dashboard')

@app.route("/logout")
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
