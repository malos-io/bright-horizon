<template>
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
        <button class="btn btn-outline">Login</button>
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
        <button class="btn btn-outline">Login</button>
        <router-link to="/apply" class="btn btn-primary" @click="mobileOpen = false">Apply for Class Now</router-link>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref } from 'vue'
import logo from '@/assets/logo.png'

const mobileOpen = ref(false)

const toggleMobile = () => {
  mobileOpen.value = !mobileOpen.value
}
</script>

<style scoped>
.navbar {
  background: #fff;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
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
    gap: 10px;
    margin-top: 15px;
  }

  .mobile-actions .btn {
    flex: 1;
  }
}
</style>
