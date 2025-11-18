from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from .models import db as main_db 

db = main_db

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)
    
    main_db.init_app(app) 

    from .routes import main
    app.register_blueprint(main)

    with app.app_context():
        main_db.create_all()
    return app