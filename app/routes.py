from app import app
from flask import redirect, url_for, request, render_template


class Obj:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


@app.route('/')
def index():
    return redirect(url_for('select_points'))


@app.route('/select_points', methods=['GET', 'POST'])
def select_points():
    # Cố gắng tải từ các model thực tế; nếu có lỗi thì dùng dữ liệu giả để thay thế
    error = None
    try:
        from app.models import Quan, LoaiDiemThamQuan, DiemThamQuan, compute_travel_durations_from_dinh_doc_lap

        quans = Quan.query.order_by(Quan.TenQuan).all()
        loai_diems = LoaiDiemThamQuan.query.order_by(LoaiDiemThamQuan.TenLoai).all()
        diems = DiemThamQuan.query.order_by(DiemThamQuan.TenDiem).all()

        # tính thời gian di chuyển từ điểm gốc và gắn vào từng diem dưới thuộc tính _computed_duration
        try:
            durations = compute_travel_durations_from_dinh_doc_lap(diems)
            # chuẩn hoá về dict để tránh lỗi NoneType
            if not isinstance(durations, dict):
                app.logger.debug('compute_travel_durations_from_dinh_doc_lap returned non-dict (%r), normalizing to empty dict', durations)
                durations = {}
            app.logger.debug('Computed travel durations: %s', durations)
            for d in diems:
                rid = getattr(d, 'id', None)
                # fallback về thuộc tính duration hoặc --
                default_dur = getattr(d, 'duration', "--")
                if rid is not None:
                    setattr(d, '_computed_duration', durations.get(rid, default_dur))
                else:
                    setattr(d, '_computed_duration', default_dur)
        except Exception:
            # không để lỗi làm crash page,vẫn đảm bảo thuộc tính tồn tại
            app.logger.exception('Could not compute travel durations; falling back to defaults')
            for d in diems:
                setattr(d, '_computed_duration', getattr(d, 'duration', "--"))

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

        # tính thời gian cho dữ liệu giả
        try:
            from app.models import compute_travel_durations_from_dinh_doc_lap
            durations = compute_travel_durations_from_dinh_doc_lap(diems)
            if not isinstance(durations, dict):
                app.logger.debug('compute_travel_durations_from_dinh_doc_lap (mock) returned non-dict (%r), normalizing to empty dict', durations)
                durations = {}
            app.logger.debug('Computed travel durations (mock): %s', durations)
            for d in diems:
                rid = getattr(d, 'id', None)
                default_dur = getattr(d, 'duration', "--")
                if rid is not None:
                    setattr(d, '_computed_duration', durations.get(rid, default_dur))
                else:
                    setattr(d, '_computed_duration', default_dur)
        except Exception:
            app.logger.exception('Could not compute travel durations for mock data')
            for d in diems:
                setattr(d, '_computed_duration', getattr(d, 'duration', "--"))

        if request.method == 'POST':
            selected = request.form.getlist('selected_diems')
            if not selected:
                error = 'Vui lòng chọn ít nhất 1 điểm tham quan.'
            else:
                ids = ','.join(selected)
                return redirect(url_for('index') + f'?selected={ids}')

        return render_template('select_points.html', quans=quans, loai_diems=loai_diems, diems=diems, error=error)
