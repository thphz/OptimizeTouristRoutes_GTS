from app import db
from decimal import Decimal 

class Quan(db.Model):
    __tablename__ = 'Quan'
    QuanID = db.Column(db.Integer, primary_key=True)
    TenQuan = db.Column(db.String(100), nullable=False)

class LoaiDiemThamQuan(db.Model):
    __tablename__ = 'LoaiDiemThamQuan'
    LoaiID = db.Column(db.Integer, primary_key=True)
    TenLoai = db.Column(db.String(100), nullable=False)

class DiemThamQuan(db.Model):

    __tablename__ = 'DiemThamQuan' 
    
    DiemID = db.Column(db.Integer, primary_key=True)
    
    TenDiem = db.Column(db.String(200), nullable=False)
    ViDo = db.Column(db.DECIMAL(10, 6), nullable=False)
    KinhDo = db.Column(db.DECIMAL(10, 6), nullable=False)
    
    QuanID = db.Column(db.Integer, db.ForeignKey('Quan.QuanID'))
    LoaiID = db.Column(db.Integer, db.ForeignKey('LoaiDiemThamQuan.LoaiID'))
    
    def to_dict(self):
        """Hàm tiện ích để chuyển Model thành JSON cho API"""
        return {
            'id': self.DiemID,
            'name': self.TenDiem,

            'lat': float(self.ViDo), 
            'lng': float(self.KinhDo)
        }

class HinhAnhDiem(db.Model):
    __tablename__ = 'HinhAnhDiem'
    HinhID = db.Column(db.Integer, primary_key=True)
    UrlHinh = db.Column(db.String(255), nullable=False)
    DiemID = db.Column(db.Integer, db.ForeignKey('DiemThamQuan.DiemID'))