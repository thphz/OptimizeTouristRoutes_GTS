# OptimizeTouristRoutes_GTS

## Sử dụng biến môi trường
`config.py` trong project sẽ ưu tiên dùng các biến môi trường sau:

- `DATABASE_URL_ODBC` — (tùy chọn) đặt toàn bộ ODBC connection string (bao gồm mật khẩu). Nếu có biến này, chương trình sẽ dùng trực tiếp.
- `DB_PASSWORD` — nếu `DATABASE_URL_ODBC` không tồn tại, `config.py` sẽ đọc `DB_PASSWORD` và chèn vào template ODBC có sẵn trong file.
- `SECRET_KEY` — có mặc định `'dev-secret-key'` trong file nhưng nên ghi đè bằng biến môi trường cho môi trường production.

Ví dụ nhanh (PowerShell):

Tạm thời cho session hiện tại:

```powershell
$env:DB_PASSWORD = "MyRealDbPassword"
$env:SECRET_KEY = "dev-secret"
python run.py
```

Vĩnh viễn cho user (dùng `setx`; mở lại PowerShell để biến có hiệu lực):

```powershell
setx DB_PASSWORD "MyRealDbPassword"
setx SECRET_KEY "my-prod-secret"
# Mở lại terminal mới
python run.py
```

Sử dụng toàn bộ ODBC connection string thay vì `DB_PASSWORD`:

```powershell
$env:DATABASE_URL_ODBC = 'Driver={ODBC Driver 18 for SQL Server};Server=tcp:optimizetouristroutes.database.windows.net,1433;Database=OptimizeTouristRoutesDB;Uid=thphz363;Pwd=MyRealDbPassword;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
python run.py
```

## Sử dụng `.env` (tùy chọn)

Bạn có thể dùng file `.env` trong thư mục project để lưu tạm các biến (không commit file này vào Git). Thao tác nhanh:

1. Cài `python-dotenv`:

```powershell
pip install python-dotenv
```

2. Tạo file `.env` (thêm vào `.gitignore`):

```
# .env (KHÔNG commit)
DB_PASSWORD=MyRealDbPassword
SECRET_KEY=dev-secret
# hoặc
# DATABASE_URL_ODBC=Driver={...};Server=...;Pwd=...;
```

3. Tải các biến lên trước khi `config` được import — ví dụ mở `run.py` hoặc `app/__init__.py` và thêm:

```python
from dotenv import load_dotenv
load_dotenv()

# sau đó import config hoặc khởi tạo app như bình thường
```

Ghi chú:
- Không được commit mật khẩu hoặc `.env` chứa secrets lên repo.
- Trên production, dùng secret manager của provider (Azure Key Vault, AWS Secrets Manager, các biến môi trường của nền tảng) thay vì `.env`.

