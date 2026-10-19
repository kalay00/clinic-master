export function calculateTableHeight(options = {}) {
  const {
    extraOffset = 0,
    excludeSelectors = []
  } = options

  const appMain = document.querySelector('.app-main')
  if (!appMain) {
    return Math.max(window.innerHeight - 300, 200)
  }

  const appMainRect = appMain.getBoundingClientRect()
  const style = window.getComputedStyle(appMain)
  const paddingTop = parseFloat(style.paddingTop) || 0
  const paddingBottom = parseFloat(style.paddingBottom) || 0
  let availableHeight = appMainRect.height - paddingTop - paddingBottom

  if (excludeSelectors.length > 0) {
    excludeSelectors.forEach(selector => {
      const elements = document.querySelectorAll(selector)
      elements.forEach(el => {
        const rect = el.getBoundingClientRect()
        const elStyle = window.getComputedStyle(el)
        const marginBottom = parseFloat(elStyle.marginBottom) || 0
        const marginTop = parseFloat(elStyle.marginTop) || 0
        availableHeight -= rect.height + marginBottom + marginTop
      })
    })
  }

  return Math.max(availableHeight - extraOffset, 200)
}

export function getTableHeightByContainer(containerSelector, options = {}) {
  const container = document.querySelector(containerSelector)
  if (!container) {
    return calculateTableHeight(options)
  }

  const {
    extraOffset = 0,
    excludeSelectors = []
  } = options

  const containerRect = container.getBoundingClientRect()
  const style = window.getComputedStyle(container)
  const paddingTop = parseFloat(style.paddingTop) || 0
  const paddingBottom = parseFloat(style.paddingBottom) || 0
  let availableHeight = containerRect.height - paddingTop - paddingBottom

  if (excludeSelectors.length > 0) {
    excludeSelectors.forEach(selector => {
      const elements = container.querySelectorAll(selector)
      elements.forEach(el => {
        const rect = el.getBoundingClientRect()
        const elStyle = window.getComputedStyle(el)
        const marginBottom = parseFloat(elStyle.marginBottom) || 0
        const marginTop = parseFloat(elStyle.marginTop) || 0
        availableHeight -= rect.height + marginBottom + marginTop
      })
    })
  }

  return Math.max(availableHeight - extraOffset, 200)
}