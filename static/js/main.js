// CSRF token setup for AJAX requests
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// AJAX request helper
async function makeRequest(url, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json'
        },
        credentials: 'same-origin'
    };

    if (data && method !== 'GET') {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(url, options);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

// Toast notification
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast show bg-${type} text-white`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="toast-header bg-${type} text-white">
            <strong class="me-auto">Bildirim</strong>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;
    
    document.body.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

// Form validation helper
function validateForm(form) {
    const inputs = form.querySelectorAll('input, select, textarea');
    let isValid = true;
    
    inputs.forEach(input => {
        if (input.hasAttribute('required') && !input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// DataTable initialization helper
function initDataTable(tableId, options = {}) {
    const defaultOptions = {
        language: {
            url: '//cdn.datatables.net/plug-ins/1.13.7/i18n/tr.json'
        },
        pageLength: 10,
        responsive: true,
        dom: '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6"f>>' +
             '<"row"<"col-sm-12"tr>>' +
             '<"row"<"col-sm-12 col-md-5"i><"col-sm-12 col-md-7"p>>',
        ...options
    };
    
    return new DataTable(`#${tableId}`, defaultOptions);
}

// Part production helper
async function producePart(teamId, partId, quantity) {
    try {
        const data = {
            team_id: teamId,
            part_id: partId,
            quantity: quantity
        };
        
        const response = await makeRequest('/api/teams/produce_part/', 'POST', data);
        showToast('Parça üretimi başarıyla tamamlandı.', 'success');
        return response;
    } catch (error) {
        showToast('Parça üretimi sırasında bir hata oluştu.', 'danger');
        throw error;
    }
}

// Aircraft part addition helper
async function addPartToAircraft(aircraftId, partId) {
    try {
        const data = {
            aircraft_id: aircraftId,
            part_id: partId
        };
        
        const response = await makeRequest('/api/aircraft/add_part/', 'POST', data);
        showToast('Parça başarıyla eklendi.', 'success');
        return response;
    } catch (error) {
        showToast('Parça eklenirken bir hata oluştu.', 'danger');
        throw error;
    }
}

// Aircraft completion helper
async function completeAircraft(aircraftId) {
    try {
        const response = await makeRequest(`/api/aircraft/${aircraftId}/complete_production/`, 'POST');
        showToast('Uçak üretimi başarıyla tamamlandı.', 'success');
        return response;
    } catch (error) {
        showToast('Uçak üretimi tamamlanırken bir hata oluştu.', 'danger');
        throw error;
    }
}

// Team member management helper
async function addTeamMember(teamId, userId) {
    try {
        const data = {
            user_id: userId
        };
        
        const response = await makeRequest(`/api/teams/${teamId}/add_member/`, 'POST', data);
        showToast('Takım üyesi başarıyla eklendi.', 'success');
        return response;
    } catch (error) {
        showToast('Takım üyesi eklenirken bir hata oluştu.', 'danger');
        throw error;
    }
}

// Stock check helper
function checkLowStock(currentStock, minStock) {
    return currentStock <= minStock;
}

// Progress calculation helper
function calculateProgress(current, total) {
    return Math.round((current / total) * 100);
}

// Document ready handler
document.addEventListener('DOMContentLoaded', () => {
    // Initialize all tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize all popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}); 