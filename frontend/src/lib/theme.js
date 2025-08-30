// Centralized theme helper (light|dark). Keeps <html data-theme="..."> in sync,
// persists to localStorage, and emits a 'themechange' CustomEvent.
//
// Usage:
//   import { initTheme, setTheme, toggleTheme, getTheme } from '@/lib/theme'
//
//   initTheme();               // once, on app boot
//   setTheme('dark');          // explicit
//   toggleTheme();             // flip light<->dark
//   window.addEventListener('themechange', (e) => console.log(e.detail.theme))

export const THEME_KEY = 'ui.theme'

export function getTheme() {
  // Prefer the attribute (truth of the DOM), then storage, else 'light'
  return document.documentElement.dataset.theme || localStorage.getItem(THEME_KEY) || 'light'
}

export function applyTheme(theme) {
  const next = theme === 'dark' ? 'dark' : 'light'
  const el = document.documentElement
  if (el.dataset.theme !== next) {
    el.dataset.theme = next
  }
  localStorage.setItem(THEME_KEY, next)
  // Broadcast so listeners (charts, etc.) can react
  window.dispatchEvent(new CustomEvent('themechange', { detail: { theme: next } }))
  return next
}

export function setTheme(theme) {
  return applyTheme(theme)
}

export function toggleTheme() {
  const current = getTheme()
  return applyTheme(current === 'light' ? 'dark' : 'light')
}

export function initTheme() {
  // Initialize from storage (or default light)
  const stored = localStorage.getItem(THEME_KEY) || 'light'
  return applyTheme(stored)
}
