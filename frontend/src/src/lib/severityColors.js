// Severity color helpers
export const SEVERITY_ORDER = ['Minor', 'Major', 'Critical']

export const SEVERITY_HEX = {
  Critical: '#FC9796',
  Major:    '#FFC08C',
  Minor:    '#8FE0AD',
}

export function hexToRgba(hex, alpha = 1) {
  let h = hex.replace('#', '').trim()
  if (h.length === 3) h = h.split('').map(c => c + c).join('')
  const r = parseInt(h.slice(0, 2), 16)
  const g = parseInt(h.slice(2, 4), 16)
  const b = parseInt(h.slice(4, 6), 16)
  const a = Math.max(0, Math.min(1, Number(alpha)))
  return `rgba(${r}, ${g}, ${b}, ${a})`
}

export function severityHex(label) {
  if (!label) return undefined
  const key = SEVERITY_ORDER.find(s => s.toLowerCase() === String(label).toLowerCase())
  return key ? SEVERITY_HEX[key] : undefined
}

export function severityBg(label, alpha = 0.85) {
  const hex = severityHex(label)
  return hex ? hexToRgba(hex, alpha) : undefined
}

export function paletteFor(labels = []) {
  return labels.map(l => severityHex(l) ?? '#9aa1a6')
}
