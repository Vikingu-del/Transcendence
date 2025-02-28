import {createI18n}  from 'vue-i18n'
import enLocale from './locales/en.json'
import frLocale from './locales/fr.json'
import deLocale from './locales/de.json'


export default createI18n({
  legacy: false,
  globalInjection: true, // Makes translation functions available globally
  locale: 'en',
  fallbackLocale: 'en',
  messages: {
    en: enLocale,
    fr: frLocale,
    de: deLocale
  }
})
