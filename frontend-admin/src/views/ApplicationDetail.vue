<template>
  <div class="application-detail">
    <!-- Back + header -->
    <div class="detail-header">
      <button class="btn-back" @click="router.push('/')">&#8592; Back to Dashboard</button>
      <div class="header-actions">
        <button v-if="statusValue === 'archived'" class="btn-unarchive" @click="handleUnarchive" :disabled="actionLoading">
          {{ actionLoading ? 'Restoring...' : 'Unarchive' }}
        </button>
        <button v-else class="btn-archive" @click="handleArchive" :disabled="actionLoading">
          {{ actionLoading ? 'Archiving...' : 'Archive' }}
        </button>
        <button v-if="canCancel" class="btn-cancel-app" @click="openCancelModal" :disabled="actionLoading">
          {{ actionLoading ? 'Cancelling...' : 'Cancel Application' }}
        </button>
        <button class="btn-export" @click="downloadPdf" :disabled="pdfLoading">
          {{ pdfLoading ? 'Exporting...' : 'Export Application to PDF' }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading-state">Loading application...</div>
    <div v-else-if="!enrollment" class="empty-state">Application not found</div>

    <template v-else>
      <!-- Applicant summary -->
      <div class="summary-card">
        <div class="summary-info">
          <h2>{{ enrollment.lastName }}, {{ enrollment.firstName }} {{ enrollment.middleName }}</h2>
          <p class="summary-meta">{{ enrollment.course }} &middot; {{ formatDate(enrollment.created_at) }}</p>
        </div>
        <select v-if="isEarlyStatus" v-model="statusValue" @change="handleStatusChange" class="status-select" :class="'status-' + statusValue">
          <option v-for="s in earlyStatuses" :key="s.value" :value="s.value">{{ s.label }}</option>
        </select>
        <span v-else class="status-badge-large" :class="'status-' + statusValue">{{ formatStatusLabel(statusValue) }}</span>
      </div>

      <!-- Sponsor Assignment -->
      <div class="sponsor-assign" v-if="sponsors.length > 0">
        <label class="sponsor-label">Sponsor:</label>
        <select v-model="sponsorValue" @change="handleSponsorChange" class="sponsor-select">
          <option value="">-- No Sponsor --</option>
          <option v-for="s in sponsors" :key="s.id" :value="s.id">{{ s.name }} ({{ s.title }})</option>
        </select>
      </div>

      <!-- Workflow Actions -->
      <div v-if="statusValue === 'in_waitlist'" class="workflow-banner workflow-interview">
        <div class="workflow-text">
          <strong>Ready for interview?</strong>
          <span>Send the interview schedule email and advance to "Physical Documents &amp; Interview Required".</span>
          <span class="workflow-hint">Requires an active course batch with a start date. To create one: go to <strong>Courses</strong> &rarr; select this course &rarr; click <strong>"Start A New Class Batch"</strong> &rarr; set a start date and save.</span>
        </div>
        <button class="btn-workflow" @click="handleSendInterview" :disabled="actionLoading">
          {{ actionLoading ? 'Sending...' : 'Send Interview Schedule' }}
        </button>
      </div>
      <div v-else-if="statusValue === 'physical_docs_required'" class="workflow-banner workflow-complete">
        <div class="workflow-text">
          <strong>Physical Document Verification</strong>
          <span>Upload official scans of the required documents. Status will auto-advance once all official scans are uploaded.</span>
        </div>
      </div>
      <div v-else-if="statusValue === 'waiting_for_class_start'" class="workflow-banner workflow-complete">
        <div class="workflow-text">
          <strong>Ready to assign to a class batch</strong>
          <span v-if="activeBatchInfo">Assign this applicant to the current <strong>{{ activeBatchInfo.courseName }}</strong> batch (start date: <strong>{{ activeBatchInfo.startDate }}</strong>).</span>
          <span v-else>No active batch found for this course. Please create a class batch first.</span>
        </div>
        <button v-if="activeBatchInfo" class="btn-workflow btn-workflow-green" @click="handleCompleteEnrollment" :disabled="actionLoading">
          {{ actionLoading ? 'Processing...' : `Add to Batch (${activeBatchInfo.startDate})` }}
        </button>
      </div>
      <div v-else-if="statusValue === 'completed'" class="workflow-banner workflow-done">
        <div class="workflow-text">
          <strong>Enrollment completed</strong>
          <span>This applicant has been promoted to a student account.</span>
          <span v-if="enrollment.batch_start_date" class="workflow-hint">Assigned batch start date: <strong>{{ enrollment.batch_start_date }}</strong></span>
        </div>
        <button class="btn-workflow btn-workflow-orange" @click="handleRemoveFromBatch" :disabled="actionLoading">
          {{ actionLoading ? 'Processing...' : 'Remove from Batch' }}
        </button>
      </div>
      <div v-else-if="statusValue === 'archived'" class="workflow-banner workflow-archived">
        <div class="workflow-text">
          <strong>This application is archived</strong>
          <span>It is hidden from the dashboard and the applicant's tracker. Click "Unarchive" to restore it.</span>
        </div>
        <button class="btn-workflow" @click="handleUnarchive" :disabled="actionLoading">
          {{ actionLoading ? 'Restoring...' : 'Unarchive' }}
        </button>
      </div>
      <div v-else-if="statusValue === 'withdrawn'" class="workflow-banner workflow-withdrawn">
        <div class="workflow-text">
          <strong>This application was withdrawn by the applicant</strong>
          <span v-if="enrollment.withdraw_reason">Reason: {{ enrollment.withdraw_reason }}<template v-if="enrollment.withdraw_comments"> &mdash; {{ enrollment.withdraw_comments }}</template></span>
        </div>
      </div>
      <div v-else-if="statusValue === 'cancelled'" class="workflow-banner workflow-cancelled">
        <div class="workflow-text">
          <strong>This application was cancelled</strong>
          <span v-if="enrollment.cancel_reason">Reason: {{ enrollment.cancel_reason }}</span>
        </div>
      </div>

      <!-- Cancel Application Modal -->
      <div v-if="cancelModal.show" class="modal-overlay" @click.self="cancelModal.show = false">
        <div class="modal-content">
          <h3>Cancel Application</h3>
          <p style="color: #555; font-size: 0.9rem; margin: 0 0 1rem;">
            Cancel the application for <strong>{{ enrollment.firstName }} {{ enrollment.lastName }}</strong>? This action cannot be undone.
          </p>
          <textarea v-model="cancelModal.reason" placeholder="Reason for cancellation (required)..." rows="3" class="reject-textarea"></textarea>
          <div class="modal-actions">
            <button class="btn-cancel" @click="cancelModal.show = false">Go Back</button>
            <button class="btn-reject-action" @click="submitCancel" :disabled="!cancelModal.reason.trim()">
              Confirm Cancel
            </button>
          </div>
        </div>
      </div>

      <!-- Application Form Section -->
      <div class="section">
        <div class="section-header">
          <h3 @click="formExpanded = !formExpanded" class="section-toggle">
            {{ formExpanded ? '&#9660;' : '&#9654;' }} Application Form
          </h3>
          <div v-if="formExpanded && !editing" class="section-actions">
            <button class="btn-export" @click="downloadPdf" :disabled="pdfLoading">
              {{ pdfLoading ? 'Exporting...' : 'Export Application to PDF' }}
            </button>
            <button class="btn-edit" @click="startEdit">Edit</button>
          </div>
          <div v-if="formExpanded && editing" class="section-actions">
            <button class="btn-save" @click="saveEdit" :disabled="saving">{{ saving ? 'Saving...' : 'Save' }}</button>
            <button class="btn-cancel" @click="cancelEdit">Cancel</button>
          </div>
        </div>

        <div v-show="formExpanded" class="form-content">
          <div v-if="saveMessage" class="save-message" :class="saveMessageType">{{ saveMessage }}</div>

          <!-- Section 2: Manpower Profile -->
          <div class="form-section">
            <h2>II. Manpower Profile</h2>
            <div class="form-row three-col">
              <div class="form-group">
                <label>Last Name</label>
                <input v-model="formData.lastName" type="text" :disabled="!editing" />
              </div>
              <div class="form-group">
                <label>First Name</label>
                <input v-model="formData.firstName" type="text" :disabled="!editing" />
              </div>
              <div class="form-group">
                <label>Middle Name</label>
                <input v-model="formData.middleName" type="text" :disabled="!editing" />
              </div>
            </div>

            <h3 class="sub-heading">Complete Mailing Address</h3>
            <div class="form-row three-col">
              <div class="form-group">
                <label>Region</label>
                <input v-model="formData.region" type="text" :disabled="!editing" />
              </div>
              <div class="form-group">
                <label>Province</label>
                <input v-model="formData.province" type="text" :disabled="!editing" />
              </div>
              <div class="form-group">
                <label>City / Municipality</label>
                <input v-model="formData.city" type="text" :disabled="!editing" />
              </div>
            </div>
            <div class="form-row three-col">
              <div class="form-group">
                <label>Street No. / Street</label>
                <input v-model="formData.street" type="text" :disabled="!editing" />
              </div>
              <div class="form-group">
                <label>Barangay</label>
                <input v-model="formData.barangay" type="text" :disabled="!editing" />
              </div>
              <div class="form-group">
                <label>District</label>
                <input v-model="formData.district" type="text" disabled class="disabled-field" />
              </div>
            </div>

            <div class="form-row three-col">
              <div class="form-group">
                <label>Email Address</label>
                <input v-model="formData.email" type="email" :disabled="!editing" />
              </div>
              <div class="form-group">
                <label>Contact No.</label>
                <input v-model="formData.contactNo" type="tel" :disabled="!editing" />
              </div>
              <div class="form-group">
                <label>Nationality</label>
                <input v-model="formData.nationality" type="text" :disabled="!editing" />
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
                    <input type="radio" v-model="formData.sex" value="Male" :disabled="!editing" /> Male
                  </label>
                  <label class="radio-label">
                    <input type="radio" v-model="formData.sex" value="Female" :disabled="!editing" /> Female
                  </label>
                </div>
              </div>
              <div class="form-group">
                <label>Civil Status</label>
                <div class="radio-group">
                  <label class="radio-label">
                    <input type="radio" v-model="formData.civilStatus" value="Single" :disabled="!editing" /> Single
                  </label>
                  <label class="radio-label">
                    <input type="radio" v-model="formData.civilStatus" value="Married" :disabled="!editing" /> Married
                  </label>
                  <label class="radio-label">
                    <input type="radio" v-model="formData.civilStatus" value="Widow/er" :disabled="!editing" /> Widow/er
                  </label>
                  <label class="radio-label">
                    <input type="radio" v-model="formData.civilStatus" value="Separated" :disabled="!editing" /> Separated
                  </label>
                </div>
              </div>
            </div>

            <div class="form-group">
              <label>Employment Status (Before Training)</label>
              <div class="radio-group wrap">
                <label class="radio-label">
                  <input type="radio" v-model="formData.employmentStatus" value="Employed" :disabled="!editing" /> Employed
                </label>
                <label class="radio-label">
                  <input type="radio" v-model="formData.employmentStatus" value="Unemployed" :disabled="!editing" /> Unemployed
                </label>
                <label class="radio-label">
                  <input type="radio" v-model="formData.employmentStatus" value="Self-employed" :disabled="!editing" /> Self-employed
                </label>
              </div>
            </div>

            <div class="form-row two-col">
              <div class="form-group">
                <label>Date of Birth</label>
                <div class="date-inputs">
                  <select v-model="formData.birthMonth" :disabled="!editing">
                    <option value="">Month</option>
                    <option v-for="m in months" :key="m" :value="m">{{ m }}</option>
                  </select>
                  <select v-model="formData.birthDay" :disabled="!editing">
                    <option value="">Day</option>
                    <option v-for="d in 31" :key="d" :value="String(d)">{{ d }}</option>
                  </select>
                  <select v-model="formData.birthYear" :disabled="!editing">
                    <option value="">Year</option>
                    <option v-for="y in years" :key="y" :value="String(y)">{{ y }}</option>
                  </select>
                </div>
              </div>
              <div class="form-group">
                <label>Age</label>
                <input :value="enrollment.age || '--'" type="text" disabled class="disabled-field" />
              </div>
            </div>

            <h3 class="sub-heading">Birthplace</h3>
            <div class="form-row three-col">
              <div class="form-group">
                <label>Region</label>
                <input v-model="formData.birthplaceRegion" type="text" :disabled="!editing" />
              </div>
              <div class="form-group">
                <label>Province</label>
                <input v-model="formData.birthplaceProvince" type="text" :disabled="!editing" />
              </div>
              <div class="form-group">
                <label>City / Municipality</label>
                <input v-model="formData.birthplaceCity" type="text" :disabled="!editing" />
              </div>
            </div>
          </div>

          <!-- Educational Attainment -->
          <div class="form-section">
            <h2>Educational Attainment (Before Training)</h2>
            <div class="education-list">
              <label class="education-option" v-for="opt in educationOptions" :key="opt">
                <input type="radio" v-model="formData.educationalAttainment" :value="opt" :disabled="!editing" />
                <span class="education-label">{{ opt }}</span>
              </label>
            </div>
          </div>

          <!-- Section 4: Learner Classification -->
          <div class="form-section">
            <h2>IV. Learner / Trainee / Student (Clients) Classification</h2>
            <div class="checkbox-group">
              <label class="checkbox-label" v-for="opt in classificationOptions" :key="opt">
                <input type="checkbox" :value="opt" v-model="formData.learnerClassification" :disabled="!editing" /> {{ opt }}
              </label>
              <div class="others-field">
                <label class="checkbox-label">
                  <input type="checkbox" value="Others" v-model="formData.learnerClassification" :disabled="!editing" /> Others (pls. specify)
                </label>
                <input
                  v-if="formData.learnerClassification.includes('Others')"
                  v-model="formData.classificationOther"
                  type="text"
                  placeholder="Please specify"
                  class="others-input"
                  :disabled="!editing"
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
                    <input type="radio" v-model="formData.ncaeTaken" :value="true" :disabled="!editing" /> Yes
                  </label>
                  <label class="radio-label">
                    <input type="radio" v-model="formData.ncaeTaken" :value="false" :disabled="!editing" /> No
                  </label>
                </div>
              </div>
            </div>
            <div class="form-row two-col" v-if="formData.ncaeTaken">
              <div class="form-group">
                <label>Where?</label>
                <input v-model="formData.ncaeWhere" type="text" :disabled="!editing" />
              </div>
              <div class="form-group">
                <label>When?</label>
                <input v-model="formData.ncaeWhen" type="text" :disabled="!editing" />
              </div>
            </div>
          </div>

          <!-- Section 6: Course/Qualification -->
          <div class="form-section">
            <h2>VI. Course / Qualification</h2>
            <div class="form-group">
              <label>Course</label>
              <select v-model="formData.course" :disabled="!editing" class="course-select">
                <option value="">-- Select a course --</option>
                <option v-for="c in courses" :key="c.slug" :value="c.title">{{ c.title }}</option>
                <option v-if="formData.course && !courses.find(c => c.title === formData.course)" :value="formData.course">{{ formData.course }}</option>
              </select>
            </div>
          </div>

          <!-- Section 7: Certification -->
          <div class="form-section">
            <h2>VII. Certification</h2>
            <label class="checkbox-label certification-check">
              <input type="checkbox" v-model="formData.certificationAgreed" disabled />
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
                  <input type="radio" v-model="formData.applyScholarship" :value="true" :disabled="!editing" /> Yes
                </label>
                <label class="radio-label">
                  <input type="radio" v-model="formData.applyScholarship" :value="false" :disabled="!editing" /> No
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Documents Section -->
      <div class="section">
        <div class="section-header">
          <h3 @click="docsExpanded = !docsExpanded" class="section-toggle">
            {{ docsExpanded ? '&#9660;' : '&#9654;' }} Documents
          </h3>
        </div>

        <div v-show="docsExpanded" class="docs-content">
          <div class="docs-grid">
            <div class="doc-card" v-for="(info, docType) in documentTypes" :key="docType">
              <div class="doc-card-header">
                <span class="doc-name">{{ info.label }}</span>
                <span class="doc-badge" :class="info.required ? 'badge-required' : 'badge-optional'">
                  {{ info.required ? 'Required' : 'Optional' }}
                </span>
              </div>

              <div class="doc-review-bar" v-if="getDocReviewStatus(docType) !== 'pending'">
                <span class="doc-status-badge" :class="'doc-status-' + getDocReviewStatus(docType)">
                  {{ formatDocStatus(getDocReviewStatus(docType)) }}
                </span>
                <span v-if="getDocRejectReason(docType)" class="reject-reason">
                  {{ getDocRejectReason(docType) }}
                </span>
              </div>

              <div class="doc-slots">
                <!-- Applicant Upload Slot -->
                <div class="doc-slot" v-if="info.official_only"></div>
                <div class="doc-slot" v-else>
                  <span class="slot-label">Applicant Upload</span>
                  <div v-if="documents[docType]?.applicant_upload" class="slot-file">
                    <a :href="documents[docType].applicant_upload.file_url" target="_blank" class="file-link">
                      {{ documents[docType].applicant_upload.file_name }}
                    </a>
                    <span class="file-meta">{{ formatDate(documents[docType].applicant_upload.uploaded_at) }}</span>
                    <button class="btn-delete-doc" @click="handleDelete(docType, 'applicant')" :disabled="deleting[`${docType}_applicant`]">
                      &#10005;
                    </button>
                  </div>
                  <div v-else class="slot-empty">
                    <label class="upload-label" :class="{ disabled: uploading[`${docType}_applicant`] }">
                      <input type="file" class="file-input" @change="handleUpload($event, docType, 'applicant')" :disabled="uploading[`${docType}_applicant`]" />
                      {{ uploading[`${docType}_applicant`] ? 'Uploading...' : 'Upload' }}
                    </label>
                  </div>
                </div>

                <!-- Official Scan Slot -->
                <div class="doc-slot">
                  <span class="slot-label">Official Scan</span>
                  <div v-if="documents[docType]?.official_scan" class="slot-file">
                    <a :href="documents[docType].official_scan.file_url" target="_blank" class="file-link">
                      {{ documents[docType].official_scan.file_name }}
                    </a>
                    <span class="file-meta">{{ formatDate(documents[docType].official_scan.uploaded_at) }}</span>
                    <button class="btn-delete-doc" @click="handleDelete(docType, 'official')" :disabled="deleting[`${docType}_official`]">
                      &#10005;
                    </button>
                  </div>
                  <div v-else class="slot-empty">
                    <label class="upload-label" :class="{ disabled: uploading[`${docType}_official`] }">
                      <input type="file" class="file-input" @change="handleUpload($event, docType, 'official')" :disabled="uploading[`${docType}_official`]" />
                      {{ uploading[`${docType}_official`] ? 'Uploading...' : 'Upload' }}
                    </label>
                  </div>
                </div>
              </div>

              <div class="doc-review-actions" v-if="hasAnyFile(docType)">
                <button class="btn-accept" @click="reviewDoc(docType, 'accepted')"
                  :disabled="getDocReviewStatus(docType) === 'accepted'">
                  Accept
                </button>
                <button class="btn-reject-action" @click="openRejectModal(docType)"
                  :disabled="getDocReviewStatus(docType) === 'rejected'">
                  Reject
                </button>
              </div>
            </div>
          </div>

          <!-- Supporting Documents -->
          <h4 style="margin: 1.5rem 0 0.75rem; color: #333;">Additional Supporting Documents</h4>
          <div class="supporting-docs">
            <div class="supporting-upload">
              <label class="upload-label" :class="{ disabled: supportingUploading }">
                <input type="file" class="file-input" @change="handleSupportingUpload" :disabled="supportingUploading" multiple />
                {{ supportingUploading ? 'Uploading...' : 'Upload Files' }}
              </label>
            </div>
            <div v-if="supportingDocuments.length === 0" class="supporting-empty">No supporting documents uploaded.</div>
            <div v-else class="supporting-list">
              <div v-for="(doc, idx) in supportingDocuments" :key="idx" class="supporting-item">
                <a :href="doc.file_url" target="_blank" class="file-link">{{ doc.file_name }}</a>
                <span class="file-meta">{{ formatDate(doc.uploaded_at) }}</span>
                <button class="btn-delete-doc" @click="handleSupportingDelete(doc.gcs_path)" :disabled="supportingDeleting[doc.gcs_path]">
                  &#10005;
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Reject Modal -->
      <div v-if="rejectModal.show" class="modal-overlay" @click.self="rejectModal.show = false">
        <div class="modal-content">
          <h3>Reject Document: {{ documentTypes[rejectModal.docType]?.label }}</h3>
          <textarea v-model="rejectModal.reason" placeholder="Reason for rejection..." rows="3" class="reject-textarea"></textarea>
          <div class="modal-actions">
            <button class="btn-cancel" @click="rejectModal.show = false">Cancel</button>
            <button class="btn-reject-action" @click="submitReject" :disabled="!rejectModal.reason.trim()">
              Confirm Reject
            </button>
          </div>
        </div>
      </div>

      <!-- Email History Section -->
      <div class="section" v-if="emailsSent.length > 0">
        <div class="section-header">
          <h3 @click="emailsExpanded = !emailsExpanded" class="section-toggle">
            {{ emailsExpanded ? '&#9660;' : '&#9654;' }} Email History ({{ emailsSent.length }})
          </h3>
        </div>
        <div v-show="emailsExpanded" class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Type</th>
                <th>Subject</th>
                <th>Triggered By</th>
                <th>Sent At</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(entry, i) in emailsSent" :key="i">
                <td><span class="email-type-badge" :class="'email-type-' + entry.type">{{ formatEmailType(entry.type) }}</span></td>
                <td>{{ entry.subject }}</td>
                <td>{{ entry.triggered_by || 'system' }}</td>
                <td>{{ formatDate(entry.sent_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Changelog Section -->
      <div class="section" v-if="changelog.length > 0">
        <div class="section-header">
          <h3 @click="changelogExpanded = !changelogExpanded" class="section-toggle">
            {{ changelogExpanded ? '&#9660;' : '&#9654;' }} Change Log ({{ changelog.length }})
          </h3>
        </div>
        <div v-show="changelogExpanded" class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Field</th>
                <th>Old Value</th>
                <th>New Value</th>
                <th>Changed By</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(entry, i) in changelog" :key="i">
                <td>{{ formatFieldName(entry.field) }}</td>
                <td class="old-value">{{ entry.oldValue || '--' }}</td>
                <td class="new-value">{{ entry.newValue || '--' }}</td>
                <td>{{ entry.updatedBy }}</td>
                <td>{{ formatDate(entry.updatedAt) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getEnrollment, updateEnrollment, exportEnrollmentPdf, getCourses, getCoursesSummary, getDocuments, uploadDocument, deleteDocument, reviewDocument, uploadSupportingDocument, deleteSupportingDocument, sendInterviewSchedule, completeEnrollment, removeFromBatch, archiveEnrollment, unarchiveEnrollment, cancelEnrollment, getSponsors } from '../services/api'

const route = useRoute()
const router = useRouter()

const enrollment = ref(null)
const loading = ref(true)
const editing = ref(false)
const saving = ref(false)
const pdfLoading = ref(false)
const actionLoading = ref(false)
const saveMessage = ref('')
const saveMessageType = ref('success')
const formExpanded = ref(true)
const docsExpanded = ref(true)
const changelogExpanded = ref(true)
const emailsExpanded = ref(true)
const courses = ref([])
const coursesSummary = ref([])
const sponsors = ref([])
const sponsorValue = ref('')
const documentTypes = ref({})
const documents = ref({})
const uploading = ref({})
const deleting = ref({})
const supportingDocuments = ref([])
const supportingUploading = ref(false)
const supportingDeleting = ref({})
const statusValue = ref('')
const rejectModal = reactive({ show: false, docType: '', reason: '' })
const cancelModal = reactive({ show: false, reason: '' })

const enrollmentStatuses = [
  { value: 'pending_upload', label: 'Pending Upload of Required Documents' },
  { value: 'pending_review', label: 'Pending Document Review' },
  { value: 'documents_rejected', label: 'Documents Rejected' },
  { value: 'in_waitlist', label: 'In Waitlist' },
  { value: 'physical_docs_required', label: 'Physical Documents Required' },
  { value: 'waiting_for_class_start', label: 'Waiting for Class Start' },
  { value: 'completed', label: 'Completed' },
  { value: 'archived', label: 'Archived' },
  { value: 'withdrawn', label: 'Withdrawn' },
  { value: 'cancelled', label: 'Cancelled' },
]

// Statuses where the dropdown is editable (before workflow buttons take over)
const earlyStatuses = enrollmentStatuses.filter(s =>
  ['pending_upload', 'pending_review', 'documents_rejected'].includes(s.value)
)

const isEarlyStatus = computed(() =>
  ['pending_upload', 'pending_review', 'documents_rejected', 'pending'].includes(statusValue.value)
)

const canCancel = computed(() =>
  ['pending', 'pending_upload', 'pending_review', 'documents_rejected', 'in_waitlist', 'physical_docs_required', 'waiting_for_class_start'].includes(statusValue.value)
)

const activeBatchInfo = computed(() => {
  if (!enrollment.value?.course) return null
  const courseName = enrollment.value.course
  const summary = coursesSummary.value.find(c => c.title === courseName)
  if (!summary || !summary.active_batch_status) return null
  return {
    startDate: summary.current_start_date || 'TBA',
    courseName: summary.title,
  }
})

function formatStatusLabel(value) {
  return enrollmentStatuses.find(s => s.value === value)?.label || value
}

const editSnapshot = ref({})

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

const allFormKeys = [
  'lastName', 'firstName', 'middleName',
  'street', 'barangay', 'district', 'city', 'province', 'region',
  'email', 'contactNo', 'nationality',
  'sex', 'civilStatus', 'employmentStatus',
  'birthMonth', 'birthDay', 'birthYear',
  'birthplaceCity', 'birthplaceProvince', 'birthplaceRegion',
  'educationalAttainment',
  'learnerClassification', 'classificationOther',
  'ncaeTaken', 'ncaeWhere', 'ncaeWhen',
  'course',
  'certificationAgreed', 'applyScholarship',
]

const formData = reactive({
  lastName: '', firstName: '', middleName: '',
  street: '', barangay: '', district: '', city: '', province: '', region: '',
  email: '', contactNo: '', nationality: '',
  sex: '', civilStatus: '', employmentStatus: '',
  birthMonth: '', birthDay: '', birthYear: '',
  birthplaceCity: '', birthplaceProvince: '', birthplaceRegion: '',
  educationalAttainment: '',
  learnerClassification: [], classificationOther: '',
  ncaeTaken: false, ncaeWhere: '', ncaeWhen: '',
  course: '',
  certificationAgreed: false, applyScholarship: false,
})

function populateFormData(data) {
  for (const key of allFormKeys) {
    if (key === 'learnerClassification') {
      formData[key] = Array.isArray(data[key]) ? [...data[key]] : []
    } else {
      formData[key] = data[key] ?? ''
    }
  }
}

const changelog = computed(() => {
  const log = enrollment.value?.changelog || []
  return [...log].reverse()
})

const emailsSent = computed(() => {
  const emails = enrollment.value?.emails_sent || []
  return [...emails].reverse()
})

function formatEmailType(type) {
  const map = {
    application_submitted: 'Application Submitted',
    interview_schedule: 'Interview Schedule',
    enrollment_completed: 'Enrollment Completed',
    document_rejected: 'Document Rejected',
    documents_accepted: 'Documents Accepted',
    application_withdrawn: 'Application Withdrawn',
  }
  return map[type] || type
}

function startEdit() {
  const snapshot = {}
  for (const key of allFormKeys) {
    if (key === 'learnerClassification') {
      snapshot[key] = [...formData[key]]
    } else {
      snapshot[key] = formData[key]
    }
  }
  editSnapshot.value = snapshot
  editing.value = true
  saveMessage.value = ''
}

function cancelEdit() {
  editing.value = false
  saveMessage.value = ''
  if (enrollment.value) {
    populateFormData(enrollment.value)
  }
}

async function saveEdit() {
  saving.value = true
  saveMessage.value = ''
  try {
    const changes = {}
    for (const key of allFormKeys) {
      const oldVal = editSnapshot.value[key]
      const newVal = formData[key]
      if (key === 'learnerClassification') {
        if (JSON.stringify(oldVal) !== JSON.stringify(newVal)) {
          changes[key] = [...newVal]
        }
      } else {
        if (String(newVal ?? '') !== String(oldVal ?? '')) {
          changes[key] = newVal
        }
      }
    }
    if (Object.keys(changes).length === 0) {
      saveMessage.value = 'No changes detected'
      saveMessageType.value = 'info'
      editing.value = false
      return
    }
    const result = await updateEnrollment(route.params.id, changes)
    saveMessage.value = result.message || 'Changes saved'
    saveMessageType.value = 'success'
    editing.value = false
    await loadEnrollment()
  } catch (e) {
    console.error('Failed to save:', e)
    saveMessage.value = 'Failed to save changes. Please try again.'
    saveMessageType.value = 'error'
  } finally {
    saving.value = false
  }
}

async function downloadPdf() {
  pdfLoading.value = true
  try {
    await exportEnrollmentPdf(route.params.id)
  } catch (e) {
    console.error('Failed to export PDF:', e)
    alert('Failed to export PDF. Please try again.')
  } finally {
    pdfLoading.value = false
  }
}

function formatDate(dateStr) {
  if (!dateStr) return '--'
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-PH', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function formatFieldName(key) {
  return key.replace(/([A-Z])/g, ' $1').replace(/^./, s => s.toUpperCase())
}

async function handleStatusChange() {
  try {
    await updateEnrollment(route.params.id, { status: statusValue.value })
    await loadEnrollment()
  } catch (e) {
    console.error('Failed to update status:', e)
    alert('Failed to update status')
    statusValue.value = enrollment.value?.status || 'pending_upload'
  }
}

async function handleSendInterview() {
  if (!confirm(`Send interview schedule email to ${enrollment.value.firstName} ${enrollment.value.lastName} (${enrollment.value.email})?`)) return
  actionLoading.value = true
  try {
    await sendInterviewSchedule(route.params.id)
    alert('Interview schedule email sent successfully.')
    await loadEnrollment()
  } catch (e) {
    const msg = e.response?.data?.detail || 'Failed to send interview schedule.'
    alert(msg)
  } finally {
    actionLoading.value = false
  }
}

async function handleCompleteEnrollment() {
  const batchInfo = activeBatchInfo.value
  const startDate = batchInfo?.startDate || 'TBA'
  if (!confirm(`Assign ${enrollment.value.firstName} ${enrollment.value.lastName} to the current batch (start date: ${startDate})? This will send a confirmation email and promote them to a student account.`)) return
  actionLoading.value = true
  try {
    await completeEnrollment(route.params.id)
    alert('Student assigned to batch successfully.')
    await loadEnrollment()
  } catch (e) {
    const msg = e.response?.data?.detail || 'Failed to assign to batch.'
    alert(msg)
  } finally {
    actionLoading.value = false
  }
}

async function handleRemoveFromBatch() {
  if (!confirm(`Remove ${enrollment.value.firstName} ${enrollment.value.lastName} from their current batch? They will be moved back to "Waiting for Class Start" and notified by email.`)) return
  actionLoading.value = true
  try {
    await removeFromBatch(route.params.id)
    alert('Student removed from batch.')
    await loadEnrollment()
  } catch (e) {
    const msg = e.response?.data?.detail || 'Failed to remove from batch.'
    alert(msg)
  } finally {
    actionLoading.value = false
  }
}

async function handleArchive() {
  if (!confirm(`Archive the application for ${enrollment.value.firstName} ${enrollment.value.lastName}? This will hide it from the dashboard and the applicant's tracker.`)) return
  actionLoading.value = true
  try {
    await archiveEnrollment(route.params.id)
    await loadEnrollment()
  } catch (e) {
    const msg = e.response?.data?.detail || 'Failed to archive.'
    alert(msg)
  } finally {
    actionLoading.value = false
  }
}

async function handleUnarchive() {
  actionLoading.value = true
  try {
    await unarchiveEnrollment(route.params.id)
    await loadEnrollment()
  } catch (e) {
    const msg = e.response?.data?.detail || 'Failed to unarchive.'
    alert(msg)
  } finally {
    actionLoading.value = false
  }
}

function openCancelModal() {
  cancelModal.reason = ''
  cancelModal.show = true
}

async function submitCancel() {
  actionLoading.value = true
  cancelModal.show = false
  try {
    await cancelEnrollment(route.params.id, cancelModal.reason)
    await loadEnrollment()
  } catch (e) {
    const msg = e.response?.data?.detail || 'Failed to cancel application.'
    alert(msg)
  } finally {
    actionLoading.value = false
  }
}

function getDocReviewStatus(docType) {
  return documents.value[docType]?.review?.status || 'pending'
}

function getDocRejectReason(docType) {
  return documents.value[docType]?.review?.reject_reason || ''
}

function hasAnyFile(docType) {
  const d = documents.value[docType]
  return !!(d?.applicant_upload || d?.official_scan)
}

function formatDocStatus(status) {
  const map = { pending: 'Pending', uploaded: 'Uploaded - Needs Admin Review', accepted: 'Accepted', rejected: 'Rejected' }
  return map[status] || status
}

function openRejectModal(docType) {
  rejectModal.docType = docType
  rejectModal.reason = ''
  rejectModal.show = true
}

async function submitReject() {
  await reviewDoc(rejectModal.docType, 'rejected', rejectModal.reason)
  rejectModal.show = false
}

async function reviewDoc(docType, status, rejectReason = null) {
  try {
    await reviewDocument(route.params.id, docType, status, rejectReason)
    await loadDocuments()
    await loadEnrollment()
  } catch (e) {
    console.error('Failed to review document:', e)
    alert('Failed to review document. Please try again.')
  }
}

async function loadDocuments() {
  try {
    const data = await getDocuments(route.params.id)
    documentTypes.value = data.document_types || {}
    documents.value = data.documents || {}
    supportingDocuments.value = data.supporting_documents || []
  } catch (e) {
    console.error('Failed to load documents:', e)
  }
}

async function handleSupportingUpload(event) {
  const files = event.target.files
  if (!files || files.length === 0) return
  supportingUploading.value = true
  try {
    for (const file of files) {
      await uploadSupportingDocument(route.params.id, file)
    }
    await loadDocuments()
  } catch (e) {
    console.error('Failed to upload supporting document:', e)
    alert('Failed to upload supporting document. Please try again.')
  } finally {
    supportingUploading.value = false
    event.target.value = ''
  }
}

async function handleSupportingDelete(gcsPath) {
  if (!confirm('Delete this supporting document?')) return
  supportingDeleting.value[gcsPath] = true
  try {
    await deleteSupportingDocument(route.params.id, gcsPath)
    await loadDocuments()
  } catch (e) {
    console.error('Failed to delete supporting document:', e)
    alert('Failed to delete supporting document. Please try again.')
  } finally {
    supportingDeleting.value[gcsPath] = false
  }
}

async function handleUpload(event, docType, source) {
  const file = event.target.files?.[0]
  if (!file) return
  const key = `${docType}_${source}`
  uploading.value[key] = true
  try {
    await uploadDocument(route.params.id, docType, file, source)
    await loadDocuments()
    await loadEnrollment()
  } catch (e) {
    console.error('Failed to upload document:', e)
    alert('Failed to upload document. Please try again.')
  } finally {
    uploading.value[key] = false
    event.target.value = ''
  }
}

async function handleDelete(docType, source) {
  if (!confirm('Delete this document?')) return
  const key = `${docType}_${source}`
  deleting.value[key] = true
  try {
    await deleteDocument(route.params.id, docType, source)
    await loadDocuments()
  } catch (e) {
    console.error('Failed to delete document:', e)
    alert('Failed to delete document. Please try again.')
  } finally {
    deleting.value[key] = false
  }
}

async function loadEnrollment() {
  try {
    enrollment.value = await getEnrollment(route.params.id)
    // Map legacy "pending" to "pending_upload" for the dropdown
    statusValue.value = enrollment.value.status === 'pending' ? 'pending_upload' : (enrollment.value.status || 'pending_upload')
    sponsorValue.value = enrollment.value.sponsor_id || ''
    populateFormData(enrollment.value)
  } catch (e) {
    console.error('Failed to load enrollment:', e)
    enrollment.value = null
  } finally {
    loading.value = false
  }
}

async function handleSponsorChange() {
  const newId = sponsorValue.value
  const sponsor = sponsors.value.find(s => s.id === newId)
  try {
    await updateEnrollment(route.params.id, {
      sponsor_id: newId || '',
      sponsor_name: sponsor?.name || '',
    })
    await loadEnrollment()
  } catch (e) {
    console.error('Failed to update sponsor:', e)
    alert('Failed to assign sponsor')
    sponsorValue.value = enrollment.value?.sponsor_id || ''
  }
}

onMounted(async () => {
  loadEnrollment()
  loadDocuments()
  try {
    courses.value = await getCourses()
  } catch (e) {
    console.error('Failed to load courses:', e)
  }
  try {
    coursesSummary.value = await getCoursesSummary()
  } catch (e) {
    console.error('Failed to load courses summary:', e)
  }
  try {
    sponsors.value = await getSponsors()
  } catch (e) {
    console.error('Failed to load sponsors:', e)
  }
})
</script>

<style scoped>
.application-detail {
  max-width: 1000px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.btn-back {
  padding: 0.4rem 1rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: #666;
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-back:hover {
  background: #f5f5f5;
  border-color: #ccc;
}

.btn-export {
  padding: 0.5rem 1.25rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: #1a5fa4;
  background: #e8f0fe;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-export:hover:not(:disabled) { background: #d0e2fc; }
.btn-export:disabled { opacity: 0.6; cursor: not-allowed; }

.loading-state,
.empty-state {
  text-align: center;
  color: #999;
  padding: 3rem;
  background: white;
  border-radius: 12px;
}

.summary-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.summary-info h2 { font-size: 1.25rem; color: #1a1a2e; margin-bottom: 0.25rem; }
.summary-meta { font-size: 0.85rem; color: #666; }

.status-badge {
  display: inline-block;
  padding: 0.3rem 0.8rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.status-pending, .status-pending_upload { background: #fff3cd; color: #856404; }
.status-approved, .status-in_waitlist { background: #d4edda; color: #155724; }
.status-rejected, .status-documents_rejected { background: #f8d7da; color: #721c24; }
.status-pending_review { background: #e3f2fd; color: #1565c0; }
.status-physical_docs_required { background: #e8f0fe; color: #1a5fa4; }
.status-waiting_for_class_start { background: #fef3c7; color: #92400e; }
.status-completed { background: #c8e6c9; color: #1b5e20; }
.status-archived { background: #e0e0e0; color: #616161; }
.status-withdrawn { background: #fef2f2; color: #991b1b; }
.status-cancelled { background: #fef2f2; color: #991b1b; }

.status-select {
  padding: 0.3rem 0.8rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  border: none;
  cursor: pointer;
  appearance: auto;
}

.section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  margin-bottom: 1.5rem;
}

.section-header { display: flex; justify-content: space-between; align-items: center; }

.section-toggle {
  font-size: 1rem;
  font-weight: 700;
  color: #1a1a2e;
  cursor: pointer;
  user-select: none;
}

.section-toggle:hover { color: #1a5fa4; }
.section-actions { display: flex; gap: 0.5rem; }

.btn-edit {
  padding: 0.35rem 1rem;
  font-size: 0.8rem;
  font-weight: 600;
  color: #1a5fa4;
  background: #e8f0fe;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-edit:hover { background: #d0e2fc; }

.btn-save {
  padding: 0.35rem 1rem;
  font-size: 0.8rem;
  font-weight: 600;
  color: white;
  background: #1a5fa4;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-save:hover:not(:disabled) { background: #154d87; }
.btn-save:disabled { opacity: 0.6; cursor: not-allowed; }

.btn-cancel {
  padding: 0.35rem 1rem;
  font-size: 0.8rem;
  font-weight: 600;
  color: #666;
  background: #f0f0f0;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-cancel:hover { background: #e0e0e0; }

.save-message { padding: 0.6rem 1rem; border-radius: 6px; font-size: 0.85rem; margin: 0 0 1rem; }
.save-message.success { background: #d4edda; color: #155724; }
.save-message.error { background: #f8d7da; color: #721c24; }
.save-message.info { background: #e8f0fe; color: #1a5fa4; }

.form-content {
  margin-top: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* ── Form styles (matching Apply.vue) ── */

.form-section {
  background: #fafbff;
  border-radius: 12px;
  padding: 2rem;
  border: 1px solid #e8f0fe;
}

.form-section h2 {
  font-size: 1.05rem;
  font-weight: 700;
  color: #1a5fa4;
  margin-bottom: 1.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #e8f0fe;
}

.sub-heading {
  font-size: 0.9rem;
  font-weight: 600;
  color: #444;
  margin: 1.75rem 0 1rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
  margin-bottom: 1.25rem;
}

.form-row.three-col { grid-template-columns: 1fr 1fr 1fr; }
.form-row.two-col { grid-template-columns: 1fr 1fr; }

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

.form-group input:disabled,
.form-group select:disabled {
  background: #f8f9fa;
  color: #333;
  cursor: default;
  border-color: #e0e0e0;
}

.disabled-field {
  background: #f5f5f5 !important;
  color: #999 !important;
  cursor: not-allowed !important;
}

.date-inputs { display: flex; gap: 0.5rem; }

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

.date-inputs select:disabled {
  background: #f8f9fa;
  color: #333;
  cursor: default;
  border-color: #e0e0e0;
}

.radio-group { display: flex; gap: 1.5rem; flex-wrap: wrap; padding: 0.5rem 0; }
.radio-group.wrap { gap: 1rem 1.75rem; }

.radio-label {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.85rem;
  color: #444;
  cursor: pointer;
}

.radio-label input[type="radio"] { accent-color: #1a5fa4; }
.radio-label input[type="radio"]:disabled { cursor: default; }

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

.checkbox-label input[type="checkbox"] { accent-color: #1a5fa4; margin-top: 2px; }
.checkbox-label input[type="checkbox"]:disabled { cursor: default; }

.others-field { display: flex; flex-direction: column; gap: 0.5rem; }

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

.others-input:disabled {
  background: #f8f9fa;
  color: #333;
  cursor: default;
  border-color: #e0e0e0;
}

.certification-check { line-height: 1.6; font-size: 0.9rem; }
.course-select { max-width: 500px; }

.education-list { display: flex; flex-direction: column; gap: 0; }

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

.education-option:first-child { border-radius: 10px 10px 0 0; }
.education-option:last-child { border-radius: 0 0 10px 10px; }
.education-option:hover { background: #f0f5ff; }

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

/* ── Changelog table ── */

.table-container { overflow-x: auto; margin-top: 1rem; }

.data-table { width: 100%; border-collapse: collapse; }

.data-table th,
.data-table td {
  padding: 0.6rem 0.75rem;
  text-align: left;
  border-bottom: 1px solid #eee;
  font-size: 0.85rem;
}

.data-table th {
  font-size: 0.75rem;
  font-weight: 600;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.old-value { color: #c0392b; }
.new-value { color: #27ae60; }

.status-badge-large {
  display: inline-block;
  padding: 0.4rem 1rem;
  border-radius: 12px;
  font-size: 0.82rem;
  font-weight: 600;
  white-space: nowrap;
}

/* ── Sponsor assignment ── */

.sponsor-assign {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
  padding: 0.75rem 1rem;
  background: white;
  border-radius: 10px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.sponsor-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #555;
  white-space: nowrap;
}

.sponsor-select {
  padding: 0.4rem 0.75rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 0.85rem;
  color: #333;
  background: white;
  cursor: pointer;
  min-width: 200px;
}

.sponsor-select:focus {
  outline: none;
  border-color: #1a5fa4;
}

/* ── Workflow actions ── */

.workflow-banner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.5rem;
  border-radius: 12px;
  margin-bottom: 1.5rem;
}

.workflow-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.workflow-text strong {
  font-size: 0.9rem;
}

.workflow-text span {
  font-size: 0.8rem;
  opacity: 0.85;
}

.workflow-hint {
  font-size: 0.75rem !important;
  font-style: italic;
  opacity: 0.7 !important;
  margin-top: 4px;
}

.workflow-interview {
  background: #eff6ff;
  color: #1e40af;
  border: 1px solid #bfdbfe;
}

.workflow-complete {
  background: #f0fdf4;
  color: #166534;
  border: 1px solid #bbf7d0;
}

.btn-workflow {
  padding: 0.5rem 1.25rem;
  font-size: 0.8rem;
  font-weight: 600;
  color: white;
  background: #1a5fa4;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.2s;
}

.btn-workflow:hover:not(:disabled) { background: #154d87; }
.btn-workflow:disabled { opacity: 0.6; cursor: not-allowed; }

.btn-workflow-green {
  background: #16a34a;
}

.btn-workflow-green:hover:not(:disabled) { background: #15803d; }

.btn-workflow-orange {
  background: #ea580c;
}

.btn-workflow-orange:hover:not(:disabled) { background: #c2410c; }

.workflow-done {
  background: #f0fdf4;
  color: #166534;
  border: 1px solid #bbf7d0;
}

.workflow-archived {
  background: #f5f5f5;
  color: #616161;
  border: 1px solid #e0e0e0;
}

.workflow-withdrawn {
  background: #fef2f2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.workflow-cancelled {
  background: #fefce8;
  color: #92400e;
  border: 1px solid #fde68a;
}

.btn-cancel-app {
  padding: 0.4rem 1rem;
  font-size: 0.8rem;
  font-weight: 600;
  color: #b91c1c;
  background: #fee2e2;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-cancel-app:hover:not(:disabled) { background: #fecaca; }
.btn-cancel-app:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-archive {
  padding: 0.4rem 1rem;
  font-size: 0.8rem;
  font-weight: 600;
  color: #616161;
  background: #e0e0e0;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-archive:hover:not(:disabled) { background: #ccc; }
.btn-archive:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-unarchive {
  padding: 0.4rem 1rem;
  font-size: 0.8rem;
  font-weight: 600;
  color: #1a5fa4;
  background: #e8f0fe;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-unarchive:hover:not(:disabled) { background: #d0e2fc; }
.btn-unarchive:disabled { opacity: 0.5; cursor: not-allowed; }

/* ── Email history ── */

.email-type-badge {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  border-radius: 10px;
  font-size: 0.7rem;
  font-weight: 600;
  white-space: nowrap;
}

.email-type-application_submitted { background: #e8f0fe; color: #1a5fa4; }
.email-type-interview_schedule { background: #fff3cd; color: #856404; }
.email-type-enrollment_completed { background: #c8e6c9; color: #1b5e20; }
.email-type-document_rejected { background: #f8d7da; color: #721c24; }
.email-type-documents_accepted { background: #d4edda; color: #155724; }

/* ── Documents section ── */

.docs-content { margin-top: 1.25rem; }

.supporting-docs {
  margin-top: 1rem;
}

.supporting-upload {
  margin-bottom: 1rem;
}

.supporting-empty {
  color: #999;
  font-size: 0.85rem;
  padding: 0.5rem 0;
}

.supporting-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.supporting-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0.75rem;
  background: #fafbff;
  border: 1px solid #e8f0fe;
  border-radius: 6px;
  font-size: 0.85rem;
}

.supporting-item .file-link {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.docs-grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.doc-card {
  background: #fafbff;
  border: 1px solid #e8f0fe;
  border-radius: 10px;
  overflow: hidden;
}

.doc-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1.25rem;
  background: #f0f5ff;
  border-bottom: 1px solid #e8f0fe;
}

.doc-name {
  font-size: 0.9rem;
  font-weight: 600;
  color: #1a1a2e;
}

.doc-badge {
  font-size: 0.7rem;
  font-weight: 600;
  padding: 0.2rem 0.6rem;
  border-radius: 10px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.badge-required { background: #fff3cd; color: #856404; }
.badge-optional { background: #e8f0fe; color: #1a5fa4; }

.doc-slots {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1px;
  background: #e8f0fe;
}

.doc-slot {
  padding: 0.75rem 1.25rem;
  background: white;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.slot-label {
  font-size: 0.7rem;
  font-weight: 600;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.slot-file {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.file-link {
  font-size: 0.82rem;
  color: #1a5fa4;
  text-decoration: none;
  word-break: break-all;
}

.file-link:hover { text-decoration: underline; }

.file-meta {
  font-size: 0.7rem;
  color: #999;
}

.btn-delete-doc {
  background: none;
  border: none;
  color: #c0392b;
  font-size: 0.85rem;
  cursor: pointer;
  padding: 0.15rem 0.35rem;
  border-radius: 4px;
  line-height: 1;
  transition: background 0.15s;
  margin-left: auto;
}

.btn-delete-doc:hover:not(:disabled) { background: #fde8e8; }
.btn-delete-doc:disabled { opacity: 0.4; cursor: not-allowed; }

.slot-empty {
  display: flex;
  align-items: center;
}

.upload-label {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.35rem 0.85rem;
  font-size: 0.8rem;
  font-weight: 600;
  color: #1a5fa4;
  background: #e8f0fe;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.upload-label:hover:not(.disabled) { background: #d0e2fc; }
.upload-label.disabled { opacity: 0.6; cursor: not-allowed; }

.file-input {
  display: none;
}

/* ── Document review ── */

.doc-review-bar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 1.25rem;
  background: #fafbff;
  border-bottom: 1px solid #e8f0fe;
}

.doc-status-badge {
  font-size: 0.7rem;
  font-weight: 600;
  padding: 0.2rem 0.6rem;
  border-radius: 10px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.doc-status-uploaded { background: #fff3cd; color: #856404; }
.doc-status-accepted { background: #d4edda; color: #155724; }
.doc-status-rejected { background: #f8d7da; color: #721c24; }

.reject-reason {
  font-size: 0.8rem;
  color: #721c24;
  font-style: italic;
}

.doc-review-actions {
  display: flex;
  gap: 0.5rem;
  padding: 0.6rem 1.25rem;
  border-top: 1px solid #e8f0fe;
}

.btn-accept {
  padding: 0.3rem 0.85rem;
  font-size: 0.78rem;
  font-weight: 600;
  color: #155724;
  background: #d4edda;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-accept:hover:not(:disabled) { background: #b7dfc5; }
.btn-accept:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-reject-action {
  padding: 0.3rem 0.85rem;
  font-size: 0.78rem;
  font-weight: 600;
  color: #721c24;
  background: #f8d7da;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-reject-action:hover:not(:disabled) { background: #f1b5bb; }
.btn-reject-action:disabled { opacity: 0.5; cursor: not-allowed; }

/* ── Reject modal ── */

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  max-width: 450px;
  width: 90%;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
}

.modal-content h3 {
  font-size: 1rem;
  color: #1a1a2e;
  margin-bottom: 1rem;
}

.reject-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1.5px solid #ddd;
  border-radius: 8px;
  font-size: 0.9rem;
  font-family: inherit;
  resize: vertical;
  margin-bottom: 1rem;
}

.reject-textarea:focus {
  outline: none;
  border-color: #c0392b;
  box-shadow: 0 0 0 3px rgba(192, 57, 43, 0.1);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

@media (max-width: 768px) {
  .form-row,
  .form-row.three-col,
  .form-row.two-col {
    grid-template-columns: 1fr;
  }

  .checkbox-group { grid-template-columns: 1fr; }
  .form-section { padding: 1.25rem; }
  .doc-slots { grid-template-columns: 1fr; }

  .summary-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }

  .detail-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }
}
</style>
