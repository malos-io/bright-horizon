<template>
  <div class="page">
    <div class="page-header">
      <h2>Instructor Applications</h2>
      <div class="header-actions">
        <select v-model="statusFilter" class="filter-select">
          <option value="">All Statuses</option>
          <option value="new">New</option>
          <option value="reviewed">Reviewed</option>
          <option value="contacted">Contacted</option>
          <option value="archived">Archived</option>
        </select>
        <div class="search-box">
          <input
            v-model="search"
            type="text"
            placeholder="Search applications..."
            class="search-input"
          />
        </div>
        <button class="btn-refresh" @click="loadApplications">Refresh</button>
      </div>
    </div>

    <div v-if="loading" class="loading-state">Loading applications...</div>

    <div v-else-if="filtered.length" class="list">
      <div
        class="card"
        v-for="app in filtered"
        :key="app.id"
        @click="router.push('/instructor-applications/' + app.id)"
      >
        <div class="card-avatar">
          {{ getInitials(app) }}
        </div>
        <div class="card-info">
          <div class="card-name">{{ app.lastName }}, {{ app.firstName }}</div>
          <div class="card-email">{{ app.email }}</div>
          <div class="card-courses">
            <span class="course-tag" v-for="c in app.coursesInterested" :key="c">{{ c }}</span>
            <span class="course-tag other" v-if="app.otherCourses">+ Other</span>
          </div>
        </div>
        <div class="card-meta">
          <span :class="['status-badge', 'status-' + app.status]">{{ formatStatus(app.status) }}</span>
          <span class="meta-date">{{ formatDate(app.created_at) }}</span>
        </div>
        <span class="card-arrow">&#8594;</span>
      </div>
    </div>

    <div v-else-if="search || statusFilter" class="empty-state">No applications matching your filters</div>
    <div v-else class="empty-state">No instructor applications yet</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getInstructorApplications } from '../services/api'

const router = useRouter()
const applications = ref([])
const loading = ref(false)
const search = ref('')
const statusFilter = ref('')

const filtered = computed(() => {
  let list = applications.value
  if (statusFilter.value) {
    list = list.filter(a => a.status === statusFilter.value)
  }
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    list = list.filter(a =>
      `${a.firstName} ${a.lastName} ${a.email} ${(a.coursesInterested || []).join(' ')}`.toLowerCase().includes(q)
    )
  }
  return list
})

function getInitials(app) {
  const first = (app.firstName || '')[0] || ''
  const last = (app.lastName || '')[0] || ''
  return (first + last).toUpperCase() || '?'
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

function formatStatus(status) {
  const map = { new: 'New', reviewed: 'Reviewed', contacted: 'Contacted', archived: 'Archived' }
  return map[status] || status
}

async function loadApplications() {
  loading.value = true
  try {
    applications.value = await getInstructorApplications()
  } catch (err) {
    console.error('Failed to load instructor applications:', err)
  } finally {
    loading.value = false
  }
}

onMounted(loadApplications)
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
  width: 200px;
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
  background: #fff3e0;
  color: #e88a1a;
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

.card-courses {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 6px;
}

.course-tag {
  font-size: 0.7rem;
  padding: 2px 8px;
  background: #e8f0fe;
  color: #1a5fa4;
  border-radius: 4px;
  white-space: nowrap;
}

.course-tag.other {
  background: #fff3e0;
  color: #e88a1a;
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
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.status-new {
  background: #e3f2fd;
  color: #1565c0;
}

.status-reviewed {
  background: #fff3cd;
  color: #856404;
}

.status-contacted {
  background: #c8e6c9;
  color: #1b5e20;
}

.status-archived {
  background: #f0f0f0;
  color: #777;
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
