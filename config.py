import os
import urllib.parse

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "devkey")
    
    DB_USER = os.environ.get("DB_USER", "sa")
    DB_PASSWORD = urllib.parse.quote_plus(os.environ.get("DB_PASSWORD", "111"))
    DB_SERVER = os.environ.get("DB_SERVER", "localhost")
    DB_NAME = os.environ.get("DB_NAME", "OptimizeTouristRoutes_GTS")

    SQLALCHEMY_DATABASE_URI = (
        f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}"
        "?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
