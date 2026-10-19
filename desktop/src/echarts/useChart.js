import * as echarts from 'echarts'
import { useAppStore } from '@/store/modules/app'
import { watch, onBeforeUnmount, nextTick } from 'vue'

const chartInstances = new Map()

export function useChart(chartRef, options = {}) {
  let chartInstance = null
  let resizeObserver = null
  const appStore = useAppStore()

  function initChart() {
    if (!chartRef.value) return null
    chartInstance = echarts.init(chartRef.value, appStore.isDark ? 'dark' : 'light')
    chartInstances.set(chartRef.value, chartInstance)
    return chartInstance
  }

  function setOption(option, notMerge = false, lazyUpdate = false) {
    if (!chartInstance) {
      initChart()
    }
    if (chartInstance) {
      chartInstance.setOption(option, notMerge, lazyUpdate)
    }
  }

  function resize() {
    chartInstance && chartInstance.resize()
  }

  function handleResize() {
    resize()
  }

  function setupResizeObserver() {
    if (chartRef.value && window.ResizeObserver) {
      resizeObserver = new ResizeObserver(handleResize)
      resizeObserver.observe(chartRef.value)
    }
  }

  function destroyChart() {
    if (chartInstance) {
      chartInstance.dispose()
      chartInstances.delete(chartRef.value)
      chartInstance = null
    }
    if (resizeObserver) {
      resizeObserver.disconnect()
      resizeObserver = null
    }
  }

  const stopWatchTheme = watch(
    () => appStore.isDark,
    () => {
      if (chartInstance && chartRef.value) {
        const option = chartInstance.getOption()
        chartInstance.dispose()
        chartInstance = echarts.init(chartRef.value, appStore.isDark ? 'dark' : 'light')
        chartInstance.setOption(option)
      }
    }
  )

  onBeforeUnmount(() => {
    destroyChart()
    stopWatchTheme()
  })

  nextTick(() => {
    initChart()
    setupResizeObserver()
    if (options.onReady) {
      options.onReady(chartInstance)
    }
  })

  return {
    chartInstance,
    setOption,
    resize,
    destroyChart
  }
}

export function getChartInstance(el) {
  return chartInstances.get(el)
}

export default echarts
