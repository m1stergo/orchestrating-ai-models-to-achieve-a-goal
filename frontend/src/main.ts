import './app/assets/main.css'
import PrimeVue from 'primevue/config'
import ConfirmationService from 'primevue/confirmationservice';
import ToastService from 'primevue/toastservice';
import Aura from '@primeuix/themes/aura'
import 'primeicons/primeicons.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './app/router'
import { createPinia } from 'pinia'
import { PiniaColada } from '@pinia/colada'
const app = createApp(App)

const pinia = createPinia()
app.use(pinia)
app.use(PiniaColada)
app.use(ConfirmationService)
app.use(ToastService)
app.use(PrimeVue, {
  theme: {
    preset: Aura,
    options: {
      cssLayer: {
        name: 'primevue',
        order: 'theme, base, primevue',
      },
      darkModeSelector: '.dark',
    },
  },
})
app.use(router)

app.mount('#app')
