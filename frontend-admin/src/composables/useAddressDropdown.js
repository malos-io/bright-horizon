import { ref, watch } from 'vue'
import api from '../services/api'

/**
 * Composable for cascading address dropdowns — fully API-driven.
 * @param {Object} options
 * @param {boolean} options.withBarangay - Whether to fetch barangays (false for birthplace)
 * @param {boolean} options.allRegions  - Show all 17 PH regions (true for birthplace, false for mailing)
 */
export function useAddressDropdown({ withBarangay = true, allRegions = false } = {}) {
  const selectedRegion = ref('')
  const selectedProvince = ref('')
  const selectedCity = ref('')
  const selectedBarangay = ref('')
  const autoDistrict = ref('')

  const regionOptions = ref([])
  const provinceOptions = ref([])
  const cityOptions = ref([])
  const barangayOptions = ref([])

  const regionLoading = ref(false)
  const provinceLoading = ref(false)
  const cityLoading = ref(false)
  const barangayLoading = ref(false)

  // Internal city data (with district info)
  let _cityData = []

  // Fetch regions on init
  regionLoading.value = true
  api.get('/address/regions', { params: { all: allRegions } })
    .then((res) => { regionOptions.value = res.data })
    .catch(() => { regionOptions.value = [] })
    .finally(() => { regionLoading.value = false })

  // Region changed → fetch provinces
  watch(selectedRegion, async (newRegion) => {
    selectedProvince.value = ''
    selectedCity.value = ''
    selectedBarangay.value = ''
    autoDistrict.value = ''
    provinceOptions.value = []
    cityOptions.value = []
    barangayOptions.value = []
    _cityData = []

    if (!newRegion) return
    provinceLoading.value = true
    try {
      const res = await api.get('/address/provinces', { params: { region: newRegion } })
      provinceOptions.value = res.data
    } catch {
      provinceOptions.value = []
    } finally {
      provinceLoading.value = false
    }
  })

  // Province changed → fetch cities
  watch(selectedProvince, async (newProvince) => {
    selectedCity.value = ''
    selectedBarangay.value = ''
    autoDistrict.value = ''
    cityOptions.value = []
    barangayOptions.value = []
    _cityData = []

    if (!newProvince) return
    cityLoading.value = true
    try {
      const res = await api.get('/address/cities', {
        params: { region: selectedRegion.value, province: newProvince },
      })
      _cityData = res.data
      cityOptions.value = res.data.map((c) => c.name)
    } catch {
      cityOptions.value = []
      _cityData = []
    } finally {
      cityLoading.value = false
    }
  })

  // City changed → auto-district + fetch barangays
  watch(selectedCity, async (newCity) => {
    selectedBarangay.value = ''
    barangayOptions.value = []

    // Auto-populate district from city data
    const city = _cityData.find((c) => c.name === newCity)
    autoDistrict.value = city?.district || ''

    if (newCity && withBarangay) {
      barangayLoading.value = true
      try {
        const res = await api.get('/address/barangays', {
          params: {
            city: newCity,
            region: selectedRegion.value,
            province: selectedProvince.value,
          },
        })
        barangayOptions.value = Array.isArray(res.data) ? res.data : []
      } catch {
        barangayOptions.value = []
      } finally {
        barangayLoading.value = false
      }
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
