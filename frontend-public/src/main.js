import { createApp } from 'vue'
import VueGtag from 'vue-gtag-next'
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(router)

const gaMeasurementId = import.meta.env.VITE_GA_MEASUREMENT_ID
if (gaMeasurementId) {
  app.use(VueGtag, {
    property: { id: gaMeasurementId },
  }, router)
}

app.mount('#app')
