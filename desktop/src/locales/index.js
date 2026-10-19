import { createI18n } from 'vue-i18n'
import zhCN from './lang/zh-CN'
import enUS from './lang/en-US'

const messages = {
  'zh-CN': zhCN,
  'en-US': enUS
}

const savedLocale = localStorage.getItem('locale') || 'zh-CN'

const i18n = createI18n({
  legacy: false,
  locale: savedLocale,
  fallbackLocale: 'zh-CN',
  messages
})

export default i18n

export function setLocale(locale) {
  i18n.global.locale.value = locale
  localStorage.setItem('locale', locale)
  document.querySelector('html').setAttribute('lang', locale)
  // 强制触发更新
  window.dispatchEvent(new Event('locale-changed'))
}

export function getLocale() {
  return i18n.global.locale.value
}