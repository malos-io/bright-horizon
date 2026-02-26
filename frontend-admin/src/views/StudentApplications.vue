<template>
  <div class="page">
    <div class="page-header">
      <h2>Student Applications</h2>
      <div class="header-actions">
        <select v-model="statusFilter" class="filter-select">
          <option value="">All Statuses</option>
          <option value="pending_upload">Pending Upload</option>
          <option value="pending_review">Pending Review</option>
          <option value="documents_rejected">Docs Rejected</option>
          <option value="in_waitlist">In Waitlist</option>
          <option value="physical_docs_required">Physical Docs Required</option>
          <option value="waiting_for_class_start">Waiting for Class</option>
          <option value="completed">Completed</option>
          <option value="archived">Archived</option>
          <option value="withdrawn">Withdrawn</option>
          <option value="cancelled">Cancelled</option>
        </select>
        <div class="search-box">
          <input
            v-model="search"
            type="text"
            placeholder="Search by name, email, course..."
            class="search-input"
          />
        </div>
        <button class="btn-refresh" @click="loadEnrollments">Refresh</button>
      </div>
    </div>

    <div v-if="loading" class="loading-state">Loading applications...</div>

    <div v-else-if="filtered.length" class="list">
      <div
        class="card"
        v-for="enrollment in filtered"
        :key="enrollment.id"
        @click="router.push('/application/' + enrollment.id)"
      >
        <div class="card-avatar">
          {{ getInitials(enrollment) }}
        </div>
        <div class="card-info">
          <div class="card-name">{{ enrollment.lastName }}, {{ enrollment.firstName }}</div>
          <div class="card-email">{{ enrollment.email }}</div>
          <div class="card-course">{{ enrollment.course }}</div>
        </div>
        <div class="card-meta">
          <span :class="['status-badge', 'status-' + enrollment.status]">{{ formatStatus(enrollment.status) }}</span>
          <span class="meta-days">{{ formatDaysInStatus(enrollment.days_in_status) }}</span>
          <span class="meta-date">{{ formatDate(enrollment.created_at) }}</span>
        </div>
        <span class="card-arrow">&#8594;</span>
      </div>
    </div>

    <div v-else-if="search || statusFilter" class="empty-state">No applications matching your filters</div>
    <div v-else class="empty-state">No student applications yet</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getEnrollments } from '../services/api'

const router = useRouter()
const enrollments = ref([])
const loading = ref(false)
const search = ref('')
const statusFilter = ref('')

const filtered = computed(() => {
  let list = enrollments.value
  if (statusFilter.value) {
    list = list.filter(e => e.status === statusFilter.value)
  }
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    list = list.filter(e =>
      `${e.firstName} ${e.lastName} ${e.email} ${e.course}`.toLowerCase().includes(q)
    )
  }
  return list
})

function getInitials(enrollment) {
  const first = (enrollment.firstName || '')[0] || ''
  const last = (enrollment.lastName || '')[0] || ''
  return (first + last).toUpperCase() || '?'
}

function formatStatus(status) {
  const map = {
    pending: 'Pending',
    pending_upload: 'Pending Upload',
    pending_review: 'Pending Review',
    documents_rejected: 'Docs Rejected',
    in_waitlist: 'In Waitlist',
    physical_docs_required: 'Physical Docs Required',
    waiting_for_class_start: 'Waiting for Class',
    completed: 'Completed',
    archived: 'Archived',
    withdrawn: 'Withdrawn',
    cancelled: 'Cancelled',
  }
  return map[status] || status
}

function formatDaysInStatus(days) {
  if (days == null) return ''
  if (days === 0) return 'Today'
  if (days === 1) return '1 day in status'
  return `${days} days in status`
}

function formatDate(dateStr) {
  if (!dateStr) return '--'
  const d = new Date(dateStr)
  if (isNaN(d)) return '--'
  return d.toLocaleDateString('en-PH', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

async function loadEnrollments() {
  loading.value = true
  try {
    enrollments.value = await getEnrollments()
  } catch (err) {
    console.error('Failed to load enrollments:', err)
  } finally {
    loading.value = false
  }
}

onMounted(loadEnrollments)
</script>

<style scoped>
.page {
  max-width: 900px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  gap: 1rem;
  flex-wrap: wrap;
}

.page-header h2 {
  font-size: 1.25rem;
  color: #1a1a2e;
  white-space: nowrap;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.filter-select {
  padding: 0.4rem 0.75rem;
  font-size: 0.85rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  outline: none;
  background: #fff;
  cursor: pointer;
}

.filter-select:focus {
  border-color: #1a5fa4;
}

.search-input {
  padding: 0.4rem 0.75rem;
  font-size: 0.85rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  outline: none;
  width: 220px;
  transition: border-color 0.2s;
}

.search-input:focus {
  border-color: #1a5fa4;
}

.btn-refresh {
  padding: 0.4rem 1rem;
  font-size: 0.8rem;
  font-weight: 600;
  color: #1a5fa4;
  background: #e8f0fe;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
  white-space: nowrap;
}

.btn-refresh:hover {
  background: #d0e2fc;
}

.list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.card {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: white;
  border-radius: 10px;
  padding: 1rem 1.25rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: box-shadow 0.2s, transform 0.15s;
}

.card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.card-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #e8f0fe;
  color: #1a5fa4;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  font-weight: 700;
  flex-shrink: 0;
}

.card-info {
  flex: 1;
  min-width: 0;
}

.card-name {
  font-size: 0.95rem;
  font-weight: 600;
  color: #1a1a2e;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-email {
  font-size: 0.8rem;
  color: #888;
  margin-top: 0.1rem;
}

.card-course {
  font-size: 0.8rem;
  color: #1a5fa4;
  font-weight: 500;
  margin-top: 0.2rem;
}

.card-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  flex-shrink: 0;
}

.status-badge {
  font-size: 0.7rem;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 20px;
  white-space: nowrap;
}

.status-pending,
.status-pending_upload {
  background: #fff3cd;
  color: #856404;
}

.status-pending_review {
  background: #e3f2fd;
  color: #1565c0;
}

.status-documents_rejected {
  background: #f8d7da;
  color: #721c24;
}

.status-in_waitlist {
  background: #d4edda;
  color: #155724;
}

.status-physical_docs_required {
  background: #e8f0fe;
  color: #1a5fa4;
}

.status-waiting_for_class_start {
  background: #fef3c7;
  color: #92400e;
}

.status-completed {
  background: #c8e6c9;
  color: #1b5e20;
}

.status-archived {
  background: #e0e0e0;
  color: #616161;
}

.status-withdrawn {
  background: #fef2f2;
  color: #991b1b;
}

.status-cancelled {
  background: #fefce8;
  color: #92400e;
}

.meta-days {
  font-size: 0.7rem;
  color: #b07800;
  font-weight: 500;
}

.meta-date {
  font-size: 0.75rem;
  color: #999;
}

.card-arrow {
  color: #ccc;
  font-size: 1.1rem;
  flex-shrink: 0;
  transition: color 0.2s, transform 0.2s;
}

.card:hover .card-arrow {
  color: #1a5fa4;
  transform: translateX(2px);
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
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .header-actions {
    width: 100%;
    flex-wrap: wrap;
  }
  .search-input {
    flex: 1;
  }
  .card {
    flex-wrap: wrap;
  }
  .card-meta {
    align-items: flex-start;
    margin-left: 56px;
  }
  .card-arrow {
    display: none;
  }
}
</style>
