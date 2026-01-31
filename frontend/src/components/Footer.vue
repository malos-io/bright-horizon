<template>
  <footer class="footer">
    <div class="footer-container">
      <div class="footer-section">
        <div class="footer-logo">
          <img :src="logo" alt="Bright Horizons Institute Inc." class="logo-img" />
          <span class="logo-text">Bright Horizons Institute Inc.</span>
        </div>
        <p class="footer-desc">
          Empowering individuals with industry-recognized skills and certifications
          for better career opportunities.
        </p>
        <div class="social-links">
          <a href="#" class="social-link">FB</a>
          <a href="#" class="social-link">IG</a>
          <a href="#" class="social-link">TW</a>
          <a href="#" class="social-link">YT</a>
        </div>
      </div>

      <div class="footer-section">
        <h4>Quick Links</h4>
        <ul>
          <li><router-link to="/">Home</router-link></li>
          <li><router-link to="/courses">All Courses</router-link></li>
          <li><a href="#">About Us</a></li>
          <li><a href="#">Contact</a></li>
        </ul>
      </div>

      <div class="footer-section">
        <h4>Our Courses</h4>
        <ul>
          <li><router-link to="/bookkeeping-nc-iii">Bookkeeping NC III</router-link></li>
          <li><router-link to="/events-management-nc-iii">Events Management NC III</router-link></li>
        </ul>
      </div>

      <div class="footer-section">
        <h4>Contact Us</h4>
        <ul class="contact-list">
          <li>123 Training Street, Manila</li>
          <li>Philippines 1000</li>
          <li>0995 589 2022</li>
          <li>info@trainingcenter.ph</li>
        </ul>
      </div>
    </div>

    <div class="footer-bottom">
      <p>&copy; 2026 Bright Horizons Institute Inc. All rights reserved. | TESDA Accredited</p>
    </div>
  </footer>
</template>

<script setup>
import logo from '@/assets/logo.png'
</script>

<style scoped>
.footer {
  background: #1a1a2e;
  color: #fff;
  padding: 60px 0 0;
}

.footer-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 40px;
}

.footer-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.logo-img {
  height: 40px;
  width: auto;
}

.logo-text {
  font-weight: 700;
  font-size: 18px;
}

.footer-desc {
  color: #a0a0a0;
  line-height: 1.6;
  margin-bottom: 20px;
}

.social-links {
  display: flex;
  gap: 10px;
}

.social-link {
  width: 36px;
  height: 36px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  text-decoration: none;
  font-size: 12px;
  font-weight: 600;
  transition: all 0.3s;
}

.social-link:hover {
  background: #667eea;
}

.footer-section h4 {
  font-size: 16px;
  margin-bottom: 20px;
  color: #fff;
}

.footer-section ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-section ul li {
  margin-bottom: 12px;
}

.footer-section ul a {
  color: #a0a0a0;
  text-decoration: none;
  transition: color 0.3s;
}

.footer-section ul a:hover {
  color: #667eea;
}

.contact-list li {
  color: #a0a0a0;
}

.footer-bottom {
  margin-top: 40px;
  padding: 20px;
  text-align: center;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.footer-bottom p {
  color: #a0a0a0;
  font-size: 14px;
}

@media (max-width: 768px) {
  .footer-container {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 480px) {
  .footer-container {
    grid-template-columns: 1fr;
  }
}
</style>
