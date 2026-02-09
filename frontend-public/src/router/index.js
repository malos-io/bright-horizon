import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import CourseDetail from '../views/CourseDetail.vue'
import Courses from '../views/Courses.vue'
import Sponsors from '../views/Sponsors.vue'
import Apply from '../views/Apply.vue'
import TrackApplication from '../views/TrackApplication.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
  },
  {
    path: '/courses',
    name: 'Courses',
    component: Courses,
  },
  {
    path: '/sponsors',
    name: 'Sponsors',
    component: Sponsors,
  },
  {
    path: '/track',
    name: 'TrackApplication',
    component: TrackApplication,
  },
  {
    path: '/apply',
    name: 'Apply',
    component: Apply,
  },
  {
    path: '/apply/:courseSlug',
    name: 'ApplyWithCourse',
    component: Apply,
  },
  {
    path: '/:slug',
    name: 'CourseDetail',
    component: CourseDetail,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

export default router
