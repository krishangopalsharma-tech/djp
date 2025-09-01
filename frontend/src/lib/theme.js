// frontend/src/lib/theme.js
/** Read a CSS variable (hex or rgb[a]) from the app root or document.
 * @param {string} name CSS var name like '--text'
 * @param {string} [fallback] fallback color
 * @returns {string}
 */
export function getCssVar(name, fallback = '') {
  const el = document.getElementById('app') || document.body || document.documentElement
  const val = getComputedStyle(el).getPropertyValue(name)?.trim()
  return val || fallback || '#000'
}

/** Convert a color to rgba string with given alpha.
 * Accepts hex (#rgb/#rrggbb) or rgb/rgba strings.
 * @param {string} color
 * @param {number} alpha 0..1
 */
export function withAlpha(color, alpha) {
  if (!color) return `rgba(0,0,0,${alpha})`
  if (color.startsWith('rgba(')) return color.replace(/rgba\(([^)]+)\)/, (_m, inner) => {
    const parts = inner.split(',').map(s => s.trim())
    return `rgba(${parts[0]}, ${parts[1]}, ${parts[2]}, ${alpha})`
  })
  if (color.startsWith('rgb(')) return color.replace(/rgb\(([^)]+)\)/, (_m, inner) => `rgba(${inner}, ${alpha})`)
  if (color.startsWith('#')) {
    const hex = color.slice(1)
    const to255 = h => parseInt(h, 16)
    let r, g, b
    if (hex.length === 3) {
      r = to255(hex[0] + hex[0]); g = to255(hex[1] + hex[1]); b = to255(hex[2] + hex[2])
    } else if (hex.length >= 6) {
      r = to255(hex.slice(0,2)); g = to255(hex.slice(2,4)); b = to255(hex.slice(4,6))
    } else {
      r = g = b = 0
    }
    return `rgba(${r}, ${g}, ${b}, ${alpha})`
  }
  // Fallback
  return color
}

export function currentThemeColors() {
  return {
    text: getCssVar('--text', '#0f172a'),
    muted: getCssVar('--muted', '#64748b'),
    border: getCssVar('--border', '#e5e7eb'),
    card: getCssVar('--card', '#ffffff'),
    primary: getCssVar('--primary', '#2563eb'),
    primary600: getCssVar('--primary-600', '#1d4ed8'),
  }
}

