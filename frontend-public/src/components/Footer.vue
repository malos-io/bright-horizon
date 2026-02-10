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
          <a href="https://www.facebook.com/profile.php?id=61587655770706" target="_blank" rel="noopener noreferrer" class="social-link">FB</a>
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
          <li>info@brighthii.com</li>
        </ul>
      </div>
    </div>

    <div class="accreditation">
      <p class="accreditation-text">Accredited & Registered</p>
      <div class="accreditation-logos">
        <div class="accreditation-card">
          <div class="accreditation-img-wrap">
            <img :src="tesdaLogo" alt="TESDA Accredited" class="accreditation-logo" />
          </div>
          <span class="accreditation-label">TESDA Accredited</span>
        </div>
        <div class="accreditation-card">
          <div class="accreditation-img-wrap">
            <img :src="secLogo" alt="SEC Registered" class="accreditation-logo" />
          </div>
          <span class="accreditation-label">SEC Registered</span>
        </div>
      </div>
    </div>

    <div class="footer-bottom">
      <p>&copy; 2026 Bright Horizons Institute Inc. All rights reserved.</p>
      <a :href="adminUrl" class="admin-link">Admin Login</a>
    </div>
  </footer>
</template>

<script setup>
import logo from '@/assets/logo.png'
import tesdaLogo from '@/assets/tesda-logo.png'
import secLogo from '@/assets/sec-logo.png'

const adminUrl = import.meta.env.VITE_ADMIN_URL || 'http://localhost:5174'
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
  background: #1a5fa4;
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
  color: #1a5fa4;
}

.contact-list li {
  color: #a0a0a0;
}

.accreditation {
  max-width: 1200px;
  margin: 40px auto 0;
  padding: 30px 20px;
  text-align: center;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.accreditation-text {
  color: #a0a0a0;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 2px;
  margin-bottom: 24px;
}

.accreditation-logos {
  display: flex;
  justify-content: center;
  align-items: stretch;
  gap: 30px;
}

.accreditation-card {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 20px 30px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  transition: all 0.3s;
}

.accreditation-card:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

.accreditation-img-wrap {
  background: white;
  border-radius: 10px;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 80px;
}

.accreditation-logo {
  max-height: 56px;
  width: auto;
  max-width: 140px;
  object-fit: contain;
}

.accreditation-label {
  color: #a0a0a0;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.footer-bottom {
  margin-top: 20px;
  padding: 20px;
  text-align: center;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.footer-bottom p {
  color: #a0a0a0;
  font-size: 14px;
}

.admin-link {
  color: #666;
  font-size: 12px;
  text-decoration: none;
  margin-top: 8px;
  display: inline-block;
  transition: color 0.2s;
}

.admin-link:hover {
  color: #a0a0a0;
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
