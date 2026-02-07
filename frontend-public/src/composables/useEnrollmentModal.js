import { ref } from 'vue'

const isOpen = ref(false)
const prefilledCourse = ref('')

export function useEnrollmentModal() {
  function open(courseName = '') {
    prefilledCourse.value = courseName
    isOpen.value = true
  }

  function close() {
    isOpen.value = false
    prefilledCourse.value = ''
  }

  return { isOpen, prefilledCourse, open, close }
}
