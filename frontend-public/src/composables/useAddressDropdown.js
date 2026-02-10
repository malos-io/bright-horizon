import { ref, computed, watch } from 'vue'
import { addressData } from '../data/addressHierarchy'
import api from '../services/api'

/**
 * Composable for cascading address dropdowns.
 * @param {Object} options
 * @param {boolean} options.withBarangay - Whether to fetch barangays (false for birthplace)
 */
export function useAddressDropdown({ withBarangay = true } = {}) {
  const selectedRegion = ref('')
  const selectedProvince = ref('')
  const selectedCity = ref('')
  const selectedBarangay = ref('')
  const autoDistrict = ref('')

  const barangayOptions = ref([])
  const barangayLoading = ref(false)

  // Region options (static)
  const regionOptions = addressData.regions.map((r) => r.name)

  // Province options based on selected region
  const provinceOptions = computed(() => {
    const region = addressData.regions.find((r) => r.name === selectedRegion.value)
    return region ? region.provinces.map((p) => p.name) : []
  })

  // City options based on selected province
  const cityOptions = computed(() => {
    const region = addressData.regions.find((r) => r.name === selectedRegion.value)
    if (!region) return []
    const province = region.provinces.find((p) => p.name === selectedProvince.value)
    return province ? province.cities.map((c) => c.name) : []
  })

  // Auto-populate district from city selection
  const cityData = computed(() => {
    const region = addressData.regions.find((r) => r.name === selectedRegion.value)
    if (!region) return null
    const province = region.provinces.find((p) => p.name === selectedProvince.value)
    if (!province) return null
    return province.cities.find((c) => c.name === selectedCity.value) || null
  })

  // Cascading resets
  watch(selectedRegion, () => {
    selectedProvince.value = ''
    selectedCity.value = ''
    selectedBarangay.value = ''
    autoDistrict.value = ''
    barangayOptions.value = []
  })

  watch(selectedProvince, () => {
    selectedCity.value = ''
    selectedBarangay.value = ''
    autoDistrict.value = ''
    barangayOptions.value = []
  })

  watch(selectedCity, async (newCity) => {
    selectedBarangay.value = ''
    autoDistrict.value = cityData.value?.district || ''

    if (newCity && withBarangay) {
      barangayLoading.value = true
      try {
        const response = await api.get('/address/barangays', { params: { city: newCity } })
        barangayOptions.value = Array.isArray(response.data) ? response.data : []
      } catch {
        barangayOptions.value = []
      } finally {
        barangayLoading.value = false
      }
    } else {
      barangayOptions.value = []
    }
  })

  return {
    selectedRegion,
    selectedProvince,
    selectedCity,
    selectedBarangay,
    autoDistrict,
    regionOptions,
    provinceOptions,
    cityOptions,
    barangayOptions,
    barangayLoading,
  }
}
