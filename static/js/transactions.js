async function loadFormOptions() {
  try {
    const [booksData, membersData] = await Promise.all([
      apiRequest(`${API_BASE}/books/`),
      apiRequest(`${API_BASE}/members/`),
    ]);
    const books = (booksData.results || booksData).filter(b => b.available_copies > 0);
    const members = (membersData.results || membersData).filter(m => m.is_active);

    const bookSelect = document.getElementById('issueBook');
    const memberSelect = document.getElementById('issueMember');

    bookSelect.innerHTML = books.length
      ? books.map(b => `<option value="${b.id}">${escapeHtml(b.title)} (${b.available_copies} available)</option>`).join('')
      : '<option value="">No books available right now</option>';

    memberSelect.innerHTML = members.length
      ? members.map(m => `<option value="${m.id}">${escapeHtml(m.name)}</option>`).join('')
      : '<option value="">No active members</option>';
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function loadTransactions() {
  const statusFilter = document.getElementById('statusFilter').value;
  const params = new URLSearchParams();
  if (statusFilter) params.append('status', statusFilter);

  try {
    const data = await apiRequest(`${API_BASE}/transactions/?${params.toString()}`);
    const transactions = data.results || data;
    const tbody = document.getElementById('transactionsTableBody');

    if (transactions.length) {
      tbody.innerHTML = transactions.map(t => `
        <tr>
          <td>${escapeHtml(t.book_title)}</td>
          <td>${escapeHtml(t.member_name)}</td>
          <td>${formatDate(t.issue_date)}</td>
          <td>${formatDate(t.due_date)}</td>
          <td>${formatDate(t.return_date)}</td>
          <td>${statusBadge(t.status)}</td>
          <td>${Number(t.fine_amount).toFixed(2)}</td>
          <td>${t.status !== 'RETURNED' ? `<button class="btn btn-small btn-primary" onclick="returnBook(${t.id})">Return</button>` : '-'}</td>
        </tr>
      `).join('');
    } else {
      tbody.innerHTML = '<tr><td colspan="8" class="empty-state">No transactions found.</td></tr>';
    }
  } catch (err) {
    showToast(err.message, 'error');
  }
}

document.getElementById('issueForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const book = document.getElementById('issueBook').value;
  const member = document.getElementById('issueMember').value;
  const errorEl = document.getElementById('issueFormError');
  errorEl.textContent = '';

  if (!book || !member) {
    errorEl.textContent = 'Please select both a book and a member.';
    return;
  }

  try {
    await apiRequest(`${API_BASE}/transactions/`, 'POST', { book, member });
    showToast('Book issued successfully.');
    loadFormOptions();
    loadTransactions();
  } catch (err) {
    errorEl.textContent = err.message;
  }
});

async function returnBook(id) {
  if (!confirm('Confirm that this book has been returned?')) return;
  try {
    await apiRequest(`${API_BASE}/transactions/${id}/return_book/`, 'POST');
    showToast('Book returned successfully.');
    loadFormOptions();
    loadTransactions();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

document.getElementById('statusFilter').addEventListener('change', loadTransactions);

loadFormOptions();
loadTransactions();
