<template>
  <div class="dashboard">
    <div class="welcome-card">
      <h2>Welcome back!</h2>
      <p>Continue where you left off or explore new courses.</p>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <h3>Enrolled Courses</h3>
        <p class="stat-value">--</p>
      </div>
      <div class="stat-card">
        <h3>Completed</h3>
        <p class="stat-value">--</p>
      </div>
      <div class="stat-card">
        <h3>In Progress</h3>
        <p class="stat-value">--</p>
      </div>
    </div>

    <div class="section">
      <h2>Available Courses</h2>
      <div class="courses-grid">
        <div v-for="course in courses" :key="course.id || course.slug" class="course-card">
          <h3>{{ course.title }}</h3>
          <p class="course-category">{{ course.category }}</p>
          <p class="course-duration">{{ course.duration || 'TBD' }}</p>
        </div>
        <p v-if="courses.length === 0" class="empty-state">No courses available yet.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getCourses } from '../services/api'

const courses = ref([])

onMounted(async () => {
  try {
    courses.value = await getCourses()
  } catch (e) {
    console.error('Failed to load courses:', e)
  }
})
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
}

.welcome-card {
  background: linear-gradient(135deg, #0d3b6e 0%, #1a5fa4 100%);
  color: white;
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 2rem;
}

.welcome-card h2 {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

.welcome-card p {
  opacity: 0.9;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.stat-card h3 {
  font-size: 0.85rem;
  color: #666;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 2rem;
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

.courses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}

.course-card {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 1.25rem;
  transition: box-shadow 0.2s;
}

.course-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.course-card h3 {
  font-size: 1rem;
  color: #1a1a2e;
  margin-bottom: 0.5rem;
}

.course-category {
  font-size: 0.8rem;
  color: #1a5fa4;
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.course-duration {
  font-size: 0.85rem;
  color: #999;
}

.empty-state {
  text-align: center;
  color: #999;
  padding: 2rem;
  grid-column: 1 / -1;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
