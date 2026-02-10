<template>
  <div class="my-classes">
    <h1>My Classes</h1>

    <div v-if="loading" class="loading-state">Loading your classes...</div>
    <div v-else-if="errorMsg" class="error-state">{{ errorMsg }}</div>

    <div v-else-if="!classes.length" class="empty-state">
      <p>You don't have any enrolled classes yet.</p>
      <p class="empty-sub">Once your enrollment is completed, your classes will appear here.</p>
    </div>

    <div v-else class="classes-list">
      <div v-for="cls in classes" :key="cls.enrollment_id" class="class-card">
        <div class="class-header">
          <h2>{{ cls.course }}</h2>
          <span class="batch-badge" :class="'batch-' + (cls.batch_status || 'unknown')">
            {{ batchLabel(cls.batch_status) }}
          </span>
        </div>

        <div class="class-details">
          <!-- Instructor -->
          <div v-if="cls.instructor" class="detail-row instructor-row">
            <div class="instructor-info">
              <span class="detail-icon">&#128100;</span>
              <div>
                <span class="instructor-name">{{ cls.instructor.name }}</span>
                <span class="instructor-title">{{ cls.instructor.title }}</span>
              </div>
            </div>
          </div>

          <!-- Schedule & Duration -->
          <div class="detail-grid">
            <div v-if="cls.batch_start_date" class="detail-item">
              <span class="detail-label">Start Date</span>
              <span class="detail-value">{{ cls.batch_start_date }}</span>
            </div>
            <div v-if="cls.duration_weeks" class="detail-item">
              <span class="detail-label">Duration</span>
              <span class="detail-value">{{ cls.duration_weeks }} weeks ({{ cls.total_hours }} hrs)</span>
            </div>
            <div v-if="cls.schedule && cls.schedule.length" class="detail-item">
              <span class="detail-label">Schedule</span>
              <span class="detail-value">
                {{ cls.schedule.map(s => `${s.day} — ${s.time}`).join(', ') }}
              </span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Enrolled</span>
              <span class="detail-value">{{ formatDate(cls.enrolled_at) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getMyClasses } from '../services/api'

const loading = ref(true)
const errorMsg = ref('')
const classes = ref([])

onMounted(async () => {
  try {
    const data = await getMyClasses()
    classes.value = data.classes || []
  } catch (e) {
    errorMsg.value = e.response?.data?.detail || 'Failed to load your classes.'
  } finally {
    loading.value = false
  }
})

function batchLabel(status) {
  const map = {
    active: 'Enrolling',
    enrollment_closed: 'In Progress',
    completed: 'Completed',
  }
  return map[status] || 'Scheduled'
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
</script>

<style scoped>
.my-classes {
  max-width: 900px;
}

.my-classes > h1 {
  font-size: 1.3rem;
  color: #1a1a2e;
  margin-bottom: 1.25rem;
}

.loading-state,
.error-state {
  text-align: center;
  padding: 3rem;
  color: #999;
  font-size: 0.95rem;
}

.error-state {
  color: #dc2626;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.empty-state p {
  color: #666;
  font-size: 0.95rem;
}

.empty-sub {
  color: #999 !important;
  font-size: 0.82rem !important;
  margin-top: 0.25rem;
}

.classes-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.class-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.class-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  background: linear-gradient(135deg, #0d3b6e 0%, #1a5fa4 100%);
  color: white;
}

.class-header h2 {
  font-size: 1.1rem;
  font-weight: 700;
}

.batch-badge {
  padding: 0.25rem 0.7rem;
  border-radius: 10px;
  font-size: 0.7rem;
  font-weight: 600;
  white-space: nowrap;
}

.batch-active { background: #fff3cd; color: #856404; }
.batch-enrollment_closed { background: #e3f2fd; color: #1565c0; }
.batch-completed { background: #c8e6c9; color: #1b5e20; }
.batch-unknown { background: rgba(255,255,255,0.2); color: white; }

.class-details {
  padding: 1.25rem 1.5rem;
}

.instructor-row {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #f0f0f0;
}

.instructor-info {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.detail-icon {
  font-size: 1.5rem;
}

.instructor-name {
  display: block;
  font-weight: 600;
  font-size: 0.9rem;
  color: #1a1a2e;
}

.instructor-title {
  display: block;
  font-size: 0.78rem;
  color: #999;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.75rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.detail-label {
  font-size: 0.7rem;
  font-weight: 600;
  color: #999;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.detail-value {
  font-size: 0.88rem;
  color: #1a1a2e;
}

@media (max-width: 600px) {
  .class-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
