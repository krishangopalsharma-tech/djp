export const STATUS_ORDER = ['Active', 'In Progress', 'Resolved', 'On Hold'] as const
export type Status = typeof STATUS_ORDER[number]

export const STATUS_COLORS: Record<Status, string> = {
  Active: '#FC9796',
  'In Progress': '#EEEE96',
  Resolved: '#8FE0AD',
  'On Hold': '#FFC08C',
}

function hexToRgba(hex: string, alpha = 1): string {
  let h = hex.replace('#', '').trim()
  if (h.length === 3) h = h.split('').map(ch => ch + ch).join('')
  const r = parseInt(h.slice(0, 2), 16)
  const g = parseInt(h.slice(2, 4), 16)
  const b = parseInt(h.slice(4, 6), 16)
  const a = Math.max(0, Math.min(1, Number(alpha)))
  return `rgba(${r}, ${g}, ${b}, ${a})`
}

export function borderColor(status: Status): string {
  return STATUS_COLORS[status]
}

export function bgColor(status: Status, alpha = 0.2): string {
  return hexToRgba(STATUS_COLORS[status], alpha)
}

export function arrayForOrder(order: readonly Status[] = STATUS_ORDER): string[] {
  return Array.from(order, s => STATUS_COLORS[s])
}

export function colorForLabel(label: string): string | undefined {
  // exact match only to avoid false positives
  const s = STATUS_ORDER.find(s => s === label)
  return s ? STATUS_COLORS[s] : undefined
}
