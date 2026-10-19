<template>
  <div ref="chartRef" :style="{ width, height }" class="base-chart"></div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import { useAppStore } from '@/store/modules/app'

const props = defineProps({
  option: {
    type: Object,
    default: () => ({})
  },
  width: {
    type: String,
    default: '100%'
  },
  height: {
    type: String,
    default: '300px'
  },
  loading: {
    type: Boolean,
    default: false
  },
  emptyData: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['chartReady', 'click'])

const chartRef = ref(null)
let chartInstance = null
const appStore = useAppStore()

function initChart() {
  if (!chartRef.value) return
  chartInstance = echarts.init(chartRef.value, appStore.isDark ? 'dark' : 'light')
  updateChart()
  chartInstance.on('click', params => {
    emit('click', params)
  })
  emit('chartReady', chartInstance)
}

function updateChart() {
  if (!chartInstance) return
  if (props.emptyData) {
    chartInstance.clear()
    chartInstance.setOption({
      title: {
        text: '暂无数据',
        left: 'center',
        top: 'center',
        textStyle: {
          color: '#999',
          fontSize: 14
        }
      }
    })
  } else {
    chartInstance.setOption(props.option, true)
  }
}

function resize() {
  chartInstance && chartInstance.resize()
}

watch(
  () => props.option,
  () => {
    updateChart()
  },
  { deep: true }
)

watch(
  () => props.loading,
  val => {
    if (chartInstance) {
      if (val) {
        chartInstance.showLoading()
      } else {
        chartInstance.hideLoading()
      }
    }
  }
)

watch(
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

onMounted(() => {
  initChart()
  window.addEventListener('resize', resize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resize)
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})

defineExpose({
  resize,
  getInstance: () => chartInstance
})
</script>

<style lang="scss" scoped>
.base-chart {
  width: 100%;
  height: 100%;
}
</style>
