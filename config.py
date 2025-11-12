"""
Cấu hình cho OptimizeTouristRoutes_GTS

Tệp này xây dựng `SQLALCHEMY_DATABASE_URI` phù hợp cho SQL Server sử dụng
chuỗi kết nối ODBC. Vì lý do bảo mật, mật khẩu cơ sở dữ liệu nên được cung
qua biến môi trường `DB_PASSWORD` hoặc bạn có thể cung cấp chuỗi ODBC đầy đủ
thông qua `DATABASE_URL_ODBC`.

Ví dụ mẫu ODBC (đặt mật khẩu vào DB_PASSWORD):

Driver={ODBC Driver 18 for SQL Server};Server=tcp:optimizetouristroutes.database.windows.net,1433;Database=OptimizeTouristRoutesDB;Uid=thphz363;Pwd={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;

SQLAlchemy sẽ sử dụng dialect `pyodbc` với chuỗi `odbc_connect` đã mã hóa.
Hãy đảm bảo bạn đã cài ODBC Driver 18 for SQL Server trên máy và đã cài
`pyodbc` cùng `sqlalchemy` trong môi trường Python. (t đã dịch)
"""

import os
import urllib.parse

# Khóa bí mật cho Flask (ghi đè bằng biến môi trường trong venv production)
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Ưu tiên dùng chuỗi kết nối ODBC đầy đủ qua biến môi trường
odbc_conn = os.environ.get('DATABASE_URL_ODBC')

if not odbc_conn:
	# đọc mật khẩu từ DB_PASSWORD
	db_password = os.environ.get('DB_PASSWORD')
	if not db_password:
		# Để chỗ trống, web sẽ không kết nối được cho đến khi DB_PASSWORD được đặt
		db_password = '{your_password_here}'

	odbc_conn = (
		r"Driver={ODBC Driver 18 for SQL Server};"
		r"Server=tcp:optimizetouristroutes.database.windows.net,1433;"
		r"Database=OptimizeTouristRoutesDB;"
		f"Uid=thphz363;Pwd={db_password};"
		r"Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
	)

# Mã hóa (URL-encode) chuỗi kết nối ODBC
odbc_conn_quoted = urllib.parse.quote_plus(odbc_conn)

# Chuỗi kết nối SQLAlchemy dùng pyodbc
SQLALCHEMY_DATABASE_URI = f"mssql+pyodbc:///?odbc_connect={odbc_conn_quoted}"

SQLALCHEMY_TRACK_MODIFICATIONS = False
