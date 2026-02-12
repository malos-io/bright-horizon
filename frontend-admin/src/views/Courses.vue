<template>
  <div class="courses-page">
    <div class="courses-header">
      <h2>Courses</h2>
      <button class="btn-refresh" @click="loadCourses">Refresh</button>
    </div>

    <div v-if="loading" class="loading-state">Loading courses...</div>

    <div v-else-if="courses.length" class="courses-grid">
      <div class="course-card" v-for="course in courses" :key="course.slug" @click="router.push('/courses/' + course.slug)">
        <div class="card-top">
          <div class="card-title-row">
            <h3>{{ course.title }}</h3>
            <span class="status-badge" :class="statusClass(course.active_batch_status)">
              {{ statusLabel(course.active_batch_status) }}
            </span>
          </div>
          <p class="card-category">{{ course.category }}</p>
        </div>
        <div class="card-stats">
          <div class="card-stat">
            <span class="stat-number">{{ course.batch_count }}</span>
            <span class="stat-label">{{ course.batch_count === 1 ? 'Batch' : 'Batches' }}</span>
          </div>
          <div class="card-stat">
            <span class="stat-number">{{ course.total_completed_students }}</span>
            <span class="stat-label">{{ course.total_completed_students === 1 ? 'Student' : 'Students' }}</span>
          </div>
          <div class="card-stat">
            <span class="stat-number stat-date">{{ formatStartDate(course.current_start_date) }}</span>
            <span class="stat-label">Start Date</span>
          </div>
        </div>
        <div class="card-footer">
          <div class="card-instructor">
            <span class="instructor-label">Instructor:</span>
            <span class="instructor-name">{{ course.instructor?.name || 'TBA' }}</span>
          </div>
          <span class="card-arrow">&#8594;</span>
        </div>
      </div>
    </div>

    <div v-else class="empty-state">No courses found</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getCoursesSummary } from '../services/api'

const router = useRouter()
const courses = ref([])
const loading = ref(false)

function statusLabel(status) {
  if (status === 'active') return 'Active'
  if (status === 'enrollment_closed') return 'Enrollment Closed'
  return 'No Active Class'
}

function statusClass(status) {
  if (status === 'active') return 'status-active'
  if (status === 'enrollment_closed') return 'status-enrollment-closed'
  return 'status-inactive'
}

function formatStartDate(dateStr) {
  if (!dateStr || dateStr === 'TBA') return 'TBA'
  try {
    const d = new Date(dateStr + 'T00:00:00')
    if (isNaN(d)) return dateStr
    return d.toLocaleDateString('en-PH', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  } catch {
    return dateStr
  }
}

async function loadCourses() {
  loading.value = true
  try {
    courses.value = await getCoursesSummary()
  } catch (err) {
    console.error('Failed to load courses:', err)
  } finally {
    loading.value = false
  }
}

onMounted(loadCourses)
</script>

<style scoped>
.courses-page {
  max-width: 900px;
}

.courses-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.courses-header h2 {
  font-size: 1.25rem;
  color: #1a1a2e;
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
}

.btn-refresh:hover {
  background: #d0e2fc;
}

.courses-grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.course-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  cursor: pointer;
  transition: box-shadow 0.2s, transform 0.15s;
  overflow: hidden;
}

.course-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
  transform: translateY(-1px);
}

.card-top {
  padding: 1.25rem 1.5rem 0.75rem;
}

.card-title-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.75rem;
  margin-bottom: 0.25rem;
}

.card-title-row h3 {
  font-size: 1.05rem;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0;
}

.card-category {
  font-size: 0.8rem;
  color: #888;
  margin: 0;
}

.status-badge {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  border-radius: 8px;
  font-size: 0.7rem;
  font-weight: 600;
  white-space: nowrap;
  flex-shrink: 0;
}

.status-active {
  background: #c8e6c9;
  color: #1b5e20;
}

.status-enrollment-closed {
  background: #fff3cd;
  color: #856404;
}

.status-inactive {
  background: #f0f0f0;
  color: #888;
}

.card-stats {
  display: flex;
  gap: 0;
  padding: 0.75rem 1.5rem;
  border-top: 1px solid #f0f0f0;
  border-bottom: 1px solid #f0f0f0;
}

.card-stat {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.15rem;
}

.card-stat + .card-stat {
  border-left: 1px solid #f0f0f0;
}

.stat-number {
  font-size: 1.1rem;
  font-weight: 700;
  color: #1a5fa4;
}

.stat-date {
  font-size: 0.85rem;
  font-weight: 600;
}

.stat-label {
  font-size: 0.68rem;
  font-weight: 500;
  color: #999;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1.5rem;
}

.card-instructor {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.82rem;
}

.instructor-label {
  color: #999;
}

.instructor-name {
  color: #444;
  font-weight: 600;
}

.card-arrow {
  color: #ccc;
  font-size: 1.1rem;
  transition: color 0.2s, transform 0.2s;
}

.course-card:hover .card-arrow {
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
  .card-stats {
    flex-direction: column;
    gap: 0.5rem;
  }
  .card-stat + .card-stat {
    border-left: none;
    border-top: 1px solid #f0f0f0;
    padding-top: 0.5rem;
  }
}
</style>
