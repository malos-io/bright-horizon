<template>
  <div class="sponsors-page">
    <!-- Hero Section -->
    <section class="sponsors-hero">
      <div class="hero-content">
        <h1>Our <span class="highlight">Sponsors</span></h1>
        <p>We are grateful to our sponsors who believe in empowering individuals through education and skills training.</p>
      </div>
    </section>

    <!-- Stats Section -->
    <section v-if="sponsors.length > 0" class="stats-section">
      <div class="stats-container">
        <div class="stat-card">
          <span class="stat-number">{{ totalScholars }}</span>
          <span class="stat-label">Scholars Supported</span>
        </div>
        <div class="stat-card">
          <span class="stat-number">{{ sponsors.length }}</span>
          <span class="stat-label">Active Sponsors</span>
        </div>
        <div class="stat-card">
          <span class="stat-number">100%</span>
          <span class="stat-label">Graduation Rate</span>
        </div>
      </div>
    </section>

    <!-- Sponsors Grid -->
    <section class="sponsors-section">
      <div class="section-header">
        <h2>Meet Our <span class="highlight">Sponsors</span></h2>
        <p>Leaders who are making a difference in our community</p>
      </div>

      <div class="sponsors-grid" v-if="sponsors.length > 0">
        <div v-for="sponsor in sponsors" :key="sponsor.id" class="sponsor-card">
          <div class="sponsor-image">
            <img v-if="sponsor.image" :src="sponsor.image" :alt="sponsor.name" />
            <div v-else class="sponsor-placeholder">
              <svg viewBox="0 0 200 250" xmlns="http://www.w3.org/2000/svg">
                <rect width="200" height="250" fill="#e8ecf1"/>
                <circle cx="100" cy="90" r="35" fill="#c5cdd8"/>
                <ellipse cx="100" cy="190" rx="55" ry="40" fill="#c5cdd8"/>
              </svg>
            </div>
          </div>
          <div class="sponsor-info">
            <h3>{{ sponsor.name }}</h3>
            <p class="sponsor-title">{{ sponsor.title }}</p>
            <p class="sponsor-position" v-if="sponsor.position">{{ sponsor.position }}</p>
            <div class="sponsor-stats">
              <div class="scholar-count">
                <span class="count-icon">&#127891;</span>
                <span><strong>{{ sponsor.scholars_sponsored }}</strong> Scholars Sponsored</span>
              </div>
            </div>
            <p class="sponsor-message" v-if="sponsor.message">"{{ sponsor.message }}"</p>
          </div>
        </div>
      </div>

      <div v-else class="no-sponsors">
        <div class="no-sponsors-icon">&#129309;</div>
        <h3>Be Our First Sponsor!</h3>
        <p>Help empower individuals through education and skills training. Your support can change lives and build brighter futures in our community.</p>
        <a href="#" class="btn btn-blue">Get in Touch</a>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta">
      <div class="cta-content">
        <h2>Become a Sponsor</h2>
        <p>Help us empower more individuals through skills training. Your support can change lives.</p>
        <div class="cta-actions">
          <a href="#" class="btn btn-white">Contact Us</a>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { getSponsors } from '../services/api'

const sponsors = ref([])

const totalScholars = computed(() => {
  return sponsors.value.reduce((sum, s) => sum + s.scholars_sponsored, 0)
})

onMounted(async () => {
  try {
    sponsors.value = await getSponsors()
  } catch (error) {
    console.error('Error fetching sponsors:', error)
  }
})
</script>

<style scoped>
.sponsors-page {
  overflow-x: hidden;
  position: relative;
  background: linear-gradient(180deg, #f8f9ff 0%, #ffffff 50%, #f0f4ff 100%);
}

/* Hero Section */
.sponsors-hero {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  padding: 80px 20px;
  text-align: center;
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
  color: white;
}

.sponsors-hero h1 {
  font-size: 48px;
  font-weight: 800;
  margin-bottom: 20px;
}

.highlight {
  background: linear-gradient(135deg, #0d3b6e 0%, #1a5fa4 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.sponsors-hero p {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.7;
}

/* Stats Section */
.stats-section {
  padding: 0 20px;
  margin-top: -40px;
  position: relative;
  z-index: 10;
}

.stats-container {
  max-width: 900px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.stat-card {
  background: white;
  padding: 30px;
  border-radius: 16px;
  text-align: center;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.stat-number {
  display: block;
  font-size: 42px;
  font-weight: 800;
  background: linear-gradient(135deg, #0d3b6e 0%, #1a5fa4 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-top: 5px;
}

/* Sponsors Section */
.sponsors-section {
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

.sponsors-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 30px;
}

.sponsor-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  display: flex;
  transition: all 0.3s;
}

.sponsor-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.12);
}

.sponsor-image {
  width: 200px;
  height: 280px;
  flex-shrink: 0;
  overflow: hidden;
}

.sponsor-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.sponsor-info {
  padding: 25px;
  display: flex;
  flex-direction: column;
}

.sponsor-info h3 {
  font-size: 22px;
  font-weight: 700;
  color: #1a1a2e;
  margin-bottom: 5px;
}

.sponsor-title {
  font-size: 14px;
  color: #1a5fa4;
  font-weight: 600;
  margin-bottom: 3px;
}

.sponsor-position {
  font-size: 13px;
  color: #888;
  margin-bottom: 15px;
}

.sponsor-stats {
  margin-bottom: 15px;
}

.scholar-count {
  display: flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, rgba(26, 95, 164, 0.1) 0%, rgba(232, 135, 42, 0.1) 100%);
  padding: 10px 15px;
  border-radius: 10px;
  font-size: 14px;
  color: #555;
}

.count-icon {
  font-size: 20px;
}

.sponsor-message {
  font-size: 14px;
  color: #666;
  font-style: italic;
  line-height: 1.6;
  margin-top: auto;
  padding-top: 15px;
  border-top: 1px solid #eee;
}

/* CTA Section */
.cta {
  background: linear-gradient(135deg, #0d3b6e 0%, #1a5fa4 100%);
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

.btn-white {
  background: white;
  color: #1a5fa4;
}

.btn-white:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.sponsor-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #e8ecf1;
}

.sponsor-placeholder svg {
  width: 100%;
  height: 100%;
}

.no-sponsors {
  text-align: center;
  padding: 60px 20px;
  max-width: 500px;
  margin: 0 auto;
}

.no-sponsors-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.no-sponsors h3 {
  font-size: 28px;
  font-weight: 800;
  color: #1a1a2e;
  margin-bottom: 15px;
}

.no-sponsors p {
  font-size: 16px;
  color: #666;
  line-height: 1.7;
  margin-bottom: 25px;
}

.btn-blue {
  background: linear-gradient(135deg, #0d3b6e 0%, #1a5fa4 100%);
  color: white;
}

.btn-blue:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(26, 95, 164, 0.3);
}

/* Responsive */
@media (max-width: 900px) {
  .sponsors-grid {
    grid-template-columns: 1fr;
  }

  .sponsor-card {
    flex-direction: column;
  }

  .sponsor-image {
    width: 100%;
    height: 250px;
  }
}

@media (max-width: 768px) {
  .sponsors-hero h1 {
    font-size: 36px;
  }

  .stats-container {
    grid-template-columns: 1fr;
  }

  .stat-card {
    padding: 20px;
  }

  .stat-number {
    font-size: 32px;
  }
}
</style>
