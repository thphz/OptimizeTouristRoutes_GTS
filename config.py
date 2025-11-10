"""
Configuration for OptimizeTouristRoutes_GTS

This file builds a SQLALCHEMY_DATABASE_URI suitable for SQL Server using the
ODBC connection string template you provided. For security, the database
password should be provided via environment variable `DB_PASSWORD` or you can
provide a full ODBC connection string through `DATABASE_URL_ODBC`.

Example ODBC template (place your password in DB_PASSWORD):

Driver={ODBC Driver 18 for SQL Server};Server=tcp:optimizetouristroutes.database.windows.net,1433;Database=OptimizeTouristRoutesDB;Uid=thphz363;Pwd={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;

SQLAlchemy will use the pyodbc dialect with an encoded odbc_connect string.
Make sure you have the ODBC Driver 18 for SQL Server installed on the host
and `pyodbc` and `sqlalchemy` installed in your Python environment.
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

# Mã hóa (URL-encode) conn string ODBC
odbc_conn_quoted = urllib.parse.quote_plus(odbc_conn)

# Chuỗi kết nối SQLAlchemy dùng pyodbc
SQLALCHEMY_DATABASE_URI = f"mssql+pyodbc:///?odbc_connect={odbc_conn_quoted}"

SQLALCHEMY_TRACK_MODIFICATIONS = False
