const API_BASE = '/api';

function showToast(message, type = 'success') {
  const toast = document.getElementById('toast');
  toast.textContent = message;
  toast.className = `toast show ${type === 'error' ? 'toast-error' : ''}`;
  setTimeout(() => { toast.className = 'toast'; }, 3200);
}

async function apiRequest(url, method = 'GET', body = null) {
  const options = { method, headers: {} };
  if (body !== null) {
    options.headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(body);
  }
  const response = await fetch(url, options);
  let data = null;
  try {
    data = await response.json();
  } catch (e) {
    data = null;
  }
  if (!response.ok) {
    let message = 'Something went wrong. Please try again.';
    if (data) {
      if (data.detail) {
        message = data.detail;
      } else {
        const firstKey = Object.keys(data)[0];
        if (firstKey) {
          const value = data[firstKey];
          message = Array.isArray(value) ? value[0] : value;
        }
      }
    }
    throw new Error(message);
  }
  return data;
}

function formatDate(dateStr) {
  if (!dateStr) return '-';
  const d = new Date(dateStr + 'T00:00:00');
  return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}

function statusBadge(status) {
  const map = { ISSUED: 'badge-orange', OVERDUE: 'badge-red', RETURNED: 'badge-green' };
  return `<span class="badge ${map[status] || 'badge-gray'}">${status}</span>`;
}

function debounce(fn, delay) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

function escapeHtml(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
