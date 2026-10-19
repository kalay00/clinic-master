import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import piniaPersist from 'pinia-plugin-persistedstate'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import './assets/scss/index.scss'
import './assets/scss/element-plus.scss'
import { setupErrorHandler } from './utils/errorHandler'
import { setupGlobalProperties } from './utils/globalProperties'
import i18n from './locales'
import permissionDirective from './directives/permission'

const app = createApp(App)
const pinia = createPinia()
pinia.use(piniaPersist)

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(pinia)
app.use(router)
app.use(ElementPlus)
app.use(i18n)

setupGlobalProperties(app)
setupErrorHandler(app)
app.directive('permission', permissionDirective)

app.mount('#app')
