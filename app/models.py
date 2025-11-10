from app import db
from sqlalchemy import func


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

	# quan hệ
	quan = db.relationship('Quan', backref=db.backref('diems', lazy='dynamic'))
	loai = db.relationship('LoaiDiemThamQuan', backref=db.backref('diems', lazy='dynamic'))

	def __repr__(self):
		return f"<Diem {self.DiemID} {self.TenDiem}>"

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
		# CSDL gốc không bao gồm cột duration; dùng giá trị mặc định
		return 60


class HinhAnhDiem(db.Model):
	__tablename__ = 'HinhAnhDiem'
	HinhID = db.Column(db.Integer, primary_key=True)
	DiemID = db.Column(db.Integer, db.ForeignKey('DiemThamQuan.DiemID'))
	UrlHinh = db.Column(db.Unicode(255), nullable=False)
	MoTaHinh = db.Column(db.Unicode(200))

	diem = db.relationship('DiemThamQuan', backref=db.backref('hinh_anh', lazy='dynamic'))

	def __repr__(self):
		return f"<HinhAnh {self.HinhID} for Diem {self.DiemID}>"

