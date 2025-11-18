from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

# Khởi tạo instance SQLAlchemy
db = SQLAlchemy() 

# Bảng Quận
class Quan(db.Model):
    __tablename__ = 'Quan' 
    QuanID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    TenQuan = db.Column(db.String(100), nullable=False)
    diem_tham_quan = relationship("DiemThamQuan", back_populates="quan") 

# Bảng Loại Điểm Tham Quan
class LoaiDiemThamQuan(db.Model):
    __tablename__ = 'LoaiDiemThamQuan'
    LoaiID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    TenLoai = db.Column(db.String(100), nullable=False)
    diem_tham_quan = relationship("DiemThamQuan", back_populates="loai")

# Bảng Điểm Tham Quan
class DiemThamQuan(db.Model):
    __tablename__ = 'DiemThamQuan'
    DiemID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    TenDiem = db.Column(db.String(200), nullable=False)
    MoTa = db.Column(db.String(2000))
    DiaChi = db.Column(db.String(300))
    
    QuanID = db.Column(db.Integer, ForeignKey('Quan.QuanID'))
    LoaiID = db.Column(db.Integer, ForeignKey('LoaiDiemThamQuan.LoaiID'))
    
    ViDo = db.Column(db.Numeric(10, 6), nullable=False)
    KinhDo = db.Column(db.Numeric(10, 6), nullable=False)
    
    quan = relationship("Quan", back_populates="diem_tham_quan")
    loai = relationship("LoaiDiemThamQuan", back_populates="diem_tham_quan")

# Bảng Hình Ảnh Điểm
class HinhAnhDiem(db.Model):
    __tablename__ = 'HinhAnhDiem'
    HinhID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    DiemID = db.Column(db.Integer, ForeignKey('DiemThamQuan.DiemID'))
    UrlHinh = db.Column(db.String(255), nullable=False)
    MoTaHinh = db.Column(db.String(200))
    
    diem_tham_quan = relationship("DiemThamQuan", backref="hinh_anh")