async function loadDashboard() {
  try {
    const data = await apiRequest(`${API_BASE}/dashboard/`);

    document.getElementById('statTotalBooks').textContent = data.total_books;
    document.getElementById('statAvailable').textContent = data.available_copies;
    document.getElementById('statMembers').textContent = data.total_members;
    document.getElementById('statIssued').textContent = data.issued_count;
    document.getElementById('statOverdue').textContent = data.overdue_count;
    document.getElementById('statReturned').textContent = data.returned_count;

    const categoryList = document.getElementById('categoryList');
    if (data.category_counts && data.category_counts.length) {
      categoryList.innerHTML = data.category_counts.map(c => `
        <div class="category-item">
          <span class="category-name">${escapeHtml(c.category.replace('_', ' ').toLowerCase())}</span>
          <span class="category-count">${c.count}</span>
        </div>
      `).join('');
    } else {
      categoryList.innerHTML = '<p class="empty-state">No books added yet.</p>';
    }

    const recentBody = document.getElementById('recentTransactions');
    if (data.recent_transactions && data.recent_transactions.length) {
      recentBody.innerHTML = data.recent_transactions.map(t => `
        <tr>
          <td>${escapeHtml(t.book__title)}</td>
          <td>${escapeHtml(t.member__name)}</td>
          <td>${formatDate(t.issue_date)}</td>
          <td>${formatDate(t.due_date)}</td>
          <td>${statusBadge(t.status)}</td>
        </tr>
      `).join('');
    } else {
      recentBody.innerHTML = '<tr><td colspan="5" class="empty-state">No transactions yet.</td></tr>';
    }
  } catch (err) {
    showToast(err.message, 'error');
  }
}

loadDashboard();
