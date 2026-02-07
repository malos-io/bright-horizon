<template>
  <div class="home">
    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-content">
        <h1>Build Your Future with <span class="highlight">TESDA-Certified</span> Skills</h1>
        <p>
          Transform your career with industry-recognized training programs.
          Join thousands of successful graduates working locally and internationally.
        </p>
        <div class="hero-actions">
          <router-link to="/courses" class="btn btn-primary">Explore Courses</router-link>
          <a href="#courses" class="btn btn-outline">View Programs</a>
        </div>
        <div class="hero-stats">
          <div class="stat">
            <span class="stat-number">5,000+</span>
            <span class="stat-label">Graduates</span>
          </div>
          <div class="stat">
            <span class="stat-number">15+</span>
            <span class="stat-label">Courses</span>
          </div>
          <div class="stat">
            <span class="stat-number">95%</span>
            <span class="stat-label">Job Placement</span>
          </div>
          <div class="stat">
            <span class="stat-number">4.8</span>
            <span class="stat-label">Rating</span>
          </div>
        </div>
      </div>
      <div class="hero-image">
        <img src="https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=600&h=500&fit=crop" alt="Students learning" />
      </div>
    </section>

    <!-- Features Section -->
    <section class="features">
      <div class="features-container">
        <div class="feature-card">
          <div class="feature-icon">&#127891;</div>
          <h3>TESDA Accredited</h3>
          <p>All programs are TESDA-accredited for nationally recognized certifications</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">&#128188;</div>
          <h3>Job Placement</h3>
          <p>Strong industry partnerships ensure employment opportunities for graduates</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">&#128104;&#8205;&#127891;</div>
          <h3>Expert Trainers</h3>
          <p>Learn from industry professionals with years of real-world experience</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">&#128176;</div>
          <h3>Affordable Fees</h3>
          <p>Quality education at competitive rates with flexible payment options</p>
        </div>
      </div>
    </section>

    <!-- Courses Section -->
    <section id="courses" class="courses-section">
      <div class="section-header">
        <h2>Popular <span class="highlight">Training Programs</span></h2>
        <p>Choose from our wide range of industry-focused courses</p>
      </div>

      <div class="courses-grid" v-if="courses.length > 0">
        <CourseCard v-for="course in courses" :key="course.id" :course="course" />
      </div>

      <div v-else class="loading">
        <p>Loading courses...</p>
      </div>

      <div class="view-all">
        <router-link to="/courses" class="btn btn-primary">View All Courses</router-link>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta">
      <div class="cta-content">
        <h2>Ready to Start Your Journey?</h2>
        <p>Enroll now and take the first step towards a better career. Limited slots available!</p>
        <div class="cta-actions">
          <router-link to="/courses" class="btn btn-white">Browse Courses</router-link>
          <a href="#" class="btn btn-outline-white">Contact Us</a>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getCourses } from '../services/api'
import CourseCard from '../components/CourseCard.vue'

const courses = ref([])

onMounted(async () => {
  try {
    courses.value = await getCourses()
  } catch (error) {
    console.error('Error fetching courses:', error)
  }
})
</script>

<style scoped>
.home {
  overflow-x: hidden;
  position: relative;
  background: linear-gradient(180deg, #f8f9ff 0%, #ffffff 50%, #f0f4ff 100%);
}

.home::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 600px;
  background:
    radial-gradient(ellipse 80% 50% at 20% -10%, rgba(26, 95, 164, 0.15) 0%, transparent 50%),
    radial-gradient(ellipse 60% 40% at 80% 10%, rgba(232, 135, 42, 0.12) 0%, transparent 50%);
  pointer-events: none;
  z-index: 0;
}

.home > section {
  position: relative;
  z-index: 1;
}

.home::after {
  content: '';
  position: absolute;
  top: 400px;
  right: -100px;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(26, 95, 164, 0.08) 0%, transparent 70%);
  border-radius: 50%;
  pointer-events: none;
  z-index: 0;
  animation: float 8s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) scale(1);
  }
  50% {
    transform: translateY(-30px) scale(1.05);
  }
}

/* Hero Section */
.hero {
  max-width: 1200px;
  margin: 0 auto;
  padding: 60px 20px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 60px;
  align-items: center;
}

.hero-content h1 {
  font-size: 48px;
  font-weight: 800;
  color: #1a1a2e;
  line-height: 1.2;
  margin-bottom: 20px;
}

.highlight {
  background: linear-gradient(135deg, #1a5fa4 0%, #e8872a 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-content p {
  font-size: 18px;
  color: #666;
  line-height: 1.7;
  margin-bottom: 30px;
}

.hero-actions {
  display: flex;
  gap: 15px;
  margin-bottom: 40px;
}

.btn {
  padding: 14px 28px;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  text-decoration: none;
  display: inline-block;
  font-size: 16px;
  border: none;
}

.btn-primary {
  background: linear-gradient(135deg, #1a5fa4 0%, #e8872a 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(26, 95, 164, 0.4);
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

.hero-stats {
  display: flex;
  gap: 40px;
}

.stat {
  display: flex;
  flex-direction: column;
}

.stat-number {
  font-size: 32px;
  font-weight: 800;
  color: #1a1a2e;
}

.stat-label {
  font-size: 14px;
  color: #888;
}

.hero-image {
  position: relative;
}

.hero-image img {
  width: 100%;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

/* Features Section */
.features {
  background: linear-gradient(135deg, #f8f9ff 0%, #e8ecff 50%, #f0f4ff 100%);
  padding: 80px 20px;
  position: relative;
  overflow: hidden;
}

.features::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -20%;
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(26, 95, 164, 0.1) 0%, transparent 60%);
  border-radius: 50%;
  animation: float 10s ease-in-out infinite reverse;
}

.features-container {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 30px;
}

.feature-card {
  background: white;
  padding: 30px;
  border-radius: 16px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.feature-icon {
  font-size: 40px;
  margin-bottom: 15px;
}

.feature-card h3 {
  font-size: 18px;
  color: #1a1a2e;
  margin-bottom: 10px;
}

.feature-card p {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
}

/* Courses Section */
.courses-section {
  max-width: 1200px;
  margin: 0 auto;
  padding: 80px 20px;
}

.section-header {
  text-align: center;
  margin-bottom: 50px;
}

.section-header h2 {
  font-size: 36px;
  font-weight: 800;
  color: #1a1a2e;
  margin-bottom: 10px;
}

.section-header p {
  font-size: 18px;
  color: #666;
}

.courses-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 30px;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #666;
}

.view-all {
  text-align: center;
  margin-top: 40px;
}

/* Why Choose Us Section */
.why-us {
  max-width: 1200px;
  margin: 0 auto;
  padding: 80px 20px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 60px;
  align-items: center;
}

.why-us-content h2 {
  font-size: 36px;
  font-weight: 800;
  color: #1a1a2e;
  margin-bottom: 30px;
}

.why-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.why-list li {
  display: flex;
  gap: 15px;
  margin-bottom: 25px;
}

.check {
  width: 30px;
  height: 30px;
  background: linear-gradient(135deg, #1a5fa4 0%, #e8872a 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  flex-shrink: 0;
}

.why-list strong {
  color: #1a1a2e;
  font-size: 16px;
  display: block;
  margin-bottom: 5px;
}

.why-list p {
  color: #666;
  font-size: 14px;
  margin: 0;
}

.why-us-image img {
  width: 100%;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

/* CTA Section */
.cta {
  background: linear-gradient(135deg, #1a5fa4 0%, #e8872a 100%);
  padding: 80px 20px;
  text-align: center;
}

.cta-content {
  max-width: 700px;
  margin: 0 auto;
}

.cta h2 {
  font-size: 36px;
  font-weight: 800;
  color: white;
  margin-bottom: 15px;
}

.cta p {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 30px;
}

.cta-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
}

.btn-white {
  background: white;
  color: #1a5fa4;
}

.btn-white:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.btn-outline-white {
  background: transparent;
  border: 2px solid white;
  color: white;
}

.btn-outline-white:hover {
  background: white;
  color: #1a5fa4;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .courses-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .features-container {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .hero {
    grid-template-columns: 1fr;
    text-align: center;
  }

  .hero-content h1 {
    font-size: 36px;
  }

  .hero-actions {
    justify-content: center;
  }

  .hero-stats {
    justify-content: center;
  }

  .hero-image {
    order: -1;
  }

  .why-us {
    grid-template-columns: 1fr;
  }

  .why-us-image {
    order: -1;
  }

  .courses-grid {
    grid-template-columns: 1fr;
  }

  .features-container {
    grid-template-columns: 1fr;
  }

  .cta-actions {
    flex-direction: column;
    align-items: center;
  }
}
</style>
