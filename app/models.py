from app import db
from sqlalchemy import func
import math
import json

# import requests theo cách lười để tránh lỗi phụ thuộc bắt buộc khi chạy trong chế độ không có DB
try:
    import requests
except Exception:
    requests = None


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


# --- Trợ giúp về định tuyến / thời lượng ---
# Điểm gốc cố định: Dinh Độc Lập
DINH_DOC_LAP = (10.777017, 106.695859)


def _haversine_km(a_lat, a_lng, b_lat, b_lng):
    # trả về khoảng cách theo kilômét
    R = 6371.0
    phi1 = math.radians(a_lat)
    phi2 = math.radians(b_lat)
    delta_phi = math.radians(b_lat - a_lat)
    delta_lambda = math.radians(b_lng - a_lng)
    p = math.sin(delta_phi/2.0)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(delta_lambda/2.0)**2
    c = 2 * math.atan2(math.sqrt(p), math.sqrt(1-p))
    return R * c


def compute_travel_durations_from_dinh_doc_lap(points, osrm_base='https://router.project-osrm.org'):
    """
    Tính thời lượng di chuyển (phút) từ gốc cố định Dinh Độc Lập tới tập các điểm.

    Tham số:
    - points: iterable các đối tượng hoặc dict có thuộc tính 'id', 'vi_do' (hoặc 'lat'), 'kinh_do' (hoặc 'lng')
    - osrm_base: URL gốc cho server OSRM

    Trả về: dict ánh xạ id điểm -> thời lượng_phút (int)
    Nếu truy vấn OSRM thất bại, trả về ước lượng thời gian dựa trên khoảng cách thẳng và tốc độ giả định.
    """
    origin_lat, origin_lng = DINH_DOC_LAP
    valid_points = []
    for p in points:
        # chấp nhận model instance hoặc dict-like
        try:
            plat = getattr(p, 'vi_do', None) or getattr(p, 'lat', None) or (p.get('vi_do') if isinstance(p, dict) else None)
            plng = getattr(p, 'kinh_do', None) or getattr(p, 'lng', None) or (p.get('kinh_do') if isinstance(p, dict) else None)
            pid = getattr(p, 'id', None) or (p.get('id') if isinstance(p, dict) else None)
        except Exception:
            plat = plng = pid = None
        if plat is None or plng is None or pid is None:
            continue
        try:
            plat = float(plat)
            plng = float(plng)
        except Exception:
            continue
        valid_points.append({'id': pid, 'lat': plat, 'lng': plng})

    if len(valid_points) == 0:
        return {}

    # Xây dựng yêu cầu OSRM table: toạ độ gốc trước
    # OSRM mong đợi thứ tự lon,lat
    coord_str = f"{origin_lng},{origin_lat}"
    for vp in valid_points:
        coord_str += f";{vp['lng']},{vp['lat']}"

    # chỉ số đích là 1..n (vì nguồn là 0)
    dests = ";".join(str(i) for i in range(1, len(valid_points) + 1))
    url = f"{osrm_base}/table/v1/driving/{coord_str}?sources=0&destinations={dests}&annotations=duration"

    # ước lượng mặc định: giả định tốc độ trung bình đô thị 30 km/h
    estimation = {}
    for vp in valid_points:
        d = _haversine_km(origin_lat, origin_lng, vp['lat'], vp['lng'])
        # hours = km / speed
        hours = d / 30.0
        mins = max(1, int(round(hours * 60)))
        estimation[vp['id']] = mins

    if not requests:
        # requests không có, trả về ước lượng
        return estimation

    try:
        resp = requests.get(url, timeout=8)
        if resp.status_code != 200:
            return estimation
        data = resp.json()
        # data.durations là ma trận với 1 hàng (nguồn) và n cột (đích)
        if 'durations' in data and isinstance(data['durations'], list) and len(data['durations']) > 0:
            durs = data['durations'][0]
            result = {}
            for idx, vp in enumerate(valid_points):
                dur_seconds = durs[idx]
                if dur_seconds is None:
                    # không có tuyến; fallback về ước lượng
                    result[vp['id']] = estimation[vp['id']]
                else:
                    result[vp['id']] = max(1, int(round(dur_seconds / 60.0)))
            return result
    except Exception:
        # trên bất kỳ lỗi nào, fallback về ước lượng
        return estimation

    # không thể tới đây
    return estimation

