document.addEventListener('DOMContentLoaded', function () {
	const filterQuan = document.getElementById('filter-quan');
	const filterLoai = document.getElementById('filter-loai');
	const selectedCountEl = document.getElementById('selected-count');
	const totalTimeEl = document.getElementById('total-time');
	const totalPointsEl = document.getElementById('total-points');
	const selectedList = document.getElementById('selected-summary-list');
	const optimizeBtn = document.getElementById('optimize-btn');
	const form = document.getElementById('select-form');
	const resetBtn = document.getElementById('reset-btn');
	const clearBtn = document.getElementById('clear-selection');

	function filterDiems() {
		const q = filterQuan ? filterQuan.value : '';
		const l = filterLoai ? filterLoai.value : '';
		const items = Array.from(document.querySelectorAll('.diem-item'));
		items.forEach(item => {
			const qi = item.dataset.quanId || '';
			const li = item.dataset.loaiId || '';
			const showQ = !q || (qi + '') === (q + '');
			const showL = !l || (li + '') === (l + '');
			const shouldShow = (showQ && showL);
			item.classList.toggle('d-none', !shouldShow);
			if (!shouldShow) {
				const cb = item.querySelector('.select-diem');
				if (cb && cb.checked) cb.checked = false;
			}
		});
		updateSummary();
	}

	function isVisibleItem(item) {
		return item && !item.classList.contains('d-none');
	}

	function updateSummary() {
		// chỉ xem xét các checkbox đã được chọn nằm trong các diem-item đang hiển thị
		const allChecked = Array.from(document.querySelectorAll('.select-diem:checked'));
		const checked = allChecked.filter(cb => {
			const item = cb.closest('.diem-item');
			return isVisibleItem(item);
		});
		if (selectedCountEl) selectedCountEl.textContent = checked.length;

		let totalMinutes = 0;
		if (selectedList) selectedList.innerHTML = '';
		checked.forEach((cb, idx) => {
			const item = cb.closest('.diem-item');
			const name = (item.querySelector('label') || {}).textContent.trim();
			const duration = parseInt(item.dataset.duration || '60', 10);
			totalMinutes += duration;

			const li = document.createElement('li');
			li.className = 'mb-2 p-2 border rounded d-flex align-items-center gap-2';
			li.innerHTML = `<div class="badge bg-primary text-white">${idx+1}</div>
						<div class="flex-grow-1">
							<div class="fw-semibold">${name}</div>
							<small class="text-muted">${duration} phút</small>
						</div>`;
			selectedList.appendChild(li);
		});

		// Định dạng thời gian -> H giờ M phút
		const hours = Math.floor(totalMinutes / 60);
		const mins = totalMinutes % 60;
		if (totalTimeEl) totalTimeEl.textContent = `${hours}h ${mins}m`;
		if (totalPointsEl) totalPointsEl.textContent = `${checked.length} địa điểm`;
	}

	// hooks khởi tạo
	if (filterQuan) filterQuan.addEventListener('change', function () { filterDiems(); refreshMarkers(); });
	if (filterLoai) filterLoai.addEventListener('change', function () { filterDiems(); refreshMarkers(); });
	// gán handler change lên document để bắt các checkbox thêm sau
	document.addEventListener('change', function (e) {
		if (e.target && e.target.classList && e.target.classList.contains('select-diem')) {
			updateSummary();
			refreshMarkers();
		}
	});

	// kiểm tra form
	if (form) {
		form.addEventListener('submit', function (e) {
			const checked = Array.from(document.querySelectorAll('.select-diem:checked'))
				.filter(cb => {
					const item = cb.closest('.diem-item');
					return isVisibleItem(item);
				});
			if (checked.length === 0) {
				e.preventDefault();
				alert('Vui lòng chọn ít nhất 1 điểm tham quan.');
			}
		});
	}

	if (resetBtn) resetBtn.addEventListener('click', function () {
		document.querySelectorAll('.select-diem').forEach(cb => cb.checked = false);
		if (filterQuan) filterQuan.value = '';
		if (filterLoai) filterLoai.value = '';
		filterDiems();
		updateSummary();
		refreshMarkers();
	});

	if (clearBtn) clearBtn.addEventListener('click', function () {
		document.querySelectorAll('.select-diem').forEach(cb => cb.checked = false);
		updateSummary();
		refreshMarkers();
	});

	filterDiems();
	updateSummary();

	// --- Khởi tạo mini-map ---
	let map = null;
	let markers = null;
	let routeLayer = null; // lớp chứa tuyến đường đã vẽ
	try {
		const miniMapEl = document.getElementById('mini-map');
		if (miniMapEl && typeof L !== 'undefined') {
			// tạo bản đồ
			map = L.map(miniMapEl).setView([10.7769, 106.70098], 12);

			//lớp tile OSM
			L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
				attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
			}).addTo(map);

			// helper để thêm marker từ các diem-item đang hiển thị
			markers = L.layerGroup().addTo(map);
		}
	} catch (err) {
		console.warn('Mini-map init failed:', err);
	}

	function refreshMarkers() {
		if (!map || !markers) return;
		markers.clearLayers();
		// ưu tiên các phần tử đã chọn và đang hiển thị; nếu không có, hiển thị tất cả phần tử đang hiển thị
		const selectedCbs = Array.from(document.querySelectorAll('.select-diem:checked'))
			.filter(cb => {
				const it = cb.closest('.diem-item');
				return isVisibleItem(it);
			});
		let items = [];
		if (selectedCbs.length > 0) {
			items = selectedCbs.map(cb => cb.closest('.diem-item'));
		} else {
			items = Array.from(document.querySelectorAll('.diem-item')).filter(it => isVisibleItem(it));
		}
		const bounds = [];
		items.forEach(it => {
			const lat = parseFloat(it.dataset.lat || '');
			const lng = parseFloat(it.dataset.lng || '');
			const name = (it.querySelector('label') || {}).textContent || '';
			const img = (it.dataset.image || '').trim();
			if (!isNaN(lat) && !isNaN(lng)) {
				let marker;
				if (img) {
					// dùng hình ảnh làm icon marker
					const icon = L.icon({
						iconUrl: img,
						iconSize: [44, 44],
						iconAnchor: [22, 44],
						popupAnchor: [0, -44],
						className: 'diem-image-icon'
					});
					marker = L.marker([lat, lng], {icon: icon});
				} else {
					marker = L.marker([lat, lng]);
				}

				// popup hiển thị thumbnail chứa hình ảnh
				const popupContent = img ? `<div class="fw-semibold mb-1">${name}</div><img class="diem-popup-img" src="${img}" alt="${name}">` : `<div class="fw-semibold">${name}</div>`;
				marker.bindPopup(popupContent);
				markers.addLayer(marker);
				bounds.push([lat, lng]);
			}
		});
		if (bounds.length > 0) {
			map.fitBounds(bounds, {padding: [40, 40]});
		} else {
			// trả về view mặc định
			map.setView([10.7769, 106.70098], 12);
		}

		// vẽ tuyến đường
		if (selectedCbs.length > 0) {
			computeAndDrawRoute(selectedCbs.map(cb => cb.closest('.diem-item')));
		} else {
			// xóa tuyến đường hiện có nếu không có điểm nào được chọn
			if (routeLayer) {
				routeLayer.remove();
				routeLayer = null;
			}
		}
	}

	// tính toán tuyến dùng OSRM (dự phòng GraphHopper nếu cần)
	async function computeAndDrawRoute(items) {
		if (!map) return;
		if (!items || items.length < 2) {
			// cần ít nhất 2 điểm để vẽ tuyến
			if (routeLayer) { routeLayer.remove(); routeLayer = null; }
			return;
		}

		// xây dựng danh sách toạ độ: OSRM (lon,lat); GraphHopper dùng lat,lon trong tham số point
		const coords = [];
		items.forEach(it => {
			const lat = parseFloat(it.dataset.lat || '');
			const lng = parseFloat(it.dataset.lng || '');
			if (!isNaN(lat) && !isNaN(lng)) coords.push({lat: lat, lng: lng});
		});
		if (coords.length < 2) return;

		// thử server public OSRM trước
		const osrmCoordStr = coords.map(c => `${c.lng},${c.lat}`).join(';');
		const osrmUrl = `https://router.project-osrm.org/route/v1/driving/${osrmCoordStr}?overview=full&geometries=geojson`;
		try {
			const resp = await fetch(osrmUrl);
			if (!resp.ok) throw new Error('OSRM request failed: ' + resp.status);
			const data = await resp.json();
			if (data && data.routes && data.routes.length > 0) {
				const route = data.routes[0];
				const geo = route.geometry; // GeoJSON LineString
				// loại bỏ route cũ
				if (routeLayer) { routeLayer.remove(); routeLayer = null; }
				routeLayer = L.geoJSON(geo, { style: { color: '#eb3434', weight: 4, opacity: 0.9}}).addTo(map);
				// phóng to bản đồ tới tuyến
				const routeBounds = routeLayer.getBounds();
				if (routeBounds.isValid()) map.fitBounds(routeBounds.pad(0.1));
				// hiển thị khoảng cách/thời gian trong popup nhỏ trên layer
				const distanceKm = (route.distance / 1000).toFixed(1);
				const durationMin = Math.round(route.duration / 60);
				routeLayer.bindPopup(`<div class="fw-semibold">Lộ trình</div><div>${distanceKm} km · ${durationMin} phút</div>`);
				return;
			}
		} catch (err) {
			console.warn('OSRM routing failed, will try GraphHopper if configured:', err);
		}

		// dự phòng sang GraphHopper nếu có API key
		const ghKey = window.GH_API_KEY || (document.body && document.body.dataset && document.body.dataset.ghApiKey);
		if (ghKey) {
			try {
				const params = new URLSearchParams();
				coords.forEach(c => params.append('point', `${c.lat},${c.lng}`));
				params.set('vehicle', 'car');
				params.set('points_encoded', 'false');
				params.set('key', ghKey);
				const ghUrl = `https://graphhopper.com/api/1/route?${params.toString()}`;
				const resp = await fetch(ghUrl);
				if (!resp.ok) throw new Error('GraphHopper request failed: ' + resp.status);
				const data = await resp.json();
				if (data && data.paths && data.paths.length > 0) {
					const path = data.paths[0];
					// path.points.coordinates là arr [lon,lat] (GeoJSON)
					const coordsArr = (path.points && path.points.coordinates) || [];
					const geojson = {
						type: 'LineString',
						coordinates: coordsArr
					};
					if (routeLayer) { routeLayer.remove(); routeLayer = null; }
					routeLayer = L.geoJSON(geojson, { style: { color: '#eb3434', weight: 4, opacity: 0.9}}).addTo(map);
					const routeBounds = routeLayer.getBounds();
					if (routeBounds.isValid()) map.fitBounds(routeBounds.pad(0.1));
					const distanceKm = path.distance ? (path.distance / 1000).toFixed(1) : '';
					const durationMin = path.time ? Math.round(path.time / 60000) : '';
					routeLayer.bindPopup(`<div class="fw-semibold">Lộ trình (GraphHopper)</div><div>${distanceKm} km · ${durationMin} phút</div>`);
					return;
				}
			} catch (err) {
				console.warn('GraphHopper routing failed:', err);
			}
		}

		// nếu đến đây, không có routing
		if (routeLayer) { routeLayer.remove(); routeLayer = null; }
		console.warn('Routing failed: no route drawn (OSRM and GraphHopper unavailable)');
	}

	// gán nút tối ưu để
	if (optimizeBtn) {
		optimizeBtn.addEventListener('click', function (e) {
			e.preventDefault();
			const selectedCbs = Array.from(document.querySelectorAll('.select-diem:checked'))
				.filter(cb => cb.closest('.diem-item') && isVisibleItem(cb.closest('.diem-item')));
			if (selectedCbs.length < 2) {
				alert('Vui lòng chọn ít nhất 2 điểm để vẽ tuyến đường.');
				return;
			}
			const items = selectedCbs.map(cb => cb.closest('.diem-item'));
			computeAndDrawRoute(items);
		});
	}

	window.refreshMarkers = refreshMarkers;
});
