import os
import urllib.parse

class Config:
    # 1. Cấu hình bảo mật
    SECRET_KEY = os.environ.get("SECRET_KEY", "devkey")
    
    # 2. Cấu hình Database (MSSQL)
    DB_USER = os.environ.get("DB_USER", "sa")
    # Quote_plus đảm bảo các ký tự đặc biệt trong mật khẩu được xử lý đúng
    DB_PASSWORD = urllib.parse.quote_plus(os.environ.get("DB_PASSWORD", "111"))
    DB_SERVER = os.environ.get("DB_SERVER", "localhost")
    DB_NAME = os.environ.get("DB_NAME", "OptimizeTouristRoutes_GTS")

    # Xây dựng chuỗi kết nối SQLAlchemy cho MSSQL (Sử dụng ODBC Driver 18)
    SQLALCHEMY_DATABASE_URI = (
        f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}"
        "?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 3. Cấu hình ứng dụng Flask/Cache
    # Vô hiệu hóa cache cho các file tĩnh (giúp việc phát triển dễ dàng hơn)
    SEND_FILE_MAX_AGE_DEFAULT = 0 
    
    # Map center default (TP.HCM)
    MAP_CENTER = [10.776889, 106.700806]