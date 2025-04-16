from flask import Flask, render_template, request, session, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mydatabase.db"
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    username = db.Column(db.String(150), nullable=False)
    DOB = db.Column(db.Date, nullable=True)
    password_hash = db.Column(db.String(150), nullable=False)
    
    tasks = db.relationship('SetTasks', backref='user', lazy=True)
    home_owner = db.relationship('Homes', backref='owner', lazy=True)
    homes = db.relationship('UserInHome', backref='user', lazy=True)
    rota_set = db.relationship('Rotas', backref='set', lazy=True)
    rota = db.relationship('RotaUsers', backref='user', lazy=True)
    photo_uploader = db.relationship('Photos', backref='uploader', lazy=True)
    file_uploader = db.relationship('Files', backref='uploader', lazy=True)
    pinboard_creator = db.relationship('PinboardItems', backref='creator', lazy=True)
    tasks_creator = db.relationship('SetTasks', backref='creator', lazy=True)
    
    def update_password(self, password):
        self.password_hash = generate_password_hash(password)
        db.session.commit()
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class SetTasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    home_id = db.Column(db.Integer, db.ForeignKey('home.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    task_name = db.Column(db.String(200), nullable=False)
    date_set = db.Column(db.DateTime, default=datetime.utcnow)
    date_due = db.Column(db.DateTime, nullable=True)
    description = db.Column(db.String(1000), nullable=True)
    set_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    attachment = db.relationship('TaskAttachments', backref='task', lazy=True)

class TaskAttachments(db.Model):
    task_id = db.Column(db.Integer, db.ForeignKey('SetTasks.id'), primary_key=True)
    attachment_id = db.Column(db.Integer, db.ForeignKey('Files.id'), primary_key=True)

class Homes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    home_name = db.Column(db.String(200), nullable=False)
    home_description = db.Column(db.String(1000), nullable=True)
    join_by_link = db.Column(db.Boolean, default=False)
    home_password = db.Column(db.String(200), nullable=True)
    background_photo = db.Column(db.LargeBinary, nullable=True)
    tasks = db.relationship('SetTasks', backref='home', lazy=True)
    users = db.relationship('UserInHome', backref='home', lazy=True)
    photos = db.relationship('Photos', backref='home', lazy=True)
    pinboard = db.relationship('Pinboard', backref='home', lazy=True)
    lists = db.relationship('Lists', backref='home', lazy=True) 
    events = db.relationship('Event', backref='home', lazy=True) 
    files = db.relationship('Files', backref='home', lazy=True) 
    rotas = db.relationship('Rotas', backref='home', lazy=True) 

class UserInHome(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    home_id = db.Column(db.Integer, db.ForeignKey('home.id'), primary_key=True)
    is_admin = db.Column(db.Boolean, default=False)

class Rotas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    home_id = db.Column(db.Integer, db.ForeignKey('home.id'), nullable=False)
    rota_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(1000), nullable=True)
    last_changed = db.Column(db.DateTime, default=datetime.utcnow)
    set_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    pointer = db.Column(db.Integer, nullable=True)
    size = db.Column(db.Integer, nullable=True)
    users = db.relationship('RotaUsers', backref='rota', lazy=True)

class RotaUsers(db.Model):
    rota_id = db.Column(db.Integer, db.ForeignKey('rotas.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    position = db.Column(db.Integer, nullable=False)
    catchup = db.Column(db.Integer, nullable=False)

class Lists(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    home_id = db.Column(db.Integer, db.ForeignKey('home.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    admin_only = db.Column(db.Boolean, default=False)
    item = db.relationship('ListItems', backref='list', lazy=True)

class ListItems(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey('Lists.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)

class Photos(db.Model):
    photo_id = db.Column(db.Integer, primary_key=True)
    home_id = db.Column(db.Integer, db.ForeignKey('home.id'), nullable=False)
    uploader_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    photo = db.Column(db.LargeBinary, nullable=False)
    date_uploaded = db.Column(db.DateTime, default=datetime.utcnow)
    event = db.relationship('EventPhotos', backref='photo', lazy=True)

class Pinboard(db.Model):
    pinboard_id = db.Column(db.Integer, primary_key=True)
    home_id = db.Column(db.Integer, db.ForeignKey('home.id'), nullable=False)
    admin_only = db.Column(db.Boolean, default=False)
    item = db.relationship('PinboardItems', backref='pinboard', lazy=True)

class PinboardItems(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pinboard_id = db.Column(db.Integer, db.ForeignKey('Pinboard.id'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    position_x = db.Column(db.Integer, nullable=False)
    position_y = db.Column(db.Integer, nullable=False)
    size_x = db.Column(db.Integer, nullable=False)
    size_y = db.Column(db.Integer, nullable=False)

class PinboardAttachments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('PinboardItems.id'), nullable=False)
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'), nullable=False)

class Files(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    home_id = db.Column(db.Integer, db.ForeignKey('home.id'), nullable=False)
    uploader_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    file = db.Column(db.LargeBinary, nullable=False)
    date_uploaded = db.Column(db.DateTime, default=datetime.utcnow)

class Event(db.Model):
    event_id = db.Column(db.Integer, primary_key=True)
    home_id = db.Column(db.Integer, db.ForeignKey('home.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(400), nullable=True)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    photo = db.relationship('EventPhotos', backref='event', lazy=True)

class EventPhotos(db.Model):
    event_id = db.Column(db.Integer, db.ForeignKey('Event.id'), primary_key=True)
    photo_id = db.Column(db.Integer, db.ForeignKey('Photos.id'), primary_key=True)


@app.route('/')
def home():
    if 'email' in session:
        return render_template('home.html', email=session['email'])
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        dob = request.form['DOB']
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(email=email, DOB = dob, username=username, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('home'))

@app.route('/update_password', methods=['GET', 'POST'])
def update_password():
    if request.method == 'POST':
        password = request.form['password']
        user = User.query.filter_by(email=session['email']).first()
        user.update_password(password)
        return redirect(url_for('home'))
    return render_template('update_password.html')

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

if __name__ == '__main__':
    app.run(debug=True)
