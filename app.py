import sys
from builtins import *
from flask import Flask
from flask_migrate import Migrate
from extensions import db, mail  # Import from extensions
from routes import auth_bp  # Import the blueprint

app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"

db.init_app(app)
mail.init_app(app)
migrate = Migrate(app, db)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'xjehoward@gmail.com'
app.config['MAIL_PASSWORD'] = 'lqkq vhzz cppx uzcd'
app.config['MAIL_DEFAULT_SENDER'] = 'xjehoward@gmail.com'

app.register_blueprint(auth_bp, url_prefix='/')  # Register the blueprint

from databases import *

def empty_table(model):
    try:
        num_rows_deleted = db.session.query(model).delete()
        db.session.commit()
        return f"{num_rows_deleted} rows deleted from {model.__tablename__}"
    except Exception as e:
        db.session.rollback()
        return f"Error emptying table {model.__tablename__}: {e}"

if __name__ == '__main__':
    try:
        match sys.argv[1]:
            case 'clear':
                with app.app_context():
                    print(empty_table(User))
                    print(empty_table(otp))
            case 'run':
                app.run(debug=True)
    except:
        raise Exception("Must provide a command: 'run' to run the app or 'clear' to clear the database.")
