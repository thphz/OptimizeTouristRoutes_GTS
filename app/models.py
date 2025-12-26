from app import db
from sqlalchemy import func
import math
import json


class Quan(db.Model):
    __tablename__ = 'Quan'
    QuanID = db.Column(db.Integer, primary_key=True)
    TenQuan = db.Column(db.Unicode(100), nullable=False)
    MoTa = db.Column(db.Unicode(255))

    def __repr__(self):
        return f"<Quan {self.QuanID} {self.TenQuan}>"
    @property
    def id(self):
        return self.QuanID

    @property
    def ten(self):
        return self.TenQuan


class LoaiDiemThamQuan(db.Model):
    __tablename__ = 'LoaiDiemThamQuan'
    LoaiID = db.Column(db.Integer, primary_key=True)
    TenLoai = db.Column(db.Unicode(100), nullable=False)
    MoTa = db.Column(db.Unicode(300))

    def __repr__(self):
        return f"<Loai {self.LoaiID} {self.TenLoai}>"
    @property
    def id(self):
        return self.LoaiID

    @property
    def ten(self):
        return self.TenLoai


class DiemThamQuan(db.Model):
    __tablename__ = 'DiemThamQuan'
    DiemID = db.Column(db.Integer, primary_key=True)
    TenDiem = db.Column(db.Unicode(200), nullable=False)
    MoTa = db.Column(db.Unicode(2000))
    DiaChi = db.Column(db.Unicode(300))
    QuanID = db.Column(db.Integer, db.ForeignKey('Quan.QuanID'))
    LoaiID = db.Column(db.Integer, db.ForeignKey('LoaiDiemThamQuan.LoaiID'))
    ViDo = db.Column(db.Numeric(10, 6), nullable=False)
    KinhDo = db.Column(db.Numeric(10, 6), nullable=False)
    GioMoCua = db.Column(db.Time)
    GioDongCua = db.Column(db.Time)
    Duration = db.Column(db.Integer, default=60)

    # quan hệ
    quan = db.relationship('Quan', backref=db.backref('diems', lazy='dynamic'))
    loai = db.relationship('LoaiDiemThamQuan', backref=db.backref('diems', lazy='dynamic'))

    def __repr__(self):
        return f"<Diem {self.DiemID} {self.TenDiem}>"
    
    def to_dict(self):
        """Chuyển đổi object thành dictionary để trả về JSON API"""
        return {
            'id': self.DiemID,
            'name': self.TenDiem,
            'description': self.MoTa,
            'address': self.DiaChi,
            'quan_id': self.QuanID,
            'loai_id': self.LoaiID,
            'lat': float(self.ViDo) if self.ViDo else None,
            'lng': float(self.KinhDo) if self.KinhDo else None,
            'open_time': self.GioMoCua.strftime('%H:%M') if self.GioMoCua else None,
            'close_time': self.GioDongCua.strftime('%H:%M') if self.GioDongCua else None,
            'duration': self.duration
        }
    
    @property
    def id(self):
        return self.DiemID

    @property
    def ten(self):
        return self.TenDiem

    @property
    def vi_do(self):
        return float(self.ViDo)

    @property
    def kinh_do(self):
        return float(self.KinhDo)

    @property
    def duration(self):
        """Thời gian tham quan (phút) - lấy từ cột Duration trong DB, mặc định 60 phút"""
        return self.Duration if self.Duration is not None else 60

    @property
    def image_url(self):
        """Trả về UrlHinh đầu tiên cho điểm này hoặc chuỗi rỗng.

        Phương thức xử lý cả hai trường hợp: quan hệ động (trả về query) và
        collection giống danh sách.
        """
        try:
            if not hasattr(self, 'hinh_anh') or self.hinh_anh is None:
                return ''
            # Nếu quan hệ là dynamic nó cung cấp phương thức .first()
            if hasattr(self.hinh_anh, 'first'):
                first = self.hinh_anh.first()
                return getattr(first, 'UrlHinh', '') if first else ''
            # Ngược lại xử lý như một sequence
            if hasattr(self.hinh_anh, '__len__'):
                if len(self.hinh_anh) > 0:
                    return getattr(self.hinh_anh[0], 'UrlHinh', '')
            return ''
        except Exception:
            return ''


class HinhAnhDiem(db.Model):
    __tablename__ = 'HinhAnhDiem'
    HinhID = db.Column(db.Integer, primary_key=True)
    DiemID = db.Column(db.Integer, db.ForeignKey('DiemThamQuan.DiemID'))
    UrlHinh = db.Column(db.Unicode(255), nullable=False)
    MoTaHinh = db.Column(db.Unicode(200))

    diem = db.relationship('DiemThamQuan', backref=db.backref('hinh_anh', lazy='dynamic'))

    def __repr__(self):
        return f"<HinhAnh {self.HinhID} for Diem {self.DiemID}>"

