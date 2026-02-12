<template>
  <div class="staff-page">
    <div class="staff-header">
      <h2>User Management</h2>
      <button class="btn btn-primary" @click="showAdd = true">Add Staff</button>
    </div>

    <!-- Add Staff Form -->
    <div v-if="showAdd" class="add-form">
      <input v-model="newEmail" type="email" placeholder="Email address" class="form-input" />
      <select v-model="newRole" class="form-select">
        <option value="" disabled>Select role</option>
        <option value="admin">Admin</option>
        <option value="faculty">Faculty</option>
      </select>
      <div class="add-actions">
        <button class="btn btn-primary" :disabled="!newEmail || !newRole || adding" @click="handleAdd">
          {{ adding ? 'Adding...' : 'Add' }}
        </button>
        <button class="btn btn-secondary" @click="cancelAdd">Cancel</button>
      </div>
      <p v-if="addError" class="error-msg">{{ addError }}</p>
    </div>

    <!-- Staff Table -->
    <div class="table-container">
      <div v-if="loading" class="loading">Loading staff...</div>
      <table v-else-if="staff.length" class="data-table">
        <thead>
          <tr>
            <th>Email</th>
            <th>Role</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="member in staff" :key="member.id">
            <td>{{ member.email }}</td>
            <td>
              <select
                :value="member.role"
                class="role-select"
                @change="handleRoleChange(member, $event.target.value)"
              >
                <option value="admin">Admin</option>
                <option value="faculty">Faculty</option>
              </select>
            </td>
            <td>
              <button
                class="btn btn-danger btn-sm"
                :disabled="member.email === currentEmail"
                @click="handleRemove(member)"
              >
                Remove
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else class="empty">No staff members found</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getStaff, addStaff, updateStaffRole, removeStaff } from '../services/api'

const staff = ref([])
const loading = ref(false)
const showAdd = ref(false)
const newEmail = ref('')
const newRole = ref('')
const adding = ref(false)
const addError = ref('')
const currentEmail = localStorage.getItem('admin_email') || ''

async function loadStaff() {
  loading.value = true
  try {
    staff.value = await getStaff()
  } catch (err) {
    console.error('Failed to load staff:', err)
  } finally {
    loading.value = false
  }
}

function cancelAdd() {
  showAdd.value = false
  newEmail.value = ''
  newRole.value = ''
  addError.value = ''
}

async function handleAdd() {
  if (!newEmail.value || !newRole.value) return
  adding.value = true
  addError.value = ''
  try {
    await addStaff(newEmail.value, newRole.value)
    cancelAdd()
    await loadStaff()
  } catch (err) {
    addError.value = err.response?.data?.detail || 'Failed to add staff member'
  } finally {
    adding.value = false
  }
}

async function handleRoleChange(member, newRole) {
  try {
    await updateStaffRole(member.email, newRole)
    member.role = newRole
  } catch (err) {
    console.error('Failed to update role:', err)
    await loadStaff()
  }
}

async function handleRemove(member) {
  if (!confirm(`Remove ${member.email}?`)) return
  try {
    await removeStaff(member.email)
    await loadStaff()
  } catch (err) {
    console.error('Failed to remove staff:', err)
    alert(err.response?.data?.detail || 'Failed to remove staff member')
  }
}

onMounted(loadStaff)
</script>

<style scoped>
.staff-page {
  max-width: 800px;
}

.staff-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.staff-header h2 {
  font-size: 1.25rem;
  color: #1a1a2e;
}

.add-form {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1.25rem;
  margin-bottom: 1.5rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: flex-start;
}

.form-input,
.form-select {
  padding: 0.6rem 0.75rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.9rem;
  outline: none;
}

.form-input {
  flex: 1;
  min-width: 200px;
}

.form-input:focus,
.form-select:focus {
  border-color: #1a5fa4;
}

.form-select {
  min-width: 140px;
}

.add-actions {
  display: flex;
  gap: 0.5rem;
}

.error-msg {
  width: 100%;
  color: #d32f2f;
  font-size: 0.85rem;
  margin: 0;
}

.table-container {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  background: #f8f9fa;
  padding: 0.75rem 1rem;
  text-align: left;
  font-size: 0.85rem;
  font-weight: 600;
  color: #555;
  border-bottom: 1px solid #e0e0e0;
}

.data-table td {
  padding: 0.75rem 1rem;
  font-size: 0.9rem;
  border-bottom: 1px solid #f0f0f0;
}

.role-select {
  padding: 0.35rem 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.85rem;
  cursor: pointer;
}

.loading,
.empty {
  padding: 2rem;
  text-align: center;
  color: #999;
  font-size: 0.9rem;
}

.btn {
  padding: 0.5rem 1.25rem;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-sm {
  padding: 0.3rem 0.75rem;
  font-size: 0.8rem;
}

.btn-primary {
  background: #1a5fa4;
  color: white;
}

.btn-primary:hover {
  background: #154d87;
}

.btn-primary:disabled {
  background: #8cb3d9;
  cursor: not-allowed;
}

.btn-secondary {
  background: #f0f0f0;
  color: #333;
}

.btn-secondary:hover {
  background: #e0e0e0;
}

.btn-danger {
  background: #e74c3c;
  color: white;
}

.btn-danger:hover {
  background: #c0392b;
}

.btn-danger:disabled {
  background: #f0a8a1;
  cursor: not-allowed;
}
</style>
