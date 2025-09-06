export const STATUS_ORDER = ['Resolved', 'Active', 'In Progress', 'On Hold']

export const STATUS_COLORS = {
  Resolved: '#8FE0AD',
  Active: '#FC9796',
  'In Progress': '#EEEE96',
  'On Hold': '#FFC08C',
}

export function hexToRgba(hex, alpha = 1) {
  let h = hex.replace('#', '').trim()
  if (h.length === 3) h = h.split('').map(ch => ch + ch).join('')
  const r = parseInt(h.slice(0, 2), 16)
  const g = parseInt(h.slice(2, 4), 16)
  const b = parseInt(h.slice(4, 6), 16)
  const a = Math.max(0, Math.min(1, Number(alpha)))
  return `rgba(${r}, ${g}, ${b}, ${a})`
}

export function borderColor(status) {
  return STATUS_COLORS[status]
}

export function bgColor(status, alpha = 0.2) {
  return hexToRgba(STATUS_COLORS[status], alpha)
}

export function arrayForOrder(order = STATUS_ORDER) {
  return Array.from(order, s => STATUS_COLORS[s])
}

export function colorForLabel(label) {
  // case-insensitive exact match against known statuses
  const s = STATUS_ORDER.find(s => s.toLowerCase() === String(label).toLowerCase())
  return s ? STATUS_COLORS[s] : undefined
}

// Convenience: map any dataset label to strict status colors
export function colorsForDatasetLabel(label, bgAlpha = 0.85) {
  const hex = colorForLabel(label)
  if (!hex) return undefined
  return { border: hex, bg: hexToRgba(hex, bgAlpha) }
}
