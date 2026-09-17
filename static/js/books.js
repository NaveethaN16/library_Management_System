async function loadBooks() {
  const search = document.getElementById('searchInput').value;
  const category = document.getElementById('categoryFilter').value;
  const params = new URLSearchParams();
  if (search) params.append('search', search);
  if (category) params.append('category', category);

  try {
    const data = await apiRequest(`${API_BASE}/books/?${params.toString()}`);
    const books = data.results || data;
    const tbody = document.getElementById('booksTableBody');

    if (books.length) {
      tbody.innerHTML = books.map(b => `
        <tr>
          <td>${escapeHtml(b.title)}</td>
          <td>${escapeHtml(b.author)}</td>
          <td>${escapeHtml(b.isbn)}</td>
          <td><span class="badge badge-blue">${escapeHtml(b.category.replace('_', ' '))}</span></td>
          <td>${b.total_copies}</td>
          <td>${b.available_copies}</td>
          <td class="actions">
            <button class="btn-icon" title="Edit" onclick='editBook(${JSON.stringify(b)})'>✏️</button>
            <button class="btn-icon" title="Delete" onclick="deleteBook(${b.id})">🗑️</button>
          </td>
        </tr>
      `).join('');
    } else {
      tbody.innerHTML = '<tr><td colspan="7" class="empty-state">No books found.</td></tr>';
    }
  } catch (err) {
    showToast(err.message, 'error');
  }
}

function openBookModal() {
  document.getElementById('bookModalTitle').textContent = 'Add New Book';
  document.getElementById('bookForm').reset();
  document.getElementById('bookId').value = '';
  document.getElementById('bookFormError').textContent = '';
  document.getElementById('bookModal').classList.remove('hidden');
}

function closeBookModal() {
  document.getElementById('bookModal').classList.add('hidden');
}

function editBook(book) {
  document.getElementById('bookModalTitle').textContent = 'Edit Book';
  document.getElementById('bookId').value = book.id;
  document.getElementById('bookTitle').value = book.title;
  document.getElementById('bookAuthor').value = book.author;
  document.getElementById('bookIsbn').value = book.isbn;
  document.getElementById('bookCategory').value = book.category;
  document.getElementById('bookPublisher').value = book.publisher || '';
  document.getElementById('bookYear').value = book.publish_year || '';
  document.getElementById('bookCopies').value = book.total_copies;
  document.getElementById('bookFormError').textContent = '';
  document.getElementById('bookModal').classList.remove('hidden');
}

async function deleteBook(id) {
  if (!confirm('Are you sure you want to delete this book?')) return;
  try {
    await apiRequest(`${API_BASE}/books/${id}/`, 'DELETE');
    showToast('Book deleted successfully.');
    loadBooks();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

document.getElementById('bookForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const id = document.getElementById('bookId').value;
  const payload = {
    title: document.getElementById('bookTitle').value.trim(),
    author: document.getElementById('bookAuthor').value.trim(),
    isbn: document.getElementById('bookIsbn').value.trim(),
    category: document.getElementById('bookCategory').value,
    publisher: document.getElementById('bookPublisher').value.trim(),
    publish_year: document.getElementById('bookYear').value || null,
    total_copies: parseInt(document.getElementById('bookCopies').value, 10),
  };

  try {
    if (id) {
      await apiRequest(`${API_BASE}/books/${id}/`, 'PUT', payload);
      showToast('Book updated successfully.');
    } else {
      await apiRequest(`${API_BASE}/books/`, 'POST', payload);
      showToast('Book added successfully.');
    }
    closeBookModal();
    loadBooks();
  } catch (err) {
    document.getElementById('bookFormError').textContent = err.message;
  }
});

document.getElementById('searchInput').addEventListener('input', debounce(loadBooks, 300));
document.getElementById('categoryFilter').addEventListener('change', loadBooks);

loadBooks();
