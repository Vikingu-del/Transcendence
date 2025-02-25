import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import TheWelcome from '../TheWelcome.vue'

describe('TheWelcome', () => {
  const i18n = createI18n({
    legacy: false,
    locale: 'en',
    messages: {
      en: {
        welcome: {
          subject: {
            heading: 'Subject'
          }
        }
      }
    }
  })

  it('renders properly and switches languages', async () => {
    const wrapper = mount(TheWelcome, {
      global: {
        plugins: [i18n]
      }
    })

    expect(wrapper.find('select').exists()).toBe(true)
    expect(wrapper.find('select').element.value).toBe('en')
  })
})