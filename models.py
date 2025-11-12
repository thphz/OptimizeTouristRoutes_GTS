from app import db

class Quan(db.Model):
    __tablename__ = "Quan"
    QuanID = db.Column(db.Integer, primary_key=True)
    TenQuan = db.Column(db.String(100), nullable=False)
    MoTa = db.Column(db.String(255))
    diem = db.relationship("DiemThamQuan", backref="quan", lazy=True)

class LoaiDiemThamQuan(db.Model):
    __tablename__ = "LoaiDiemThamQuan"
    LoaiID = db.Column(db.Integer, primary_key=True)
    TenLoai = db.Column(db.String(100), nullable=False)
    MoTa = db.Column(db.String(300))
    diem = db.relationship("DiemThamQuan", backref="loai", lazy=True)

class DiemThamQuan(db.Model):
    __tablename__ = "DiemThamQuan"
    DiemID = db.Column(db.Integer, primary_key=True)
    TenDiem = db.Column(db.String(200), nullable=False)
    MoTa = db.Column(db.String(2000))
    DiaChi = db.Column(db.String(300))
    QuanID = db.Column(db.Integer, db.ForeignKey("Quan.QuanID"))
    LoaiID = db.Column(db.Integer, db.ForeignKey("LoaiDiemThamQuan.LoaiID"))
    ViDo = db.Column(db.Float, nullable=False)
    KinhDo = db.Column(db.Float, nullable=False)
    GioMoCua = db.Column(db.Time)
    GioDongCua = db.Column(db.Time)
    hinh = db.relationship("HinhAnhDiem", backref="diem", lazy=True)

class HinhAnhDiem(db.Model):
    __tablename__ = "HinhAnhDiem"
    HinhID = db.Column(db.Integer, primary_key=True)
    DiemID = db.Column(db.Integer, db.ForeignKey("DiemThamQuan.DiemID"))
    UrlHinh = db.Column(db.String(255), nullable=False)
    MoTaHinh = db.Column(db.String(200))
