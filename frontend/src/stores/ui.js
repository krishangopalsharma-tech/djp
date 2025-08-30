import { defineStore } from 'pinia'
import { getTheme, setTheme as setThemeHelper, toggleTheme as toggleThemeHelper } from '@/lib/theme'
import { getBrand, setBrand as setBrandHelper } from '@/lib/brand'

export const useUIStore = defineStore('ui', {
  state: () => ({
    theme: 'light',
    brand: 'indigo',
  }),
  actions: {
    // theme
    loadTheme() {
      this.theme = getTheme()
    },
    setTheme(next) {
      this.theme = setThemeHelper(next)
    },
    toggleTheme() {
      this.theme = toggleThemeHelper()
    },

    // brand
    loadBrand() {
      this.brand = getBrand()
    },
    setBrand(next) {
      this.brand = setBrandHelper(next)
    },
  },
})
