// Centralized brand helper. Keeps <html data-brand="..."> in sync,
// persists to localStorage, and emits a 'brandchange' CustomEvent.

export const BRAND_KEY = 'ui.brand'

export function getBrand() {
  return document.documentElement.dataset.brand || localStorage.getItem(BRAND_KEY) || 'indigo'
}

export function applyBrand(brand) {
  const next = brand || 'indigo'
  const el = document.documentElement
  if (el.dataset.brand !== next) el.dataset.brand = next
  localStorage.setItem(BRAND_KEY, next)
  window.dispatchEvent(new CustomEvent('brandchange', { detail: { brand: next } }))
  return next
}

export function setBrand(brand) {
  return applyBrand(brand)
}

export function initBrand() {
  const stored = localStorage.getItem(BRAND_KEY) || 'indigo'
  return applyBrand(stored)
}
