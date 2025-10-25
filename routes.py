from email import errors
from flask import render_template, request, redirect, url_for, session, Blueprint
from flask_mail import Message
from time import time
from datetime import date, timedelta, datetime
from datetime import datetime
import re
from databases import User, otp  # Assuming models are in the same directory or a subdirectory
from extensions import db, mail  # Import from extensions
from werkzeug.security import generate_password_hash
import secrets
import string

auth_bp = Blueprint('auth', __name__)

def send_otp(email):
    user = User.query.filter_by(email=email).first()
    otp_code = generate_otp()
    new_otp = otp(user_id=user.id, expires_at=datetime.now()+timedelta(minutes=10), otp_code=otp_code) # type: ignore
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

def generate_otp(length=6):
    alphabet = string.ascii_uppercase + string.digits
    otp = ''.join(secrets.choice(alphabet) for i in range(length))
    return otp

@auth_bp.route('/')
def home():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        if user:
            if user.email_verified:
                return render_template('home.html', email=session['email'])
            else:
                return render_template('otp.html', email=session['email'])
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        #checking inputs
        email = request.form['email']
        username = request.form['username']
        password = request.form['password1']
        password2 = request.form['password2']
        errors = {}
        if password != password2:
            errors['password'] = "Passwords do not match"
        if User.query.filter_by(email=email).first():
            errors['email'] = "Email already exists"
        if not email or not username or not password:
            if not email:
                errors['email'] = "Email is required"
            if not username:
                errors['username'] = "Username is required"
            if not password:
                errors['password'] = "Password is required"
            if not password2:
                errors['password'] = "Password confirmation is required"
        if len(username) < 3 or len(username) > 20:
            errors['username'] = "Username must be between 3 and 20 characters"
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            errors['email'] = "Invalid email format"
        if len(password) < 8:
            errors['password'] = "Password must minimum 8 characters long"
        if not any(char.isdigit() for char in password):
            errors['password'] = "Password must contain a digit"
        if not any(char.isalpha() for char in password):
            errors['password'] = "Password must contain a letter"
        if not any(char in "!@#$%^&*()-_+=<>?/|{}[]:;'" for char in password):
            errors['password'] = "Password must contain a special character"
        if errors:
            return render_template('register.html', errors=errors)
        
        #if all inputs are valid, create user
        
        dob_string = request.form['DOB']
        dob_object = None
        if dob_string:
            try:
                dob_object = datetime.strptime(dob_string, '%Y-%m-%d').date()
            except ValueError:
                return render_template('register.html', error="Invalid date format", problem='dob')
        hashed_password = generate_password_hash(password)
        new_user = User(email=email, DOB = dob_object, username=username, password_hash=hashed_password, email_verified=False) # type: ignore
        session['email'] = email
        db.session.add(new_user)
        db.session.commit()
        
        send_otp(email)
        
        return redirect(url_for('auth.otp_route'))
        
    return render_template('register.html', errors={})

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['email'] = user.email
            return redirect(url_for('auth.home'))
        else:
            if user and not user.check_password(password):
                return render_template('login.html', error="Incorrect password")
            return render_template('login.html', error="Email not found")
    return render_template('login.html')

@auth_bp.route('/otp', methods=['GET', 'POST'])
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
                    return redirect(url_for('auth.home'))
                else:
                    return render_template('otp.html', error="Invalid OTP", email=email)
            else:
                return render_template('otp.html', error="OTP expired", email=email)
    
    return render_template('otp.html')

@auth_bp.route('/resend_otp', methods=['POST'])
def resend_otp():
    email = session['email']
    user = User.query.filter_by(email=email).first()
    if user:
        otp_class = otp.query.filter_by(user_id=user.id).order_by(otp.expires_at.desc()).first()
        if otp_class:
            if otp_class.expires_at + timedelta(minutes=-9) > datetime.now():
                return redirect(url_for('auth.otp_route'))
            db.session.delete(otp_class)
            db.session.commit()
            
            send_otp(email)
            
    return redirect(url_for('auth.otp_route'))

@auth_bp.route('/reset_password', methods=['GET', 'POST'])
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
            expires_at = time() + 600
            new_otp = otp(user_id=user.id, otp_code=otp_code, sent_at=time(), expires_at=expires_at) # type: ignore
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
        return redirect(url_for('auth.otp_route'))
    return render_template('update_password.html')

@auth_bp.route('/logout', methods = ['POST'])
def logout():
    session.pop('email', None)
    return redirect(url_for('auth.login'))