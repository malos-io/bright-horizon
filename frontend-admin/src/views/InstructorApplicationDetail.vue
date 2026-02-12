<template>
  <div class="detail-page">
    <div v-if="loading" class="loading-state">Loading application...</div>

    <template v-else-if="app">
      <!-- Header -->
      <div class="detail-header">
        <button class="btn-back" @click="router.push('/instructor-applications')">&larr; Back</button>
        <h2>{{ app.firstName }} {{ app.lastName }}</h2>
      </div>

      <!-- Summary Card -->
      <div class="summary-card">
        <div class="summary-row">
          <div class="summary-item">
            <span class="summary-label">Name</span>
            <span class="summary-value">{{ app.firstName }} {{ app.lastName }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">Email</span>
            <span class="summary-value">{{ app.email }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">Contact</span>
            <span class="summary-value">{{ app.contactNo }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">Submitted</span>
            <span class="summary-value">{{ formatDate(app.created_at) }}</span>
          </div>
        </div>
      </div>

      <!-- Courses Interested -->
      <div class="section">
        <h3>Courses Interested to Teach</h3>
        <div class="courses-list">
          <span class="course-tag" v-for="c in app.coursesInterested" :key="c">{{ c }}</span>
          <span class="course-tag other" v-if="app.otherCourses">Other: {{ app.otherCourses }}</span>
        </div>
        <p v-if="!app.coursesInterested?.length && !app.otherCourses" class="no-data">No courses specified</p>
      </div>

      <!-- Status Management -->
      <div class="section">
        <h3>Status</h3>
        <div class="status-row">
          <select v-model="newStatus" class="status-select">
            <option value="new">New</option>
            <option value="reviewed">Reviewed</option>
            <option value="contacted">Contacted</option>
            <option value="archived">Archived</option>
          </select>
          <button
            class="btn-save"
            :disabled="newStatus === app.status || saving"
            @click="handleStatusUpdate"
          >
            {{ saving ? 'Saving...' : 'Update Status' }}
          </button>
        </div>
      </div>

      <!-- Notes -->
      <div class="section">
        <h3>Admin Notes</h3>
        <textarea
          v-model="notes"
          rows="4"
          placeholder="Add internal notes about this applicant..."
          class="notes-input"
        ></textarea>
        <button
          class="btn-save"
          :disabled="notes === (app.notes || '') || savingNotes"
          @click="handleSaveNotes"
        >
          {{ savingNotes ? 'Saving...' : 'Save Notes' }}
        </button>
      </div>

      <!-- Changelog -->
      <div class="section" v-if="app.changelog?.length">
        <h3>Changelog</h3>
        <table class="changelog-table">
          <thead>
            <tr>
              <th>Field</th>
              <th>Old Value</th>
              <th>New Value</th>
              <th>Updated By</th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(entry, i) in [...app.changelog].reverse()" :key="i">
              <td>{{ entry.field }}</td>
              <td>{{ entry.oldValue || '--' }}</td>
              <td>{{ entry.newValue || '--' }}</td>
              <td>{{ entry.updatedBy }}</td>
              <td>{{ formatDate(entry.updatedAt) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Danger Zone -->
      <div class="section danger-zone">
        <h3>Danger Zone</h3>
        <div class="danger-content">
          <p>Permanently delete this instructor application. This action cannot be undone.</p>
          <button class="btn-delete" @click="handleDelete" :disabled="deleting">
            {{ deleting ? 'Deleting...' : 'Delete Application' }}
          </button>
        </div>
      </div>
    </template>

    <div v-else class="empty-state">Application not found</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getInstructorApplication, updateInstructorApplication, deleteInstructorApplication } from '../services/api'

const router = useRouter()
const route = useRoute()

const app = ref(null)
const loading = ref(true)
const newStatus = ref('')
const notes = ref('')
const saving = ref(false)
const savingNotes = ref(false)
const deleting = ref(false)

function formatDate(dateStr) {
  if (!dateStr) return '--'
  const d = new Date(dateStr)
  if (isNaN(d)) return '--'
  return d.toLocaleDateString('en-PH', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

async function loadApplication() {
  loading.value = true
  try {
    const data = await getInstructorApplication(route.params.id)
    app.value = data
    newStatus.value = data.status || 'new'
    notes.value = data.notes || ''
  } catch (err) {
    console.error('Failed to load application:', err)
  } finally {
    loading.value = false
  }
}

async function handleStatusUpdate() {
  if (newStatus.value === app.value.status) return
  saving.value = true
  try {
    await updateInstructorApplication(app.value.id, { status: newStatus.value })
    await loadApplication()
  } catch (err) {
    alert('Failed to update status: ' + (err.response?.data?.detail || err.message))
  } finally {
    saving.value = false
  }
}

async function handleSaveNotes() {
  savingNotes.value = true
  try {
    await updateInstructorApplication(app.value.id, { notes: notes.value })
    await loadApplication()
  } catch (err) {
    alert('Failed to save notes: ' + (err.response?.data?.detail || err.message))
  } finally {
    savingNotes.value = false
  }
}

async function handleDelete() {
  if (!confirm('Are you sure you want to permanently delete this application?')) return
  deleting.value = true
  try {
    await deleteInstructorApplication(app.value.id)
    router.push('/instructor-applications')
  } catch (err) {
    alert('Failed to delete: ' + (err.response?.data?.detail || err.message))
    deleting.value = false
  }
}

onMounted(loadApplication)
</script>

<style scoped>
.detail-page {
  max-width: 800px;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.btn-back {
  padding: 0.4rem 0.75rem;
  font-size: 0.85rem;
  color: #1a5fa4;
  background: #e8f0fe;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-back:hover {
  background: #d0e2fc;
}

.detail-header h2 {
  font-size: 1.25rem;
  color: #1a1a2e;
}

.summary-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  margin-bottom: 1.5rem;
}

.summary-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
}

.summary-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  display: block;
  margin-bottom: 0.25rem;
}

.summary-value {
  font-size: 0.95rem;
  color: #1a1a2e;
  font-weight: 500;
}

.section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  margin-bottom: 1.5rem;
}

.section h3 {
  font-size: 1rem;
  color: #1a1a2e;
  margin: 0 0 1rem;
}

.courses-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.course-tag {
  font-size: 0.85rem;
  padding: 6px 14px;
  background: #e8f0fe;
  color: #1a5fa4;
  border-radius: 6px;
  font-weight: 500;
}

.course-tag.other {
  background: #fff3e0;
  color: #e88a1a;
}

.no-data {
  color: #999;
  font-size: 0.9rem;
}

.status-row {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.status-select {
  padding: 0.5rem 0.75rem;
  font-size: 0.9rem;
  border: 1.5px solid #ddd;
  border-radius: 8px;
  outline: none;
  background: #fff;
  cursor: pointer;
  min-width: 160px;
}

.status-select:focus {
  border-color: #1a5fa4;
}

.btn-save {
  padding: 0.5rem 1.25rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: white;
  background: linear-gradient(135deg, #0d3b6e 0%, #1a5fa4 100%);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn-save:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-save:hover:not(:disabled) {
  box-shadow: 0 4px 12px rgba(26, 95, 164, 0.3);
}

.notes-input {
  width: 100%;
  padding: 0.75rem;
  font-size: 0.9rem;
  font-family: inherit;
  border: 1.5px solid #ddd;
  border-radius: 8px;
  resize: vertical;
  outline: none;
  margin-bottom: 0.75rem;
  box-sizing: border-box;
}

.notes-input:focus {
  border-color: #1a5fa4;
  box-shadow: 0 0 0 3px rgba(26, 95, 164, 0.1);
}

.changelog-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8rem;
}

.changelog-table th {
  text-align: left;
  padding: 0.5rem 0.75rem;
  background: #f8f9fb;
  color: #888;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.7rem;
  letter-spacing: 0.04em;
}

.changelog-table td {
  padding: 0.5rem 0.75rem;
  border-top: 1px solid #f0f0f0;
  color: #444;
}

.changelog-table tr:hover td {
  background: #f8f9ff;
}

.danger-zone {
  border: 1px solid #f8d7da;
}

.danger-zone h3 {
  color: #c0392b;
}

.danger-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.danger-content p {
  color: #666;
  font-size: 0.85rem;
  margin: 0;
}

.btn-delete {
  padding: 0.5rem 1.25rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: white;
  background: #c0392b;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.2s;
}

.btn-delete:hover:not(:disabled) {
  background: #a93226;
}

.btn-delete:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading-state,
.empty-state {
  text-align: center;
  color: #999;
  padding: 3rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  font-size: 0.9rem;
}

@media (max-width: 600px) {
  .summary-row {
    grid-template-columns: 1fr;
  }
  .danger-content {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
