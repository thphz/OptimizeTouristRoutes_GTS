from flask import Flask

app = Flask(__name__, static_folder='static', template_folder='templates')

# Tải cấu hình từ file cấp dự án (config.py) nếu có
try:
    app.config.from_object('config')
except Exception:
    # Nếu file cấu hình bị thiếu hoặc không hợp lệ, tiếp tục với giá trị mặc định
    pass

# Cố gắng khởi tạo SQLAlchemy nếu có thư viện
try:
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy(app)
except Exception:
    db = None

# Import routes để chúng được đăng ký với ứng dụng
try:
    from app import routes  # noqa: F401
except Exception:
    # routes có thể chưa tồn tại trong giai đoạn phát triển ban đầu; bỏ qua lỗi import ở đây
    pass

__all__ = ['app', 'db']
