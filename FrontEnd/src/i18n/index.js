import {createI18n}  from 'vue-i18n'
import enLocale from './locales/en.json'
import frLocale from './locales/fr.json'
import deLocale from './locales/de.json'

const i18n = createI18n({
  legacy: false,
  locale: 'en',
  fallbackLocale: 'en',
  messages: {
    en: enLocale,
    fr: frLocale,
    de: deLocale
  }
})

export default i18n