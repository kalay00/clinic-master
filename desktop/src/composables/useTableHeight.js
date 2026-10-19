import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { calculateTableHeight, getTableHeightByContainer } from '@/utils/tableHeight'

export function useTableHeight(options = {}) {
  const tableHeight = ref(400)
  let resizeObserver = null
  let containerElement = null

  const {
    extraOffset = 0,
    excludeSelectors = [],
    containerSelector = ''
  } = options

  const route = useRoute()

  const updateHeight = () => {
    if (containerSelector && containerElement) {
      tableHeight.value = getTableHeightByContainer(containerSelector, {
        extraOffset,
        excludeSelectors
      })
    } else {
      tableHeight.value = calculateTableHeight({
        extraOffset,
        excludeSelectors
      })
    }
  }

  const setContainer = (el) => {
    if (el) {
      containerElement = el
      if (resizeObserver) {
        resizeObserver.observe(el)
      }
      updateHeight()
    }
  }

  const delayedUpdate = () => {
    nextTick(() => {
      setTimeout(updateHeight, 50)
    })
  }

  onMounted(() => {
    if (containerSelector) {
      containerElement = document.querySelector(containerSelector)
      if (containerElement) {
        resizeObserver = new ResizeObserver(() => {
          updateHeight()
        })
        resizeObserver.observe(containerElement)
      }
    }

    window.addEventListener('resize', updateHeight)
    delayedUpdate()
  })

  watch(() => route.fullPath, () => {
    delayedUpdate()
  })

  onUnmounted(() => {
    if (resizeObserver) {
      resizeObserver.disconnect()
      resizeObserver = null
    }
    window.removeEventListener('resize', updateHeight)
  })

  return {
    tableHeight,
    updateHeight,
    setContainer
  }
}