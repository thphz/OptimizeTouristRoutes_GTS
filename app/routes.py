from flask import render_template, request, redirect, url_for
from app import app


class Obj:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


@app.route('/')
def index():
    return redirect(url_for('select_points'))


@app.route('/select_points', methods=['GET', 'POST'])
def select_points():
    """Render the select points page.

    If a real database and models are present, you should replace the
    mock data below with queries to your models (Quan, LoaiDiemThamQuan,
    DiemThamQuan). For development this route provides sample data so the
    UI can be tested immediately.
    """
    # Cố gắng tải từ các model thực tế; nếu có lỗi thì dùng dữ liệu giả để thay thế
    error = None
    try:
        from app.models import Quan, LoaiDiemThamQuan, DiemThamQuan

        quans = Quan.query.order_by(Quan.TenQuan).all()
        loai_diems = LoaiDiemThamQuan.query.order_by(LoaiDiemThamQuan.TenLoai).all()
        diems = DiemThamQuan.query.order_by(DiemThamQuan.TenDiem).all()

        if request.method == 'POST':
            selected = request.form.getlist('selected_diems')
            if not selected:
                error = 'Vui lòng chọn ít nhất 1 điểm tham quan.'
            else:
                ids = ','.join(selected)
                return redirect(url_for('index') + f'?selected={ids}')

        return render_template('select_points.html', quans=quans, loai_diems=loai_diems, diems=diems, error=error)

    except Exception as e:
        # Nếu DB/models không dùng được thì dùng dữ liệu giả để UI
        app.logger.exception('Could not load real data, using mock data: %s', e)

        quans = [Obj(id=1, ten='Quận 1'), Obj(id=3, ten='Quận 3'), Obj(id=4, ten='Quận 4')]
        loai_diems = [Obj(id=1, ten='Đền/Đình'), Obj(id=2, ten='Bảo tàng'), Obj(id=3, ten='Nhà thờ')]
        diems = [
            Obj(id=1, ten='Dinh Độc Lập', duration=60, quan_id=1, quan=quans[0], loai_id=1, vi_do=10.7769, kinh_do=106.7009),
            Obj(id=2, ten='Nhà Thờ Đức Bà', duration=45, quan_id=1, quan=quans[0], loai_id=3, vi_do=10.7798, kinh_do=106.6996),
            Obj(id=3, ten='Bưu Điện Trung Tâm Sài Gòn', duration=30, quan_id=1, quan=quans[0], loai_id=1, vi_do=10.7790, kinh_do=106.6992),
            Obj(id=4, ten='Phố Đi Bộ Nguyễn Huệ', duration=45, quan_id=1, quan=quans[0], loai_id=2, vi_do=10.7774, kinh_do=106.6991),
            Obj(id=5, ten='Bảo Tàng Chứng Tích Chiến Tranh', duration=90, quan_id=3, quan=quans[1], loai_id=2, vi_do=10.7776, kinh_do=106.6887),
        ]

        if request.method == 'POST':
            selected = request.form.getlist('selected_diems')
            if not selected:
                error = 'Vui lòng chọn ít nhất 1 điểm tham quan.'
            else:
                ids = ','.join(selected)
                return redirect(url_for('index') + f'?selected={ids}')

        return render_template('select_points.html', quans=quans, loai_diems=loai_diems, diems=diems, error=error)
