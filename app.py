from flask import Flask, render_template 
from application.model import db

from application.routes import *
def create_app():
    app = Flask(__name__)
    app.secret_key = "my_secret_key_123" 
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mydb.sqlite3"
    db.init_app(app)
    
    UPLOAD_FOLDER = "static/resumes"
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    '''
    loginmanager=LoginManager()
    loginmanager.init_app(app)
    @loginmanager.user_loader
    def load_user(email):
        user = db.session.query(Professional).filter_by(email=email).first() or \
                db.session.query(Customer).filter_by(email=email).first() or\
                db.session.query(Admin).filter_by(email=email).first()
        return user'''
    app.app_context().push()
    return app


app = create_app()  

from application.initial_data import *
from application.routes import *


if __name__== "__main__":
    
    app.run(debug=True)