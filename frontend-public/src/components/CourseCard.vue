<template>
  <router-link :to="`/${course.slug}`" class="course-card">
    <div class="card-image">
      <img :src="course.image" :alt="course.title" />
      <span class="category-badge">{{ course.category }}</span>
      <span v-if="!course.is_coming_soon && course.discounted_price" class="discount-badge">
        {{ getDiscount() }}% OFF
      </span>
      <div v-if="course.is_coming_soon" class="coming-soon-overlay">
        <div class="coming-soon-text">Coming Soon</div>
      </div>
    </div>

    <div class="card-content">
      <h3 class="course-title">{{ course.title }}</h3>
      <p class="course-desc">{{ course.short_description }}</p>

      <div class="course-meta">
        <div class="meta-item">
          <span class="meta-icon">&#128337;</span>
          <span>{{ course.duration_weeks }} weeks</span>
        </div>
        <div class="meta-item">
          <span class="meta-icon">&#128218;</span>
          <span>{{ course.total_hours }} hours</span>
        </div>
        <div class="meta-item">
          <span class="meta-icon">&#127942;</span>
          <span>{{ course.certification }}</span>
        </div>
        <div class="meta-item">
          <span class="meta-icon">&#128197;</span>
          <span>Starts: {{ formatStartDate(course.start_dates) }}</span>
        </div>
        <div v-if="course.enrollment_deadline" class="meta-item">
          <span class="meta-icon">&#9200;</span>
          <span>Deadline: {{ formatDeadline(course.enrollment_deadline) }}</span>
        </div>
      </div>

      <div class="course-stats">
        <div class="rating">
          <span class="stars">&#9733;</span>
          <span class="rating-value">{{ course.rating }}</span>
          <span class="reviews">({{ course.reviews_count }} reviews)</span>
        </div>
        <div class="enrolled">
          <span>{{ formatNumber(course.enrolled_count) }} enrolled</span>
        </div>
      </div>

      <div class="scholarship-note">
        <span>&#127891;</span> Scholarships Available
      </div>

      <div class="card-footer">
        <div class="price-section">
          <template v-if="course.is_coming_soon">
            <span class="current-price">Available Soon</span>
          </template>
          <template v-else-if="course.price > 0">
            <span v-if="course.discounted_price" class="original-price">&#8369;{{ Number(course.price).toLocaleString() }}</span>
            <span class="current-price">&#8369;{{ Number(course.discounted_price || course.price).toLocaleString() }}</span>
          </template>
          <template v-else>
            <span class="current-price">Contact us for pricing</span>
          </template>
        </div>
        <button v-if="course.is_coming_soon" class="coming-soon-btn" disabled>Coming Soon</button>
        <button v-else class="enroll-btn">View Course</button>
      </div>
    </div>
  </router-link>
</template>

<script setup>
const props = defineProps({
  course: {
    type: Object,
    required: true,
  },
})

const formatNumber = (num) => {
  return num.toLocaleString()
}

const formatStartDate = (startDates) => {
  const val = (startDates && startDates.length) ? startDates[0] : ''
  if (!val || val === 'TBA') return 'TBA'
  const d = new Date(val + 'T00:00:00')
  if (isNaN(d)) return val
  return d.toLocaleDateString('en-PH', { year: 'numeric', month: 'long', day: 'numeric' })
}

const formatDeadline = (val) => {
  if (!val || val === 'TBA') return 'TBA'
  const d = new Date(val + 'T00:00:00')
  if (isNaN(d)) return val
  return d.toLocaleDateString('en-PH', { year: 'numeric', month: 'long', day: 'numeric' })
}

const getDiscount = () => {
  if (!props.course.discounted_price) return 0
  const discount = ((props.course.price - props.course.discounted_price) / props.course.price) * 100
  return Math.round(discount)
}

</script>

<style scoped>
.course-card {
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  text-decoration: none;
  display: block;
}

.course-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.card-image {
  position: relative;
  height: 180px;
  overflow: hidden;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.course-card:hover .card-image img {
  transform: scale(1.05);
}

.category-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  background: rgba(255, 255, 255, 0.95);
  color: #1a5fa4;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.discount-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  background: #ff6b6b;
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
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
  padding: 16px 40px;
  border-radius: 12px;
  font-size: 20px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 2px;
  box-shadow: 0 4px 20px rgba(255, 152, 0, 0.5);
  transform: rotate(-5deg);
}

.card-content {
  padding: 20px;
}

.course-title {
  font-size: 18px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 10px;
  line-height: 1.3;
}

.course-desc {
  font-size: 14px;
  color: #666;
  line-height: 1.5;
  margin: 0 0 15px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.course-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 15px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: #888;
}

.meta-icon {
  font-size: 14px;
}

.course-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-top: 1px solid #eee;
  border-bottom: 1px solid #eee;
  margin-bottom: 15px;
}

.rating {
  display: flex;
  align-items: center;
  gap: 5px;
}

.stars {
  color: #ffc107;
  font-size: 16px;
}

.rating-value {
  font-weight: 600;
  color: #1a1a2e;
}

.reviews {
  font-size: 12px;
  color: #888;
}

.enrolled {
  font-size: 12px;
  color: #888;
}

.scholarship-note {
  background: #fff8e1;
  border: 1px solid #ffe082;
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 13px;
  font-weight: 600;
  color: #e65100;
  margin-bottom: 15px;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.price-section {
  display: flex;
  align-items: center;
  gap: 8px;
}

.original-price {
  font-size: 14px;
  color: #999;
  text-decoration: line-through;
}

.current-price {
  font-size: 20px;
  font-weight: 700;
  color: #1a5fa4;
}

.enroll-btn {
  background: linear-gradient(135deg, #0d3b6e 0%, #1a5fa4 100%);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.enroll-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(26, 95, 164, 0.4);
}

.coming-soon-btn {
  background: #ccc;
  color: #666;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  cursor: not-allowed;
  opacity: 0.7;
}
</style>
