<template>
  <div class="dashboard">
    <div class="welcome-card">
      <h2>Welcome, {{ auth.state.name || 'Student' }}!</h2>
      <p>Track your enrollment applications and manage your documents below.</p>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <h3>Total Applications</h3>
        <p class="stat-value">{{ applications.length }}</p>
      </div>
      <div class="stat-card">
        <h3>Pending</h3>
        <p class="stat-value">{{ pendingCount }}</p>
      </div>
      <div class="stat-card">
        <h3>Enrolled</h3>
        <p class="stat-value">{{ completedCount }}</p>
      </div>
    </div>

    <div class="section">
      <h2>My Applications</h2>
      <div v-if="applications.length" class="applications-list">
        <div
          class="app-card"
          v-for="app in applications"
          :key="app.id"
          @click="router.push(`/application/${app.id}`)"
        >
          <div class="app-left">
            <h3>{{ app.course }}</h3>
            <p class="app-meta">Applied {{ formatDate(app.created_at) }}</p>
          </div>
          <div class="app-right">
            <span class="status-badge" :class="'status-' + app.status">
              {{ formatStatus(app.status) }}
            </span>
            <span class="app-arrow">&#8594;</span>
          </div>
        </div>
      </div>
      <div v-else class="empty-state">
        No applications found for this email address.
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const auth = useAuth()

const applications = computed(() => auth.state.applications || [])
const pendingCount = computed(() =>
  applications.value.filter(a => a.status !== 'completed').length
)
const completedCount = computed(() =>
  applications.value.filter(a => a.status === 'completed').length
)

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
  const map = {
    pending: 'Pending',
    pending_upload: 'Upload Documents',
    pending_review: 'Under Review',
    documents_rejected: 'Documents Rejected',
    in_waitlist: 'In Waitlist',
    physical_docs_required: 'Interview Required',
    completed: 'Enrolled',
  }
  return map[status] || status
}
</script>

<style scoped>
.dashboard {
  max-width: 900px;
}

.welcome-card {
  background: linear-gradient(135deg, #0d3b6e 0%, #1a5fa4 100%);
  color: white;
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 1.5rem;
}

.welcome-card h2 {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

.welcome-card p {
  opacity: 0.9;
  font-size: 0.95rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 1.25rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.stat-card h3 {
  font-size: 0.8rem;
  color: #666;
  font-weight: 500;
  margin-bottom: 0.4rem;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1a5fa4;
}

.section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.section h2 {
  font-size: 1.1rem;
  color: #1a1a2e;
  margin-bottom: 1rem;
}

.applications-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.app-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  border: 1px solid #f0f0f0;
  border-radius: 10px;
  cursor: pointer;
  transition: box-shadow 0.2s, transform 0.15s;
}

.app-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-1px);
}

.app-left h3 {
  font-size: 0.95rem;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 0.2rem;
}

.app-meta {
  font-size: 0.8rem;
  color: #999;
}

.app-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.app-arrow {
  color: #ccc;
  font-size: 1.1rem;
  transition: color 0.2s, transform 0.2s;
}

.app-card:hover .app-arrow {
  color: #1a5fa4;
  transform: translateX(2px);
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.65rem;
  border-radius: 10px;
  font-size: 0.72rem;
  font-weight: 600;
  white-space: nowrap;
}

.status-pending,
.status-pending_upload { background: #fff3cd; color: #856404; }
.status-pending_review { background: #e3f2fd; color: #1565c0; }
.status-documents_rejected { background: #f8d7da; color: #721c24; }
.status-in_waitlist { background: #d4edda; color: #155724; }
.status-physical_docs_required { background: #e8f0fe; color: #1a5fa4; }
.status-completed { background: #c8e6c9; color: #1b5e20; }

.empty-state {
  text-align: center;
  color: #999;
  padding: 2rem;
  font-size: 0.9rem;
}

@media (max-width: 600px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  .app-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  .app-right {
    width: 100%;
    justify-content: space-between;
  }
}
</style>
