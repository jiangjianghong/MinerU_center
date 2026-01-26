import { ref, computed } from 'vue'
import zh from './zh'
import en from './en'

const messages = { zh, en }
const currentLocale = ref(localStorage.getItem('locale') || 'zh')

export function useI18n() {
  const locale = computed({
    get: () => currentLocale.value,
    set: (val) => {
      currentLocale.value = val
      localStorage.setItem('locale', val)
    }
  })

  const t = (key, params = {}) => {
    const keys = key.split('.')
    let value = messages[currentLocale.value]

    for (const k of keys) {
      if (value && typeof value === 'object') {
        value = value[k]
      } else {
        return key
      }
    }

    if (typeof value === 'string') {
      return value.replace(/\{(\w+)\}/g, (_, name) => params[name] ?? '')
    }

    return key
  }

  const toggleLocale = () => {
    locale.value = locale.value === 'zh' ? 'en' : 'zh'
  }

  return {
    locale,
    t,
    toggleLocale
  }
}
