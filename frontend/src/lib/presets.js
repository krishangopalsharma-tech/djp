// Preset exporter/importer for theme + brand + a few tokens.
// Stores in localStorage and can auto-apply on startup.

import { getTheme, setTheme } from '@/lib/theme'
import { getBrand, setBrand } from '@/lib/brand'

export const PRESET_KEY = 'ui.preset'

function readVar(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim()
}
function writeVar(name, value) {
  if (value == null || value === '') {
    document.documentElement.style.removeProperty(name) // fallback to CSS defaults
  } else {
    document.documentElement.style.setProperty(name, String(value))
  }
}

export function getCurrentPreset() {
  return {
    theme: getTheme(),         // 'light' | 'dark'
    brand: getBrand(),         // 'indigo' | 'rail' | 'emerald' | ...
    vars: {
      scaleText: readVar('--scale-text') || '1',
      scaleControl: readVar('--scale-control') || '1',
      fontSans: readVar('--font-sans') || '',
      fontMono: readVar('--font-mono') || '',
    }
  }
}

export function applyPreset(preset) {
  if (!preset || typeof preset !== 'object') return
  const { theme, brand, vars } = preset

  if (brand) setBrand(brand)
  if (theme) setTheme(theme)

  if (vars && typeof vars === 'object') {
    if (vars.scaleText)   writeVar('--scale-text', vars.scaleText)
    if (vars.scaleControl)writeVar('--scale-control', vars.scaleControl)
    if (vars.fontSans)    writeVar('--font-sans', vars.fontSans)
    if (vars.fontMono)    writeVar('--font-mono', vars.fontMono)
  }

  // persist
  try { localStorage.setItem(PRESET_KEY, JSON.stringify(preset)) } catch {}
}

export function clearPreset() {
  localStorage.removeItem(PRESET_KEY)
  // Remove any inline overrides so CSS defaults take over
  ['--scale-text','--scale-control','--font-sans','--font-mono'].forEach(v => document.documentElement.style.removeProperty(v))
}

export function initPresetIfAny() {
  try {
    const raw = localStorage.getItem(PRESET_KEY)
    if (!raw) return
    const preset = JSON.parse(raw)
    applyPreset(preset)
  } catch {
    // ignore malformed
  }
}
