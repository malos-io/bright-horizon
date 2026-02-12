<template>
  <div class="apply-page">
    <div class="form-container">
      <div class="form-header">
        <h1>TESDA Registration Form</h1>
        <p>MIS 03-01 — Learner's / Trainee's / Student's Registration Form</p>
      </div>

      <div class="requirements-card">
        <div class="requirements-header" @click="requirementsCollapsed = !requirementsCollapsed">
          <div class="req-header-left">
            <h3>Documentary Requirements</h3>
            <p>Prepare the following before your enrollment. Keep at least 2 photocopies; bring originals for verification.</p>
          </div>
          <button class="req-toggle" type="button">
            <svg :class="{ rotated: requirementsCollapsed }" width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M5 8l5 5 5-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </button>
        </div>

        <div class="requirements-body" v-show="!requirementsCollapsed">
          <div class="req-grid">
            <div class="req-item">
              <span class="req-num">1</span>
              <div class="req-content">
                <strong>Birth Certificate</strong>
                <span class="req-detail">PSA/NSO-issued photocopy</span>
              </div>
              <span class="req-onsite-badge">Required</span>
            </div>

            <div class="req-item">
              <span class="req-num">2</span>
              <div class="req-content">
                <strong>Educational Credentials</strong>
                <span class="req-detail">Photocopy of any of the following:</span>
                <ul class="req-sub">
                  <li>High School or Senior High School Diploma</li>
                  <li>Transcript of Records (College/Graduate)</li>
                  <li>Form 137 or 138 (Report Card)</li>
                </ul>
              </div>
              <span class="req-onsite-badge">Required</span>
            </div>

            <div class="req-item">
              <span class="req-num">3</span>
              <div class="req-content">
                <strong>ID Pictures</strong>
                <span class="req-detail">White background, with collar, printed name tag</span>
                <ul class="req-sub">
                  <li>4 pcs — Passport size</li>
                  <li>4 pcs — 1x1 size</li>
                </ul>
              </div>
              <span class="req-onsite-badge">We can provide this onsite</span>
            </div>

            <div class="req-item">
              <span class="req-num">4</span>
              <div class="req-content">
                <strong>Government Issued ID</strong>
                <span class="req-detail">Any one of the following:</span>
                <ul class="req-sub">
                  <li>National ID (PhilSys)</li>
                  <li>Voter's ID</li>
                  <li>Driver's License</li>
                  <li>Passport</li>
                </ul>
              </div>
              <span class="req-onsite-badge">Required</span>
            </div>

            <div class="req-item">
              <span class="req-num">5</span>
              <div class="req-content">
                <strong>Proof of Name Change</strong>
                <span class="req-detail">Required only if name on Birth Certificate differs from your current legal name (e.g. married name)</span>
                <ul class="req-sub">
                  <li>Marriage Certificate</li>
                  <li>Court Order for change of name</li>
                </ul>
              </div>
              <span class="req-onsite-badge">If applicable</span>
            </div>

          </div>

          <div class="req-note">
            <div class="req-note-badge">NOTE</div>
            <p>You will be asked to upload or photograph these documents as part of your application to help expedite the review process. <strong>You must bring the physical documents onsite once accepted</strong> for verification prior to enrollment.</p>
          </div>
        </div>
      </div>

      <form @submit.prevent="handleSubmit" class="tesda-form">
        <!-- Section 2: Manpower Profile -->
        <div class="form-section">
          <h2>II. Manpower Profile</h2>
          <div class="form-row three-col">
            <div class="form-group">
              <label>Last Name <span class="required">*</span></label>
              <input v-model="form.lastName" type="text" required />
            </div>
            <div class="form-group">
              <label>First Name <span class="required">*</span></label>
              <input v-model="form.firstName" type="text" required />
            </div>
            <div class="form-group">
              <label>Middle Name</label>
              <input v-model="form.middleName" type="text" />
            </div>
          </div>

          <h3 class="sub-heading">Complete Mailing Address</h3>
          <div class="form-row three-col">
            <div class="form-group">
              <label>Region</label>
              <select v-model="address.selectedRegion.value">
                <option value="">-- Select Region --</option>
                <option v-for="r in address.regionOptions" :key="r" :value="r">{{ r }}</option>
              </select>
            </div>
            <div class="form-group">
              <label>Province</label>
              <select v-model="address.selectedProvince.value" :disabled="!address.selectedRegion.value">
                <option value="">-- Select Province --</option>
                <option v-for="p in address.provinceOptions.value" :key="p" :value="p">{{ p }}</option>
              </select>
            </div>
            <div class="form-group">
              <label>City / Municipality</label>
              <select v-model="address.selectedCity.value" :disabled="!address.selectedProvince.value">
                <option value="">-- Select City/Municipality --</option>
                <option v-for="c in address.cityOptions.value" :key="c" :value="c">{{ c }}</option>
              </select>
            </div>
          </div>
          <div class="form-row three-col">
            <div class="form-group">
              <label>Street No. / Street</label>
              <input v-model="form.street" type="text" />
            </div>
            <div class="form-group">
              <label>Barangay</label>
              <select v-model="address.selectedBarangay.value" :disabled="!address.selectedCity.value || address.barangayLoading.value">
                <option value="">{{ address.barangayLoading.value ? 'Loading...' : '-- Select Barangay --' }}</option>
                <option v-for="b in address.barangayOptions.value" :key="b" :value="b">{{ b }}</option>
              </select>
            </div>
            <div class="form-group">
              <label>District</label>
              <input v-model="form.district" type="text" disabled class="disabled-field" />
            </div>
          </div>

          <div class="form-row three-col">
            <div class="form-group">
              <label>Email Address <span class="required">*</span></label>
              <input v-model="form.email" type="email" required />
            </div>
            <div class="form-group">
              <label>Contact No. <span class="required">*</span></label>
              <input v-model="form.contactNo" type="tel" required />
            </div>
            <div class="form-group">
              <label>Nationality</label>
              <input v-model="form.nationality" type="text" />
            </div>
          </div>
        </div>

        <!-- Section 3: Personal Information -->
        <div class="form-section">
          <h2>III. Personal Information</h2>

          <div class="form-row two-col">
            <div class="form-group">
              <label>Sex</label>
              <div class="radio-group">
                <label class="radio-label">
                  <input type="radio" v-model="form.sex" value="Male" /> Male
                </label>
                <label class="radio-label">
                  <input type="radio" v-model="form.sex" value="Female" /> Female
                </label>
              </div>
            </div>
            <div class="form-group">
              <label>Civil Status</label>
              <div class="radio-group">
                <label class="radio-label">
                  <input type="radio" v-model="form.civilStatus" value="Single" /> Single
                </label>
                <label class="radio-label">
                  <input type="radio" v-model="form.civilStatus" value="Married" /> Married
                </label>
                <label class="radio-label">
                  <input type="radio" v-model="form.civilStatus" value="Widow/er" /> Widow/er
                </label>
                <label class="radio-label">
                  <input type="radio" v-model="form.civilStatus" value="Separated" /> Separated
                </label>
              </div>
            </div>
          </div>

          <div class="form-group">
            <label>Employment Status (Before Training)</label>
            <div class="radio-group wrap">
              <label class="radio-label">
                <input type="radio" v-model="form.employmentStatus" value="Employed" /> Employed
              </label>
              <label class="radio-label">
                <input type="radio" v-model="form.employmentStatus" value="Unemployed" /> Unemployed
              </label>
              <label class="radio-label">
                <input type="radio" v-model="form.employmentStatus" value="Self-employed" /> Self-employed
              </label>
            </div>
          </div>

          <div class="form-row two-col">
            <div class="form-group">
              <label>Date of Birth</label>
              <div class="date-inputs">
                <select v-model="form.birthMonth">
                  <option value="">Month</option>
                  <option v-for="m in months" :key="m" :value="m">{{ m }}</option>
                </select>
                <select v-model="form.birthDay">
                  <option value="">Day</option>
                  <option v-for="d in 31" :key="d" :value="String(d)">{{ d }}</option>
                </select>
                <select v-model="form.birthYear">
                  <option value="">Year</option>
                  <option v-for="y in years" :key="y" :value="String(y)">{{ y }}</option>
                </select>
              </div>
            </div>
            <div class="form-group">
              <label>Age</label>
              <input :value="computedAge" type="text" disabled class="disabled-field" />
            </div>
          </div>

          <h3 class="sub-heading">Birthplace</h3>
          <div class="form-row three-col">
            <div class="form-group">
              <label>Region</label>
              <select v-model="birthplace.selectedRegion.value">
                <option value="">-- Select Region --</option>
                <option v-for="r in birthplace.regionOptions" :key="r" :value="r">{{ r }}</option>
              </select>
            </div>
            <div class="form-group">
              <label>Province</label>
              <select v-model="birthplace.selectedProvince.value" :disabled="!birthplace.selectedRegion.value">
                <option value="">-- Select Province --</option>
                <option v-for="p in birthplace.provinceOptions.value" :key="p" :value="p">{{ p }}</option>
              </select>
            </div>
            <div class="form-group">
              <label>City / Municipality</label>
              <select v-model="birthplace.selectedCity.value" :disabled="!birthplace.selectedProvince.value">
                <option value="">-- Select City/Municipality --</option>
                <option v-for="c in birthplace.cityOptions.value" :key="c" :value="c">{{ c }}</option>
              </select>
            </div>
          </div>

        </div>

        <!-- Educational Attainment -->
        <div class="form-section">
          <h2>Educational Attainment (Before Training)</h2>
          <p class="section-note">Select your highest level of education completed:</p>
          <div class="education-list">
            <label class="education-option" v-for="opt in educationOptions" :key="opt">
              <input type="radio" v-model="form.educationalAttainment" :value="opt" />
              <span class="education-label">{{ opt }}</span>
            </label>
          </div>
        </div>

        <!-- Section 4: Learner Classification -->
        <div class="form-section">
          <h2>IV. Learner / Trainee / Student (Clients) Classification</h2>
          <p class="section-note">Check all that apply:</p>
          <div class="checkbox-group">
            <label class="checkbox-label" v-for="opt in classificationOptions" :key="opt">
              <input type="checkbox" :value="opt" v-model="form.learnerClassification" /> {{ opt }}
            </label>
            <div class="others-field">
              <label class="checkbox-label">
                <input type="checkbox" value="Others" v-model="form.learnerClassification" /> Others (pls. specify)
              </label>
              <input
                v-if="form.learnerClassification.includes('Others')"
                v-model="form.classificationOther"
                type="text"
                placeholder="Please specify"
                class="others-input"
              />
            </div>
          </div>
        </div>

        <!-- Section 5: NCAE / YP4SC -->
        <div class="form-section">
          <h2>V. Has the Applicant Taken NCAE / YP4SC Before?</h2>
          <div class="form-row">
            <div class="form-group">
              <div class="radio-group">
                <label class="radio-label">
                  <input type="radio" v-model="form.ncaeTaken" :value="true" /> Yes
                </label>
                <label class="radio-label">
                  <input type="radio" v-model="form.ncaeTaken" :value="false" /> No
                </label>
              </div>
            </div>
          </div>
          <div class="form-row two-col" v-if="form.ncaeTaken">
            <div class="form-group">
              <label>Where?</label>
              <input v-model="form.ncaeWhere" type="text" />
            </div>
            <div class="form-group">
              <label>When?</label>
              <input v-model="form.ncaeWhen" type="text" />
            </div>
          </div>
        </div>

        <!-- Section 6: Course/Qualification -->
        <div class="form-section">
          <h2>VI. Course / Qualification</h2>
          <div class="form-group">
            <label>Select Course <span class="required">*</span></label>
            <select v-model="form.course" required class="course-select">
              <option value="">-- Select a course --</option>
              <option v-for="c in availableCourses" :key="c.slug" :value="c.title">{{ c.title }}</option>
            </select>
          </div>
        </div>

        <!-- Section 7: Certification -->
        <div class="form-section">
          <h2>VII. Certification</h2>
          <label class="checkbox-label certification-check">
            <input type="checkbox" v-model="form.certificationAgreed" required />
            I hereby certify that the above information is true and correct to the best of my knowledge and belief.
            I understand that any misrepresentation made herein shall cause the cancellation of my enrollment/registration.
          </label>
        </div>

        <!-- Section 8: Scholarship -->
        <div class="form-section">
          <h2>VIII. Scholarship</h2>
          <div class="form-group">
            <label>Do you want to apply for a scholarship?</label>
            <div class="radio-group">
              <label class="radio-label">
                <input type="radio" v-model="form.applyScholarship" :value="true" /> Yes
              </label>
              <label class="radio-label">
                <input type="radio" v-model="form.applyScholarship" :value="false" /> No
              </label>
            </div>
          </div>
        </div>

        <!-- Submit -->
        <div class="form-actions">
          <button type="submit" class="btn-submit" :disabled="submitting">
            {{ submitting ? 'Submitting...' : 'Submit Application' }}
          </button>
        </div>
      </form>

      <!-- Success message -->
      <div v-if="submitted" class="success-overlay">
        <div class="success-card">
          <div class="success-icon">&#10003;</div>
          <h2>Application Submitted!</h2>
          <p>Your registration form has been successfully submitted.</p>
          <p v-if="applicationId" class="reference-id">Reference ID: <strong>{{ applicationId }}</strong></p>

          <div class="next-step-card">
            <h3>What's Next?</h3>
            <p class="next-step-desc">To move your application forward, you'll need to submit the following required documents:</p>
            <ul class="next-step-docs">
              <li>Birth Certificate (PSA/NSO)</li>
              <li>Educational Credentials (TOR, Diploma, Form 137, etc.)</li>
              <li>Government Issued ID</li>
            </ul>
            <p class="next-step-note">
              You don't have to upload them right now &mdash; but your application will remain on
              <strong>"Pending Upload of Required Documents"</strong> until they are submitted.
            </p>
          </div>

          <div class="success-actions">
            <router-link to="/track" class="btn-track">Submit Documents Now</router-link>
          </div>

          <div class="later-hint">
            <p>Not ready yet? No worries! You can always upload your documents later through the <router-link to="/track" class="hint-link">Track Application</router-link> page using the email you provided.</p>
            <router-link to="/" class="btn-home">Back to Home</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getCourses, submitEnrollment } from '../services/api'
import { useAddressDropdown } from '../composables/useAddressDropdown'

const route = useRoute()
const courses = ref([])
const submitting = ref(false)
const submitted = ref(false)
const applicationId = ref('')
const requirementsCollapsed = ref(false)

// Filter out coming soon courses
const availableCourses = computed(() => {
  return courses.value.filter(c => !c.is_coming_soon)
})

// Mailing address cascading dropdowns (with barangay)
const address = useAddressDropdown({ withBarangay: true })

// Birthplace cascading dropdowns (no barangay)
const birthplace = useAddressDropdown({ withBarangay: false })

const months = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
]

const currentYear = new Date().getFullYear()
const years = Array.from({ length: 80 }, (_, i) => currentYear - i)

const educationOptions = [
  'No Grade Completed / Pre-School (Nursery/Kinder/Prep)',
  'Elementary Level',
  'Elementary Graduate',
  'High School Level',
  'High School Graduate',
  'College Level',
  'College Graduate or Higher',
  'Post-Secondary Level/Graduate',
]

const classificationOptions = [
  'Persons with Disabilities (PWDs)',
  'Displaced Worker (Local)',
  'OFW',
  'OFW Dependent',
  'OFW Repatriate',
  'Victims/Survivors of Human Trafficking',
  'Indigenous People & Cultural Communities',
  'Rebel Returnees',
  'Solo Parent',
]

const form = reactive({
  lastName: '',
  firstName: '',
  middleName: '',
  street: '',
  barangay: '',
  district: '',
  city: '',
  province: '',
  region: '',
  email: '',
  contactNo: '',
  nationality: 'Filipino',
  sex: '',
  civilStatus: '',
  employmentStatus: '',
  birthMonth: '',
  birthDay: '',
  birthYear: '',
  birthplaceCity: '',
  birthplaceProvince: '',
  birthplaceRegion: '',
  educationalAttainment: '',
  learnerClassification: [],
  classificationOther: '',
  ncaeTaken: false,
  ncaeWhere: '',
  ncaeWhen: '',
  course: '',
  certificationAgreed: false,
  applyScholarship: false,
})

// Computed age from birthdate
const computedAge = computed(() => {
  const m = months.indexOf(form.birthMonth)
  const d = parseInt(form.birthDay)
  const y = parseInt(form.birthYear)
  if (m < 0 || !d || !y) return ''
  const today = new Date()
  let age = today.getFullYear() - y
  const monthDiff = today.getMonth() - m
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < d)) age--
  return age >= 0 ? String(age) : ''
})

// Sync mailing address selections to form
watch(address.selectedRegion, (v) => { form.region = v })
watch(address.selectedProvince, (v) => { form.province = v })
watch(address.selectedCity, (v) => { form.city = v })
watch(address.selectedBarangay, (v) => { form.barangay = v })
watch(address.autoDistrict, (v) => { form.district = v })

// Sync birthplace selections to form
watch(birthplace.selectedRegion, (v) => { form.birthplaceRegion = v })
watch(birthplace.selectedProvince, (v) => { form.birthplaceProvince = v })
watch(birthplace.selectedCity, (v) => { form.birthplaceCity = v })

onMounted(async () => {
  try {
    courses.value = await getCourses()

    // Pre-fill course from route param if navigated from course page
    const slug = route.params.courseSlug
    if (slug) {
      const match = courses.value.find(c => c.slug === slug)
      if (match) {
        // Prevent enrollment for coming soon courses
        if (match.is_coming_soon) {
          alert('This course is coming soon and not yet available for enrollment.')
          window.location.href = '/courses'
          return
        }
        form.course = match.title
      }
    }
  } catch (e) {
    console.error('Failed to load courses:', e)
  }
})

async function handleSubmit() {
  if (submitting.value) return
  submitting.value = true
  try {
    const result = await submitEnrollment({ ...form, age: computedAge.value })
    applicationId.value = result.id || ''
    submitted.value = true
  } catch (e) {
    console.error('Submission failed:', e)
    alert('Failed to submit application. Please try again.')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.apply-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f0f4ff 0%, #fdf6f0 100%);
  padding: 40px 20px 80px;
}

.form-container {
  max-width: 900px;
  margin: 0 auto;
  position: relative;
}

/* Requirements Card */
.requirements-card {
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e0e8f5;
  margin-bottom: 2rem;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(26, 95, 164, 0.08);
}

.requirements-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  cursor: pointer;
  background: linear-gradient(135deg, #0d3b6e 0%, #1a5fa4 100%);
  transition: opacity 0.2s;
}

.requirements-header:hover {
  opacity: 0.95;
}

.req-header-left h3 {
  margin: 0 0 4px;
  font-size: 16px;
  font-weight: 700;
  color: #fff;
}

.req-header-left p {
  margin: 0;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.4;
}

.req-toggle {
  background: rgba(255, 255, 255, 0.15);
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #fff;
  flex-shrink: 0;
  transition: transform 0.2s, background 0.2s;
}

.req-toggle:hover {
  background: rgba(255, 255, 255, 0.25);
}

.req-toggle svg {
  transition: transform 0.3s ease;
}

.req-toggle svg.rotated {
  transform: rotate(-180deg);
}

.requirements-body {
  padding: 24px;
}

.req-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.req-item {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 14px 16px;
  background: #f8fafc;
  border-radius: 10px;
  border: 1px solid #eef2f7;
  transition: border-color 0.2s;
}

.req-item:hover {
  border-color: #c8d8ec;
}

.req-num {
  width: 28px;
  height: 28px;
  background: linear-gradient(135deg, #0d3b6e 0%, #1a5fa4 100%);
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  flex-shrink: 0;
  margin-top: 1px;
}

.req-content {
  flex: 1;
  min-width: 0;
}

.req-content strong {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #1a1a2e;
  line-height: 1.4;
}

.req-detail {
  display: block;
  font-size: 13px;
  color: #666;
  margin-top: 2px;
}

.req-detail-note {
  margin-top: 6px;
  font-style: italic;
  color: #888;
  font-size: 12px;
  line-height: 1.5;
}

.req-sub {
  margin: 8px 0 0;
  padding-left: 16px;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.req-sub li {
  font-size: 13px;
  color: #555;
  position: relative;
  padding-left: 12px;
}

.req-sub li::before {
  content: "";
  position: absolute;
  left: 0;
  top: 8px;
  width: 5px;
  height: 5px;
  background: #1a5fa4;
  border-radius: 50%;
}

.req-note {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-top: 20px;
  padding: 16px;
  background: #f0f5ff;
  border-radius: 10px;
  border: 1px solid #d4e2f4;
}

.req-onsite-badge {
  background: linear-gradient(135deg, #e65100 0%, #ff8f00 100%);
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  padding: 5px 12px;
  border-radius: 4px;
  letter-spacing: 0.3px;
  white-space: nowrap;
  align-self: center;
  flex-shrink: 0;
  margin-left: auto;
}

.req-note-badge {
  background: #1a5fa4;
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.5px;
  padding: 3px 8px;
  border-radius: 4px;
  flex-shrink: 0;
  margin-top: 2px;
}

.req-note p {
  margin: 0;
  font-size: 13px;
  color: #444;
  line-height: 1.6;
}

.form-header {
  text-align: center;
  margin-bottom: 2rem;
}

.form-header h1 {
  font-size: 2rem;
  font-weight: 800;
  color: #1a1a2e;
  margin-bottom: 0.5rem;
}

.form-header p {
  color: #666;
  font-size: 0.95rem;
}

.tesda-form {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.form-section {
  background: white;
  border-radius: 16px;
  padding: 2.5rem;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.form-section h2 {
  font-size: 1.1rem;
  font-weight: 700;
  color: #1a5fa4;
  margin-bottom: 1.75rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #e8f0fe;
}

.sub-heading {
  font-size: 0.9rem;
  font-weight: 600;
  color: #444;
  margin: 1.75rem 0 1rem;
}

.section-note {
  color: #666;
  font-size: 0.85rem;
  margin-bottom: 1rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
  margin-bottom: 1.25rem;
}

.form-row.three-col {
  grid-template-columns: 1fr 1fr 1fr;
}

.form-row.two-col {
  grid-template-columns: 1fr 1fr;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
}

.form-group label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #444;
}

.required {
  color: #d32f2f;
}

.form-group input[type="text"],
.form-group input[type="email"],
.form-group input[type="tel"],
.form-group select {
  padding: 0.75rem 0.85rem;
  border: 1.5px solid #ddd;
  border-radius: 8px;
  font-size: 0.9rem;
  transition: border-color 0.2s;
  background: white;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #1a5fa4;
  box-shadow: 0 0 0 3px rgba(26, 95, 164, 0.1);
}

.disabled-field {
  background: #f5f5f5 !important;
  color: #999;
  cursor: not-allowed;
}

.date-inputs {
  display: flex;
  gap: 0.5rem;
}

.date-inputs select {
  flex: 1;
  padding: 0.75rem 0.6rem;
  border: 1.5px solid #ddd;
  border-radius: 8px;
  font-size: 0.9rem;
  background: white;
}

.date-inputs select:focus {
  outline: none;
  border-color: #1a5fa4;
  box-shadow: 0 0 0 3px rgba(26, 95, 164, 0.1);
}

.radio-group {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
  padding: 0.5rem 0;
}

.radio-group.wrap {
  gap: 1rem 1.75rem;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.85rem;
  color: #444;
  cursor: pointer;
}

.radio-label input[type="radio"] {
  accent-color: #1a5fa4;
}

.checkbox-group {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.85rem;
  padding: 0.25rem 0;
}

.checkbox-label {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: #444;
  cursor: pointer;
  line-height: 1.4;
}

.checkbox-label input[type="checkbox"] {
  accent-color: #1a5fa4;
  margin-top: 2px;
}

.others-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.others-input {
  padding: 0.5rem 0.75rem;
  border: 1.5px solid #ddd;
  border-radius: 8px;
  font-size: 0.85rem;
  max-width: 300px;
  margin-left: 1.5rem;
}

.others-input:focus {
  outline: none;
  border-color: #1a5fa4;
  box-shadow: 0 0 0 3px rgba(26, 95, 164, 0.1);
}

.certification-check {
  line-height: 1.6;
  font-size: 0.9rem;
}

.course-select {
  max-width: 500px;
}

.education-list {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.education-option {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border: 1px solid #eee;
  margin-top: -1px;
  cursor: pointer;
  transition: background 0.15s;
  font-size: 0.9rem;
  color: #333;
}

.education-option:first-child {
  border-radius: 10px 10px 0 0;
}

.education-option:last-child {
  border-radius: 0 0 10px 10px;
}

.education-option:hover {
  background: #f0f5ff;
}

.education-option input[type="radio"] {
  accent-color: #1a5fa4;
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.education-option input[type="radio"]:checked + .education-label {
  color: #1a5fa4;
  font-weight: 600;
}

.form-actions {
  text-align: center;
  padding: 1rem 0;
}

.btn-submit {
  padding: 1rem 3rem;
  font-size: 1.1rem;
  font-weight: 700;
  color: white;
  background: linear-gradient(135deg, #0d3b6e 0%, #1a5fa4 100%);
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(26, 95, 164, 0.4);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Success overlay */
.success-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.success-card {
  background: white;
  border-radius: 20px;
  padding: 3rem;
  text-align: center;
  max-width: 520px;
  width: 90%;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  max-height: 90vh;
  overflow-y: auto;
}

.success-icon {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #0d3b6e 0%, #1a5fa4 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
  color: white;
  margin: 0 auto 1.5rem;
}

.success-card h2 {
  font-size: 1.5rem;
  color: #1a1a2e;
  margin-bottom: 0.75rem;
}

.success-card p {
  color: #666;
  line-height: 1.6;
  margin-bottom: 1.5rem;
}

.btn-home {
  display: inline-block;
  padding: 0.75rem 2rem;
  background: #1a5fa4;
  color: white;
  border-radius: 10px;
  text-decoration: none;
  font-weight: 600;
  transition: background 0.2s;
}

.btn-home:hover {
  background: #154d87;
}

.reference-id {
  background: #f0f4ff;
  border: 1px solid #c4d9f2;
  border-radius: 8px;
  padding: 10px 16px;
  font-size: 14px;
  color: #0d3b6e;
  word-break: break-all;
}

.track-hint {
  font-size: 14px;
  color: #888;
}

.next-step-card {
  background: #f8f9ff;
  border: 1px solid #d4e0f7;
  border-radius: 12px;
  padding: 1.25rem 1.5rem;
  text-align: left;
  margin-bottom: 1.5rem;
}

.next-step-card h3 {
  font-size: 1rem;
  color: #0d3b6e;
  margin: 0 0 0.5rem;
}

.next-step-desc {
  font-size: 0.85rem;
  color: #555;
  margin: 0 0 0.75rem;
  line-height: 1.5;
}

.next-step-docs {
  list-style: none;
  padding: 0;
  margin: 0 0 0.75rem;
}

.next-step-docs li {
  font-size: 0.85rem;
  color: #1a1a2e;
  padding: 0.35rem 0 0.35rem 1.25rem;
  position: relative;
  font-weight: 500;
}

.next-step-docs li::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 8px;
  height: 8px;
  background: #1a5fa4;
  border-radius: 50%;
}

.next-step-note {
  font-size: 0.8rem;
  color: #856404;
  background: #fff8e1;
  border: 1px solid #ffe082;
  border-radius: 8px;
  padding: 0.6rem 0.85rem;
  line-height: 1.5;
  margin: 0;
}

.later-hint {
  margin-top: 1.25rem;
}

.later-hint p {
  font-size: 0.82rem;
  color: #888;
  margin-bottom: 0.75rem;
  line-height: 1.5;
}

.hint-link {
  color: #1a5fa4;
  font-weight: 600;
  text-decoration: none;
}

.hint-link:hover {
  text-decoration: underline;
}

.success-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.btn-track {
  display: inline-block;
  padding: 0.75rem 2rem;
  background: linear-gradient(135deg, #0d3b6e 0%, #1a5fa4 100%);
  color: white;
  border-radius: 10px;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s;
}

.btn-track:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(26, 95, 164, 0.4);
}

/* Responsive */
@media (max-width: 768px) {
  .form-row,
  .form-row.three-col,
  .form-row.two-col {
    grid-template-columns: 1fr;
  }

  .checkbox-group {
    grid-template-columns: 1fr;
  }

  .form-section {
    padding: 1.25rem;
  }

  .form-header h1 {
    font-size: 1.5rem;
  }
}
</style>
