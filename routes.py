from flask import render_template, request, redirect, url_for, session, Blueprint
from flask_mail import Message
from datetime import datetime, timedelta
import re
from .databases import User, otp  # Assuming models are in the same directory or a subdirectory
from . import db, mail, app 
from werkzeug.security import generate_password_hash
import secrets
import string

auth_bp = Blueprint('auth', __name__)

def generate_otp(length=6):
    alphabet = string.ascii_uppercase + string.digits
    otp = ''.join(secrets.choice(alphabet) for i in range(length))
    return otp

@app.route('/')
def home():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        if user:
            if user.email_verified:
                return render_template('home.html', email=session['email'])
            else:
                return render_template('otp.html', email=session['email'])
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password1']
        password2 = request.form['password2']
        if password != password2:
            return render_template('register.html', error="Passwords do not match", problem='password')
        if User.query.filter_by(email=email).first():
            return render_template('register.html', error="Email already exists", problem='email')
        if not email or not username or not password:
            return render_template('register.html', error="All fields are required", problem='email' if not email else 'username' if not username else 'password')
        if len(username) < 3 or len(username) > 20:
            return render_template('register.html', error="Username must be between 3 and 20 characters", problem='username')
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return render_template('register.html', error="Invalid email format", problem='email')
        if len(password) < 8:
            return render_template('register.html', error="Password must minimum 8 characters long", problem='password')
        if not any(char.isdigit() for char in password):
            return render_template('register.html', error="Password must contain a digit", problem='password')
        if not any(char.isalpha() for char in password):
            return render_template('register.html', error="Password must contain a letter", problem='password')
        if not any(char in "!@#$%^&*()-_+=<>?/|{}[]:;'" for char in password):
            return render_template('register.html', error="Password must contain a special character", problem='password')
        dob_string = request.form['DOB']
        dob_object = None
        if dob_string:
            try:
                dob_object = datetime.strptime(dob_string, '%Y-%m-%d').date()
            except ValueError:
                return render_template('register.html', error="Invalid date format", problem='dob')
        hashed_password = generate_password_hash(password)
        new_user = User(email=email, DOB = dob_object, username=username, password_hash=hashed_password, email_verified=False)
        session['email'] = email
        db.session.add(new_user)
        db.session.commit()
        
        user = User.query.filter_by(email=email).first()
        otp_code = generate_otp()
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        new_otp = otp(user_id=user.id, otp_code=otp_code, sent_at = datetime.utcnow(), expires_at=expires_at)
        db.session.add(new_otp)
        db.session.commit()
        
        subject = 'confirm your email'
        body = f'Your OTP for email confirmatoin is {otp_code}, valid for 10 minutes.'
        
        msg = Message(subject, recipients=[email])
        msg.body = body
        
        try:
            mail.send(msg)
            
        except Exception as e:
            print(e)
            print(f'otp: {otp_code}')
        return redirect(url_for('otp_route'))
        
    return render_template('register.html', error=None, problem = None)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['email'] = user.email
            return redirect(url_for('home'))
        else:
            return "Invalid credentials"
    return render_template('login.html')



@app.route('/otp', methods=['GET', 'POST'])
def otp_route():
    if request.method == 'POST':
        email = session['email']
        user = User.query.filter_by(email=email).first()
        if user:
            otp_class = otp.query.filter_by(user_id=user.id).order_by(otp.expires_at.desc()).first()
            if otp_class and otp_class.is_valid():
                
                otp1 = request.form['otp1']
                otp2 = request.form['otp2']
                otp3 = request.form['otp3'] 
                otp4 = request.form['otp4'] 
                otp5 = request.form['otp5']
                otp6 = request.form['otp6']
                entered_otp = otp1 + otp2 + otp3 + otp4 + otp5 + otp6
                if len(entered_otp) != 6:
                    return render_template('otp.html', error="Invalid OTP", email=email)
                if entered_otp == otp_class.otp_code:
                    user.email_verified = True
                    db.session.delete(otp_class)
                    db.session.commit()
                    return redirect(url_for('home'))
                else:
                    return render_template('otp.html', error="Invalid OTP", email=email)
            else:
                return render_template('otp.html', error="OTP expired", email=email)
                        
    return render_template('otp.html')

@app.route('/resend_otp', methods=['POST'])
def resend_otp():
    email = session['email']
    user = User.query.filter_by(email=email).first()
    if user:
        otp_class = otp.query.filter_by(user_id=user.id).order_by(otp.expires_at.desc()).first()
        if otp_class:
            if otp_class.sent_at > datetime.utcnow() + timedelta(minutes=1):
                return redirect(url_for('otp_route'))
            db.session.delete(otp_class)
            db.session.commit()
            otp_code = generate_otp()
            expires_at = datetime.utcnow() + timedelta(minutes=10)
            new_otp = otp(user_id=user.id, otp_code=otp_code, sent_at=datetime.utcnow(), expires_at=expires_at)
            db.session.add(new_otp)
            db.session.commit()
            
            subject = 'confirm your email'
            body = f'Your OTP for email confirmatoin is {otp_code}, valid for 10 minutes.'
            
            msg = Message(subject, recipients=[email])
            msg.body = body
            
        try:
            mail.send(msg)
        except Exception as e:
            print(e)
            print(f'otp: {otp_code}')
    return redirect(url_for('otp_route'))

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password1']
        password2 = request.form['password2']
        if password != password2:
            return render_template('reset_password.html', error="Passwords do not match", problem='password')
        
        user = User.query.filter_by(email=email).first()
        if user:
            user.update_password(password)
            user.email_verified = False
            db.session.commit()
            otp_code = generate_otp()
            expires_at = datetime.utcnow() + timedelta(minutes=10)
            new_otp = otp(user_id=user.id, otp_code=otp_code, sent_at=datetime.utcnow(), expires_at=expires_at)
            db.session.add(new_otp)
            db.session.commit()
            
            subject = 'Reset your password'
            body = f'Your OTP for password reset is {otp_code}, valid for 10 minutes.'
            
            msg = Message(subject, recipients=[email])
            msg.body = body
            
            try:
                mail.send(msg)
            except Exception as e:
                print(e)
                print(f'otp: {otp_code}')
        return redirect(url_for('otp_route'))
    return render_template('update_password.html')

@app.route('/logout', methods = ['POST'])
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))