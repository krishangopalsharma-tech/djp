// frontend/src/lib/chartTheme.js
import { Chart, Filler } from 'chart.js'
import { currentThemeColors, withAlpha } from './theme'

export function applyChartTheme() {
  // Register missing plugins
  Chart.register(Filler)

  const c = currentThemeColors()

  // Base text color for labels/ticks
  Chart.defaults.color = c.text

  // Grid + ticks defaults
  const gridColor = withAlpha(c.border, 0.6)
  const tickColor = c.muted
  const borderColor = withAlpha(c.border, 0.8)

  // Apply to common scales
  ;['category','linear','logarithmic','time'].forEach(scale => {
    if (!Chart.defaults.scales[scale]) Chart.defaults.scales[scale] = {}
    Chart.defaults.scales[scale].grid = { color: gridColor }
    Chart.defaults.scales[scale].ticks = { color: tickColor }
    Chart.defaults.scales[scale].border = { color: borderColor }
  })

  // Legends and title
  Chart.defaults.plugins.legend = Chart.defaults.plugins.legend || {}
  Chart.defaults.plugins.legend.labels = { color: c.text }
  Chart.defaults.plugins.title = Chart.defaults.plugins.title || {}
  Chart.defaults.plugins.title.color = c.text

  // Tooltip to match card colors
  Chart.defaults.plugins.tooltip = {
    backgroundColor: withAlpha(c.card, 0.98),
    titleColor: c.text,
    bodyColor: c.text,
    borderColor: c.border,
    borderWidth: 1,
  }

  // Lines default to theme primary
  Chart.defaults.elements = Chart.defaults.elements || {}
  Chart.defaults.elements.line = {
    borderColor: c.primary,
    backgroundColor: withAlpha(c.primary, 0.2),
  }
  Chart.defaults.elements.bar = {
    borderColor: c.primary,
    backgroundColor: withAlpha(c.primary, 0.35),
  }
}

// Optional: re-apply on theme changes by observing the app container className
export function activateChartThemeAutoUpdate() {
  const app = document.getElementById('app')
  if (!app || typeof MutationObserver === 'undefined') return
  const obs = new MutationObserver(() => applyChartTheme())
  obs.observe(app, { attributes: true, attributeFilter: ['class'] })
}

