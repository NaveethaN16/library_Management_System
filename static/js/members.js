async function loadMembers() {
  const search = document.getElementById('searchInput').value;
  const params = new URLSearchParams();
  if (search) params.append('search', search);

  try {
    const data = await apiRequest(`${API_BASE}/members/?${params.toString()}`);
    const members = data.results || data;
    const tbody = document.getElementById('membersTableBody');

    if (members.length) {
      tbody.innerHTML = members.map(m => `
        <tr>
          <td>${escapeHtml(m.name)}</td>
          <td>${escapeHtml(m.email)}</td>
          <td>${escapeHtml(m.phone)}</td>
          <td>${formatDate(m.membership_date)}</td>
          <td>${m.is_active ? '<span class="badge badge-green">Active</span>' : '<span class="badge badge-red">Inactive</span>'}</td>
          <td class="actions">
            <button class="btn-icon" title="Edit" onclick='editMember(${JSON.stringify(m)})'>✏️</button>
            <button class="btn-icon" title="Delete" onclick="deleteMember(${m.id})">🗑️</button>
          </td>
        </tr>
      `).join('');
    } else {
      tbody.innerHTML = '<tr><td colspan="6" class="empty-state">No members found.</td></tr>';
    }
  } catch (err) {
    showToast(err.message, 'error');
  }
}

function openMemberModal() {
  document.getElementById('memberModalTitle').textContent = 'Add New Member';
  document.getElementById('memberForm').reset();
  document.getElementById('memberId').value = '';
  document.getElementById('memberActive').checked = true;
  document.getElementById('memberFormError').textContent = '';
  document.getElementById('memberModal').classList.remove('hidden');
}

function closeMemberModal() {
  document.getElementById('memberModal').classList.add('hidden');
}

function editMember(member) {
  document.getElementById('memberModalTitle').textContent = 'Edit Member';
  document.getElementById('memberId').value = member.id;
  document.getElementById('memberName').value = member.name;
  document.getElementById('memberEmail').value = member.email;
  document.getElementById('memberPhone').value = member.phone;
  document.getElementById('memberAddress').value = member.address || '';
  document.getElementById('memberActive').checked = member.is_active;
  document.getElementById('memberFormError').textContent = '';
  document.getElementById('memberModal').classList.remove('hidden');
}

async function deleteMember(id) {
  if (!confirm('Are you sure you want to delete this member?')) return;
  try {
    await apiRequest(`${API_BASE}/members/${id}/`, 'DELETE');
    showToast('Member deleted successfully.');
    loadMembers();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

document.getElementById('memberForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const id = document.getElementById('memberId').value;
  const payload = {
    name: document.getElementById('memberName').value.trim(),
    email: document.getElementById('memberEmail').value.trim(),
    phone: document.getElementById('memberPhone').value.trim(),
    address: document.getElementById('memberAddress').value.trim(),
    is_active: document.getElementById('memberActive').checked,
  };

  try {
    if (id) {
      await apiRequest(`${API_BASE}/members/${id}/`, 'PUT', payload);
      showToast('Member updated successfully.');
    } else {
      await apiRequest(`${API_BASE}/members/`, 'POST', payload);
      showToast('Member added successfully.');
    }
    closeMemberModal();
    loadMembers();
  } catch (err) {
    document.getElementById('memberFormError').textContent = err.message;
  }
});

document.getElementById('searchInput').addEventListener('input', debounce(loadMembers, 300));

loadMembers();
