<template>
  <div class="navbar-wrapper">
    <div class="top-bar">
      <div class="top-bar-inner">
        <div class="top-bar-left">
          <span class="top-bar-item">0995 589 2022</span>
          <span class="top-bar-divider">|</span>
          <span class="top-bar-item">info@brighthii.com</span>
        </div>
        <div class="top-bar-right">
          <a :href="studentUrl" class="top-bar-link">Student Portal</a>
        </div>
      </div>
    </div>

    <nav class="navbar">
      <div class="nav-container">
        <router-link to="/" class="nav-logo">
          <img :src="logo" alt="Bright Horizons Institute Inc." class="logo-img" />
          <div class="logo-text-wrapper">
            <span class="logo-text">Bright Horizons Institute Inc.</span>
            <span class="logo-tagline">Where Future Shines Bright</span>
          </div>
        </router-link>

        <div class="nav-menu">
          <router-link to="/" class="nav-link">Home</router-link>
          <router-link to="/courses" class="nav-link">Courses</router-link>
          <router-link to="/sponsors" class="nav-link">Sponsors</router-link>
          <a href="#" class="nav-link">Contact</a>
        </div>

        <div class="nav-actions">
          <router-link to="/track" class="btn btn-outline">Track Application</router-link>
          <router-link to="/apply" class="btn btn-primary">Apply for Class Now</router-link>
        </div>

        <button class="mobile-menu-btn" @click="toggleMobile">
          <span></span>
          <span></span>
          <span></span>
        </button>
      </div>

      <div class="mobile-menu" :class="{ active: mobileOpen }">
        <router-link to="/" class="nav-link" @click="mobileOpen = false">Home</router-link>
        <router-link to="/courses" class="nav-link" @click="mobileOpen = false">Courses</router-link>
        <router-link to="/sponsors" class="nav-link" @click="mobileOpen = false">Sponsors</router-link>
        <a href="#" class="nav-link">Contact</a>
        <div class="mobile-actions">
          <a :href="studentUrl" class="btn btn-outline" @click="mobileOpen = false">Student Portal</a>
          <router-link to="/track" class="btn btn-outline" @click="mobileOpen = false">Track Application</router-link>
          <router-link to="/apply" class="btn btn-primary" @click="mobileOpen = false">Apply for Class Now</router-link>
        </div>
      </div>
    </nav>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import logo from '@/assets/logo.png'

const studentUrl = import.meta.env.VITE_STUDENT_URL || 'http://localhost:5175'
const mobileOpen = ref(false)

const toggleMobile = () => {
  mobileOpen.value = !mobileOpen.value
}
</script>

<style scoped>
.navbar-wrapper {
  position: sticky;
  top: 0;
  z-index: 1000;
}

.top-bar {
  background: #1a1a2e;
  color: rgba(255, 255, 255, 0.8);
  font-size: 13px;
}

.top-bar-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 8px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.top-bar-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.top-bar-divider {
  color: rgba(255, 255, 255, 0.3);
}

.top-bar-item {
  color: rgba(255, 255, 255, 0.7);
}

.top-bar-right {
  display: flex;
  align-items: center;
}

.top-bar-link {
  color: #fff;
  text-decoration: none;
  font-weight: 600;
  padding: 4px 14px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 4px;
  transition: all 0.2s;
}

.top-bar-link:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.5);
}

.navbar {
  background: #fff;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 160px;
}

.nav-logo {
  display: flex;
  align-items: center;
  gap: 18px;
  text-decoration: none;
}

.logo-img {
  height: 130px;
  width: auto;
}

.logo-text-wrapper {
  display: flex;
  flex-direction: column;
}

.logo-text {
  font-weight: 700;
  font-size: 18px;
  background: linear-gradient(90deg, #1a4a6e 0%, #2d7da8 50%, #e88a1a 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.logo-tagline {
  font-size: 18px;
  font-weight: 700;
  font-style: italic;
  color: #e88a1a;
  margin-top: 2px;
}

.nav-menu {
  display: flex;
  gap: 30px;
}

.nav-link {
  text-decoration: none;
  color: #4a4a4a;
  font-weight: 500;
  transition: color 0.3s;
}

.nav-link:hover,
.nav-link.router-link-active {
  color: #1a5fa4;
}

.nav-actions {
  display: flex;
  gap: 12px;
}

.btn {
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
  font-size: 14px;
  text-decoration: none;
  text-align: center;
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

.btn-primary {
  background: linear-gradient(135deg, #0d3b6e 0%, #1a5fa4 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(26, 95, 164, 0.4);
}

.mobile-menu-btn {
  display: none;
  flex-direction: column;
  gap: 5px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 5px;
}

.mobile-menu-btn span {
  width: 25px;
  height: 3px;
  background: #1a1a2e;
  border-radius: 2px;
}

.mobile-menu {
  display: none;
}

@media (max-width: 768px) {
  .top-bar-left {
    display: none;
  }

  .top-bar-inner {
    justify-content: flex-end;
  }

  .nav-menu,
  .nav-actions {
    display: none;
  }

  .mobile-menu-btn {
    display: flex;
  }

  .mobile-menu {
    display: none;
    flex-direction: column;
    padding: 20px;
    background: #fff;
    border-top: 1px solid #eee;
  }

  .mobile-menu.active {
    display: flex;
  }

  .mobile-menu .nav-link {
    padding: 12px 0;
    border-bottom: 1px solid #eee;
  }

  .mobile-actions {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-top: 15px;
  }

  .mobile-actions .btn {
    flex: 1;
  }
}
</style>
