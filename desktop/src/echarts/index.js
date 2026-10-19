import BaseChart from './BaseChart.vue'
import { useChart } from './useChart'
import chartOptions from './chartOptions'
import * as echarts from 'echarts'

export { BaseChart, useChart, chartOptions, echarts }

export default {
  install(app) {
    app.component('BaseChart', BaseChart)
    app.config.globalProperties.$echarts = echarts
  }
}
