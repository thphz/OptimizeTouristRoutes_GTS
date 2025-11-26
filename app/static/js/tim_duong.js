document.addEventListener('DOMContentLoaded', function () {


    const startSelect = document.getElementById('start-point');
    const endSelect = document.getElementById('end-point');
    const findButton = document.getElementById('find-route-btn');

    const resultsPanel = document.getElementById('results-panel');
    const resultsPlaceholder = document.getElementById('results-placeholder');
    const resultsContent = document.getElementById('results-content');

    const routeTypeCards = document.querySelectorAll('.route-type-card');

    let selectedRouteType = 'fastest';

    loadLocations();

    routeTypeCards.forEach(card => {
        card.addEventListener('click', function () {
            const currentActive = document.querySelector('.route-type-card.active');
            if (currentActive) {
                currentActive.classList.remove('active');
            }

            this.classList.add('active');

            selectedRouteType = this.dataset.value;
        });
    });

    findButton.addEventListener('click', handleFindRoute);

    async function loadLocations() {
        try {
            const response = await fetch('/api/locations');
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

            const locations = await response.json();

            if (locations.error) throw new Error(locations.error);

            startSelect.innerHTML = '<option selected disabled value="">Chọn điểm xuất phát...</option>';
            endSelect.innerHTML = '<option selected disabled value="">Chọn điểm đến...</option>';

            locations.forEach(location => {
                const optionHtml = `<option value="${location.id}">${location.name}</option>`;
                startSelect.innerHTML += optionHtml;
                endSelect.innerHTML += optionHtml;
            });

        } catch (error) {
            console.error('Lỗi khi tải địa điểm:', error);
            resultsPanel.innerHTML = `<div class="alert alert-danger">Lỗi khi tải địa điểm: ${error.message}. Vui lòng kiểm tra kết nối DB và API.</div>`;
        }
    }

    async function handleFindRoute() {
        const startPointId = startSelect.value;
        const endPointId = endSelect.value;

        if (!startPointId || !endPointId) {
            alert('Vui lòng chọn cả điểm đi và điểm đến!');
            return;
        }

        resultsPlaceholder.classList.add('d-none');
        resultsContent.classList.remove('d-none');

        resultsContent.innerHTML = `
            <div class="d-flex justify-content-center align-items-center" style="min-height: 400px;">
                <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
                    <span class="visually-hidden">Đang tìm đường...</span>
                </div>
                <h5 class="ms-3 text-muted">Đang tìm đường...</h5>
            </div>
        `;

        try {
            const response = await fetch('/api/find-route', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    start: startPointId,
                    end: endPointId,
                    type: selectedRouteType
                })
            });

            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

            const routeData = await response.json();

            if (routeData.error) throw new Error(routeData.error);

            displayResults(routeData, selectedRouteType);

        } catch (error) {
            console.error('Lỗi khi tìm đường:', error);
            resultsContent.innerHTML = `<div class="alert alert-danger">Lỗi khi tìm đường: ${error.message}</div>`;
        }
    }

    function displayResults(data, type) {

        let stepsHtml = '';
        if (type !== 'scenic' && data.steps && data.steps.length > 0) {
            stepsHtml = data.steps.map((step, index) => `
                <div class="d-flex align-items-center p-2">
                    <span class="badge bg-primary rounded-pill me-3" style="width: 28px; height: 28px; display: inline-flex; align-items: center; justify-content: center;">${index + 1}</span>
                    <span>${step}</span>
                </div>
            `).join('');
        }

        let waypointsHtml = '';
        if (data.waypoints_timeline && data.waypoints_timeline.length > 0) {
            waypointsHtml = data.waypoints_timeline.map((point, index) => {
                let stepClass = 'timeline-step';
                let iconClass = 'bi-record-circle';
                let detailHtml = `<small class="text-muted">${point.detail || ''}</small>`;

                if (index === 0) {
                    stepClass += ' start';
                    iconClass = 'bi-circle-fill';
                    detailHtml = `<small class="text-success fw-bold">${point.detail || 'Xuất phát'}</small>`;
                } else if (index === data.waypoints_timeline.length - 1) {
                    stepClass += ' end';
                    iconClass = 'bi-geo-alt-fill';
                    detailHtml = `<small class="text-danger fw-bold">${point.detail || 'Đích đến'}</small>`;
                } else if (type === 'scenic') {
                    stepClass += ' middle';
                    iconClass = 'bi-record-circle-fill';
                }

                return `
                    <li class="${stepClass}">
                        <div class="icon"><i class="bi ${iconClass}"></i></div>
                        <div class="content">
                            <span class="name">${point.name}</span>
                            ${detailHtml}
                        </div>
                    </li>
                `;
            }).join('');
        }

        let finalHtml = `
            <div class="d-flex align-items-center mb-1">
                <i class="bi bi-check-circle-fill text-success me-2 fs-5"></i>
                <h5 class="card-title mb-0">Kết Quả Tìm Đường</h5>
            </div>
            <p class="card-subtitle mb-4 text-muted">Thông tin chi tiết về tuyến đường ${type} được đề xuất.</p>

            <!-- Hộp Khoảng cách & Thời gian -->
            <div class="row g-3 mb-4">
                <div class="col-6">
                    <div class="info-box blue">
                        <div class="d-flex">
                            <i class="bi bi-signpost-split-fill icon text-primary"></i>
                            <div>
                                <span class="label">Khoảng Cách</span>
                                <span class="value">${data.distance_km} km</span>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-6">
                    <div class="info-box green">
                        <div class="d-flex">
                            <i class="bi bi-clock-fill icon text-success"></i>
                            <div>
                                <span class="label">Thời Gian</span>
                                <span class="value">${data.duration_min} phút</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Tình trạng Giao thông -->
            <div class="card card-body bg-light border-0 mb-4">
                <strong class="d-block mb-1">
                    <i class="bi bi-cone-striped me-2"></i> Tình trạng giao thông
                </strong>
                <span class="text-muted">${data.traffic || 'Giao thông ổn định'}</span>
            </div>
        `;

        if (type !== 'scenic') {
            finalHtml += `
                <div class="mb-4">
                    <strong class="d-block mb-2">
                        <i class="bi bi-list-ol me-2"></i> Các Tuyến Đường
                    </strong>
                    <div class="card card-body bg-light border-0 vstack gap-2">
                        ${stepsHtml}
                    </div>
                </div>
            `;
        }

        finalHtml += `
            <div class="mb-4">
                <strong class="d-block mb-3">
                    <i class="bi bi-geo-alt-fill me-2"></i> Điểm Đi Qua
                </strong>
                <ul class="timeline-steps">
                    ${waypointsHtml}
                </ul>
            </div>
        `;

        finalHtml += `
            <hr>
            <div class="d-flex justify-content-end gap-2">
                <button id="view-on-map-btn" class="btn btn-outline-secondary">
                    <i class="bi bi-map me-2"></i> Xem Trên Bản Đồ
                </button>
                <button id="reset-route-btn" class="btn btn-primary">
                    <i class="bi bi-arrow-repeat me-2"></i> Tìm Lại
                </button>
            </div>
        `;

        resultsContent.innerHTML = finalHtml;

        resultsContent.querySelector('#reset-route-btn').addEventListener('click', () => {
            resultsContent.innerHTML = '';
            resultsContent.classList.add('d-none');
            resultsPlaceholder.classList.remove('d-none');

            startSelect.value = "";
            endSelect.value = "";
        });

        resultsContent.querySelector('#view-on-map-btn').addEventListener('click', () => {
            alert('Chức năng "Xem Trên Bản Đồ" (Tab 2) đang được phát triển!');
        });
    }

}); 