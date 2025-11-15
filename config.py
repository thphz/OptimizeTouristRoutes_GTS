import os
from dotenv import load_dotenv
import urllib 

load_dotenv()

class Config:
    """
    Tải cấu hình từ Biến Môi trường (Environment Variables).
    """
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-fallback'

    DB_USER = "dev_readonly" 
    DB_SERVER = "optimizetouristroutes.database.windows.net"
    DB_NAME = "OptimizeTouristRoutesDB"
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    
    if not DB_PASSWORD:
        print("CẢNH BÁO: Không tìm thấy 'DB_PASSWORD'. App sẽ không thể kết nối DB.")
        SQLALCHEMY_DATABASE_URI = None
    else:
        safe_password = urllib.parse.quote_plus(DB_PASSWORD)

        SQLALCHEMY_DATABASE_URI = (
            f"mssql+pyodbc://{DB_USER}:{safe_password}@{DB_SERVER}/{DB_NAME}?"
            "driver=ODBC+Driver+18+for+SQL+Server&"
            "Encrypt=yes&TrustServerCertificate=no&ConnectionTimeout=30"
        )