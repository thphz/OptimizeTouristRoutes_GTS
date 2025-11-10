
document.addEventListener('DOMContentLoaded', function () {
	const filterQuan = document.getElementById('filter-quan');
	const filterLoai = document.getElementById('filter-loai');
	const diemItems = Array.from(document.querySelectorAll('.diem-item'));
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
		diemItems.forEach(item => {
			const qi = item.dataset.quanId || '';
			const li = item.dataset.loaiId || '';
			const showQ = !q || (qi + '') === (q + '');
			const showL = !l || (li + '') === (l + '');
			item.style.display = (showQ && showL) ? '' : 'none';
		});
	}

	function updateSummary() {
		const checked = Array.from(document.querySelectorAll('.select-diem:checked'));
		selectedCountEl.textContent = checked.length;

		let totalMinutes = 0;
		selectedList.innerHTML = '';
		checked.forEach((cb, idx) => {
			const item = cb.closest('.diem-item');
			const name = item.querySelector('label').textContent.trim();
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

		// Format time -> Hh Mm
		const hours = Math.floor(totalMinutes / 60);
		const mins = totalMinutes % 60;
		totalTimeEl.textContent = `${hours}h ${mins}m`;
		totalPointsEl.textContent = `${checked.length} địa điểm`;
	}

	// hooks khởi tạo
	if (filterQuan) filterQuan.addEventListener('change', filterDiems);
	if (filterLoai) filterLoai.addEventListener('change', filterDiems);
	document.querySelectorAll('.select-diem').forEach(cb => cb.addEventListener('change', updateSummary));

	// kiểm tra form
	if (form) {
		form.addEventListener('submit', function (e) {
			const checked = document.querySelectorAll('.select-diem:checked');
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
	});

	if (clearBtn) clearBtn.addEventListener('click', function () {
		document.querySelectorAll('.select-diem').forEach(cb => cb.checked = false);
		updateSummary();
	});

	filterDiems();
	updateSummary();
});
