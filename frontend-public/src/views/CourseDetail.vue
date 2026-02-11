<template>
  <div class="course-detail" v-if="course">
    <!-- Hero Section -->
    <section class="course-hero">
      <div class="hero-content">
        <div class="breadcrumb">
          <router-link to="/">Home</router-link>
          <span>/</span>
          <router-link to="/courses">Courses</router-link>
          <span>/</span>
          <span>{{ course.title }}</span>
        </div>

        <span class="category-badge">{{ course.category }}</span>
        <span v-if="course.is_coming_soon" class="coming-soon-badge-large">Coming Soon</span>
        <h1>{{ course.title }}</h1>
        <p class="hero-desc">{{ course.short_description }}</p>

        <div class="course-meta">
          <div class="meta-item">
            <span class="stars">&#9733;</span>
            <span class="rating">{{ course.rating }}</span>
            <span class="reviews">({{ course.reviews_count }} reviews)</span>
          </div>
          <div class="meta-item">
            <span>{{ formatNumber(course.enrolled_count) }} students enrolled</span>
          </div>
        </div>

        <div class="instructor-preview">
          <div class="instructor-avatar">{{ course.instructor.name.charAt(0) }}</div>
          <div>
            <span class="instructor-label">Instructor</span>
            <span class="instructor-name">{{ course.instructor.name }}</span>
          </div>
        </div>
      </div>

      <div class="course-card-sticky">
        <div class="card-image">
          <img :src="course.image" :alt="course.title" />
          <div v-if="course.is_coming_soon" class="coming-soon-overlay">
            <div class="coming-soon-text">Coming Soon</div>
          </div>
        </div>
        <div class="card-content">
          <div v-if="course.is_coming_soon" class="coming-soon-notice">
            <span class="notice-icon">&#128337;</span>
            <div>
              <div class="notice-title">Coming Soon</div>
              <div class="notice-text">This course will be available for enrollment soon</div>
            </div>
          </div>
          <div v-else>
            <div class="contact-pricing">
              <span class="contact-pricing-icon">&#128172;</span>
              <span class="contact-pricing-text">Contact us for pricing</span>
            </div>
            <div class="scholarship-banner">
              <span class="scholarship-icon">&#127891;</span>
              <span class="scholarship-text">Scholarship Available</span>
            </div>

            <router-link :to="'/apply/' + route.params.slug" class="btn btn-primary btn-full">Apply for Class Now</router-link>
          </div>

          <div class="card-features">
            <h4>This course includes:</h4>
            <ul>
              <li><span class="icon">&#128337;</span> {{ course.duration_weeks }} weeks duration</li>
              <li><span class="icon">&#128218;</span> {{ course.total_hours }} total hours</li>
              <li><span class="icon">&#127942;</span> {{ course.certification }}</li>
              <li><span class="icon">&#128101;</span> Class size: {{ course.class_size }} students</li>
              <li><span class="icon">&#128197;</span> Starts: {{ formatStartDate(course.start_dates?.[0]) }}</li>
              <li><span class="icon">&#128196;</span> Certificate of completion</li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <!-- Course Content -->
    <div class="course-content">
      <div class="main-content">
        <!-- About Section -->
        <section class="content-section about-section">
          <h2>About This Course</h2>
          <div class="description">
            <div class="desc-icon">
              <span>&#128218;</span>
            </div>
            <div class="desc-content" v-html="formatDescription(course.description)"></div>
          </div>
        </section>

        <!-- What You'll Learn -->
        <section class="content-section">
          <h2>What You'll Learn</h2>
          <div class="learn-grid">
            <div v-for="(item, index) in course.what_you_learn" :key="index" class="learn-item">
              <span class="check-icon">&#10003;</span>
              <span>{{ item }}</span>
            </div>
          </div>
        </section>

        <!-- Course Modules -->
        <section class="content-section">
          <h2>Course Curriculum</h2>
          <div class="modules-list">
            <div v-for="(module, index) in course.modules" :key="index" class="module-item">
              <div class="module-header">
                <div class="module-number">{{ index + 1 }}</div>
                <div class="module-info">
                  <h4>{{ module.title }}</h4>
                  <p>{{ module.description }}</p>
                </div>
                <div class="module-duration">{{ module.duration_hours }} hours</div>
              </div>
            </div>
          </div>
        </section>

        <!-- Requirements -->
        <section class="content-section">
          <h2>Requirements</h2>
          <ul class="requirements-list">
            <li v-for="(req, index) in course.requirements" :key="index">
              <span class="bullet">&#8226;</span>
              {{ req }}
            </li>
          </ul>
        </section>

        <!-- Career Opportunities -->
        <section class="content-section">
          <h2>Career Opportunities</h2>
          <div class="career-grid">
            <div v-for="(career, index) in course.career_opportunities" :key="index" class="career-item">
              <span class="briefcase-icon">&#128188;</span>
              <span>{{ career }}</span>
            </div>
          </div>
        </section>

        <!-- Schedule & Start Dates -->
        <section class="content-section">
          <h2>Schedule & Upcoming Batches</h2>
          <div class="schedule-info">
            <div class="schedule-block">
              <h4>Class Schedule</h4>
              <div v-for="(sched, index) in course.schedule" :key="index" class="schedule-item">
                <span class="day">{{ sched.day }}</span>
                <span class="time">{{ sched.time }}</span>
                <span class="duration">({{ sched.duration }})</span>
              </div>
            </div>
            <div class="dates-block">
              <h4>Upcoming Start Dates</h4>
              <div v-for="(date, index) in course.start_dates" :key="index" class="date-item">
                <span class="calendar-icon">&#128197;</span>
                <span>{{ formatStartDate(date) }}</span>
              </div>
            </div>
          </div>
        </section>

        <!-- Instructor -->
        <section class="content-section">
          <h2>Your Instructor</h2>
          <div class="instructor-card">
            <div class="instructor-avatar-large">{{ course.instructor.name.charAt(0) }}</div>
            <div class="instructor-info">
              <h3>{{ course.instructor.name }}</h3>
              <p class="instructor-title">{{ course.instructor.title }}</p>
              <p class="instructor-bio">{{ course.instructor.bio }}</p>
            </div>
          </div>
        </section>
      </div>
    </div>

    <!-- Mobile Sticky CTA -->
    <div class="mobile-cta" v-if="!course.is_coming_soon">
      <div class="mobile-price">
        <span class="contact-pricing-label">Contact us for pricing</span>
        <span class="scholarship-label">&#127891; Scholarship Available</span>
      </div>
      <router-link :to="'/apply/' + route.params.slug" class="btn btn-primary">Apply for Class Now</router-link>
    </div>
  </div>

  <div v-else-if="notFound" class="loading-page">
    <p>Course not found.</p>
    <router-link to="/courses" class="back-link">Browse all courses</router-link>
  </div>

  <div v-else class="loading-page">
    <p>Loading course details...</p>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getCourse } from '../services/api'

const route = useRoute()
const course = ref(null)
const notFound = ref(false)

const fetchCourse = async (slug) => {
  try {
    notFound.value = false
    course.value = await getCourse(slug)
  } catch (error) {
    if (error.response?.status === 404) {
      notFound.value = true
    } else {
      console.error('Error fetching course:', error)
    }
  }
}

onMounted(() => {
  fetchCourse(route.params.slug)
})

watch(() => route.params.slug, (newSlug) => {
  if (newSlug) {
    fetchCourse(newSlug)
  }
})

const formatStartDate = (val) => {
  if (!val || val === 'TBA') return 'TBA'
  const d = new Date(val + 'T00:00:00')
  if (isNaN(d)) return val
  return d.toLocaleDateString('en-PH', { year: 'numeric', month: 'long', day: 'numeric' })
}

const formatNumber = (num) => {
  return num.toLocaleString()
}

const formatDescription = (desc) => {
  return desc.replace(/\n\n/g, '</p><p>').replace(/^/, '<p>').replace(/$/, '</p>')
}

</script>

<style scoped>
.course-detail {
  background: #f8f9ff;
  min-height: 100vh;
}

/* Hero Section */
.course-hero {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  padding: 40px 20px 60px;
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: 60px;
  max-width: 1200px;
  margin: 0 auto;
}

.hero-content {
  color: white;
}

.breadcrumb {
  display: flex;
  gap: 10px;
  font-size: 14px;
  margin-bottom: 20px;
  color: rgba(255, 255, 255, 0.7);
}

.breadcrumb a {
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
}

.breadcrumb a:hover {
  color: white;
}

.category-badge {
  background: rgba(26, 95, 164, 0.3);
  color: #a5b4fc;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  display: inline-block;
  margin-bottom: 15px;
}

.coming-soon-badge-large {
  background: #ff9800;
  color: white;
  padding: 8px 20px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  display: inline-block;
  margin-left: 12px;
}

.course-hero h1 {
  font-size: 36px;
  font-weight: 800;
  margin-bottom: 15px;
  line-height: 1.2;
}

.hero-desc {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.6;
  margin-bottom: 20px;
}

.course-meta {
  display: flex;
  gap: 30px;
  margin-bottom: 25px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}

.stars {
  color: #ffc107;
  font-size: 18px;
}

.rating {
  font-weight: 600;
  color: #ffc107;
}

.instructor-preview {
  display: flex;
  align-items: center;
  gap: 12px;
}

.instructor-avatar {
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #0d3b6e 0%, #1a5fa4 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 20px;
}

.instructor-label {
  display: block;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.instructor-name {
  font-weight: 600;
}

/* Sticky Course Card */
.course-card-sticky {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  position: sticky;
  top: 90px;
}

.card-image {
  position: relative;
}

.card-image img {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.coming-soon-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(2px);
}

.coming-soon-text {
  background: #ff9800;
  color: white;
  padding: 12px 30px;
  border-radius: 10px;
  font-size: 18px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 2px;
  box-shadow: 0 4px 20px rgba(255, 152, 0, 0.5);
  transform: rotate(-5deg);
}

.card-content {
  padding: 25px;
}

.contact-pricing {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #e8f0fe;
  border: 1px solid #c4d9f2;
  border-radius: 10px;
  padding: 14px 18px;
  margin-bottom: 20px;
}

.contact-pricing-icon {
  font-size: 22px;
}

.contact-pricing-text {
  font-size: 16px;
  font-weight: 600;
  color: #0d3b6e;
}

.scholarship-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fff8e1;
  border: 1px solid #ffe082;
  border-radius: 10px;
  padding: 12px 18px;
  margin-bottom: 20px;
}

.scholarship-icon {
  font-size: 20px;
}

.scholarship-text {
  font-size: 14px;
  font-weight: 600;
  color: #e65100;
}

.coming-soon-notice {
  display: flex;
  align-items: center;
  gap: 15px;
  background: #fff3e0;
  border: 2px solid #ff9800;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
}

.notice-icon {
  font-size: 36px;
}

.notice-title {
  font-size: 16px;
  font-weight: 700;
  color: #e65100;
  margin-bottom: 4px;
}

.notice-text {
  font-size: 14px;
  color: #666;
}

.btn {
  padding: 14px 24px;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 16px;
  border: none;
  text-align: center;
}

.btn-full {
  width: 100%;
  margin-bottom: 12px;
}

.btn-primary {
  background: linear-gradient(135deg, #0d3b6e 0%, #1a5fa4 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(26, 95, 164, 0.4);
}

.btn-outline {
  background: transparent;
  border: 2px solid #1a5fa4;
  color: #1a5fa4;
}

.btn-outline:hover {
  background: #1a5fa4;
  color: white;
}

.card-features {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.card-features h4 {
  font-size: 14px;
  color: #1a1a2e;
  margin-bottom: 15px;
}

.card-features ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.card-features li {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: #666;
  margin-bottom: 12px;
}

.card-features .icon {
  font-size: 16px;
}

/* Main Content */
.course-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: 60px;
}

.main-content {
  grid-column: 1;
}

.content-section {
  background: white;
  border-radius: 16px;
  padding: 30px;
  margin-bottom: 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.content-section h2 {
  font-size: 24px;
  font-weight: 700;
  color: #1a1a2e;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #f0f0f0;
}

/* About Section Enhanced */
.about-section .description {
  display: flex;
  gap: 24px;
  align-items: flex-start;
}

.desc-icon {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #0d3b6e 0%, #1a5fa4 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.desc-icon span {
  font-size: 28px;
  filter: grayscale(1) brightness(10);
}

.desc-content {
  flex: 1;
  padding-left: 24px;
  border-left: 3px solid #1a5fa4;
}

.desc-content p {
  font-size: 16px;
  color: #555;
  line-height: 1.9;
  margin-bottom: 16px;
}

.desc-content p:first-child {
  font-size: 17px;
  color: #333;
  font-weight: 500;
}

.desc-content p:last-child {
  margin-bottom: 0;
}

.description p {
  font-size: 16px;
  color: #555;
  line-height: 1.8;
  margin-bottom: 15px;
}

/* What You'll Learn */
.learn-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.learn-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  font-size: 15px;
  color: #555;
}

.check-icon {
  width: 24px;
  height: 24px;
  background: linear-gradient(135deg, #0d3b6e 0%, #1a5fa4 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  flex-shrink: 0;
}

/* Course Modules */
.modules-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.module-item {
  border: 1px solid #eee;
  border-radius: 12px;
  overflow: hidden;
}

.module-header {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  background: #fafafa;
}

.module-number {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #0d3b6e 0%, #1a5fa4 100%);
  color: white;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  flex-shrink: 0;
}

.module-info {
  flex: 1;
}

.module-info h4 {
  font-size: 16px;
  color: #1a1a2e;
  margin-bottom: 5px;
}

.module-info p {
  font-size: 14px;
  color: #888;
  margin: 0;
}

.module-duration {
  font-size: 14px;
  color: #1a5fa4;
  font-weight: 600;
  background: rgba(26, 95, 164, 0.1);
  padding: 6px 12px;
  border-radius: 20px;
}

/* Requirements */
.requirements-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.requirements-list li {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 15px;
  color: #555;
  margin-bottom: 12px;
}

.bullet {
  color: #1a5fa4;
  font-size: 20px;
}

/* Career Opportunities */
.career-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.career-item {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #f8f9ff;
  padding: 15px;
  border-radius: 10px;
  font-size: 15px;
  color: #555;
}

.briefcase-icon {
  font-size: 20px;
}

/* Schedule */
.schedule-info {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
}

.schedule-block h4,
.dates-block h4 {
  font-size: 16px;
  color: #1a1a2e;
  margin-bottom: 15px;
}

.schedule-item {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 10px;
  font-size: 14px;
}

.day {
  font-weight: 600;
  color: #1a1a2e;
}

.time {
  color: #1a5fa4;
}

.duration {
  color: #888;
}

.date-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  font-size: 14px;
  color: #555;
}

.calendar-icon {
  font-size: 18px;
}

/* Instructor */
.instructor-card {
  display: flex;
  gap: 25px;
  align-items: flex-start;
}

.instructor-avatar-large {
  width: 100px;
  height: 100px;
  background: linear-gradient(135deg, #0d3b6e 0%, #1a5fa4 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 40px;
  color: white;
  flex-shrink: 0;
}

.instructor-info h3 {
  font-size: 20px;
  color: #1a1a2e;
  margin-bottom: 5px;
}

.instructor-title {
  font-size: 14px;
  color: #1a5fa4;
  margin-bottom: 15px;
}

.instructor-bio {
  font-size: 15px;
  color: #666;
  line-height: 1.7;
}

/* Mobile CTA */
.mobile-cta {
  display: none;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  padding: 15px 20px;
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.1);
  justify-content: space-between;
  align-items: center;
  z-index: 100;
}

.mobile-price .contact-pricing-label {
  font-size: 15px;
  font-weight: 600;
  color: #0d3b6e;
  display: block;
}

.mobile-price .scholarship-label {
  font-size: 12px;
  font-weight: 600;
  color: #e65100;
  margin-top: 2px;
  display: block;
}

.mobile-cta .btn {
  padding: 12px 30px;
}

/* Loading */
.loading-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 50vh;
  color: #666;
  gap: 12px;
}

.back-link {
  color: #1a5fa4;
  text-decoration: none;
  font-weight: 600;
}

.back-link:hover {
  text-decoration: underline;
}

/* Responsive */
@media (max-width: 1024px) {
  .course-hero {
    grid-template-columns: 1fr;
    padding: 30px 20px;
  }

  .course-card-sticky {
    position: relative;
    top: 0;
    max-width: 500px;
    margin: 0 auto;
  }

  .course-content {
    grid-template-columns: 1fr;
  }

  .learn-grid,
  .career-grid,
  .schedule-info {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .course-hero h1 {
    font-size: 28px;
  }

  .course-meta {
    flex-direction: column;
    gap: 10px;
  }

  .course-card-sticky {
    display: none;
  }

  .mobile-cta {
    display: flex;
  }

  .content-section {
    padding: 20px;
  }

  .about-section .description {
    flex-direction: column;
    gap: 16px;
  }

  .desc-icon {
    width: 48px;
    height: 48px;
    border-radius: 12px;
  }

  .desc-icon span {
    font-size: 24px;
  }

  .desc-content {
    padding-left: 16px;
  }

  .instructor-card {
    flex-direction: column;
    text-align: center;
    align-items: center;
  }
}
</style>
