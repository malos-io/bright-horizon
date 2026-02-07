<template>
  <div class="courses-page">
    <section class="page-header">
      <h1>Our <span class="highlight">Training Programs</span></h1>
      <p>Choose from our wide range of TESDA-accredited courses</p>
    </section>

    <section class="courses-content">
      <div class="filters">
        <button
          v-for="cat in categories"
          :key="cat"
          class="filter-btn"
          :class="{ active: selectedCategory === cat }"
          @click="selectedCategory = cat"
        >
          {{ cat }}
        </button>
      </div>

      <div class="courses-grid" v-if="filteredCourses.length > 0">
        <CourseCard v-for="course in filteredCourses" :key="course.id" :course="course" />
      </div>

      <div v-else class="loading">
        <p>Loading courses...</p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getCourses } from '../services/api'
import CourseCard from '../components/CourseCard.vue'

const courses = ref([])
const selectedCategory = ref('All')

const categories = computed(() => {
  const cats = ['All', ...new Set(courses.value.map(c => c.category))]
  return cats
})

const filteredCourses = computed(() => {
  if (selectedCategory.value === 'All') {
    return courses.value
  }
  return courses.value.filter(c => c.category === selectedCategory.value)
})

onMounted(async () => {
  try {
    courses.value = await getCourses()
  } catch (error) {
    console.error('Error fetching courses:', error)
  }
})
</script>

<style scoped>
.courses-page {
  min-height: 100vh;
}

.page-header {
  background: linear-gradient(135deg, #1a5fa4 0%, #e8872a 100%);
  padding: 80px 20px;
  text-align: center;
  color: white;
}

.page-header h1 {
  font-size: 42px;
  font-weight: 800;
  margin-bottom: 10px;
}

.page-header .highlight {
  color: white;
  -webkit-text-fill-color: white;
}

.page-header p {
  font-size: 18px;
  opacity: 0.9;
}

.courses-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 50px 20px;
}

.filters {
  display: flex;
  gap: 10px;
  margin-bottom: 40px;
  flex-wrap: wrap;
}

.filter-btn {
  padding: 10px 24px;
  border: 2px solid #eee;
  background: white;
  border-radius: 30px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  color: #666;
}

.filter-btn:hover {
  border-color: #1a5fa4;
  color: #1a5fa4;
}

.filter-btn.active {
  background: linear-gradient(135deg, #1a5fa4 0%, #e8872a 100%);
  border-color: transparent;
  color: white;
}

.courses-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 30px;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #666;
}

@media (max-width: 1024px) {
  .courses-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .page-header h1 {
    font-size: 32px;
  }

  .courses-grid {
    grid-template-columns: 1fr;
  }
}
</style>
