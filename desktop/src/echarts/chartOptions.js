export function getLineChartOption(data = {}) {
  const { xData = [], series = [], title = '', legend = [], yAxisName = '' } = data
  return {
    title: title
      ? {
          text: title,
          left: 'center',
          textStyle: { fontSize: 16, fontWeight: 500 }
        }
      : undefined,
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    legend: legend.length
      ? {
          data: legend,
          bottom: 0
        }
      : undefined,
    grid: {
      left: '3%',
      right: '4%',
      bottom: legend.length ? '10%' : '3%',
      top: title ? '15%' : '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: xData,
      boundaryGap: false,
      axisLine: { lineStyle: { type: 'dashed' } }
    },
    yAxis: {
      type: 'value',
      name: yAxisName,
      axisLine: { show: false },
      splitLine: { lineStyle: { type: 'dashed' } }
    },
    series: series.map(item => ({
      name: item.name,
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      data: item.data,
      areaStyle: item.area ? { opacity: 0.1 } : undefined,
      itemStyle: item.color ? { color: item.color } : undefined,
      lineStyle: item.color ? { color: item.color } : undefined
    }))
  }
}

export function getBarChartOption(data = {}) {
  const { xData = [], series = [], title = '', legend = [], yAxisName = '', horizontal = false } = data
  return {
    title: title
      ? {
          text: title,
          left: 'center',
          textStyle: { fontSize: 16, fontWeight: 500 }
        }
      : undefined,
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    legend: legend.length
      ? {
          data: legend,
          bottom: 0
        }
      : undefined,
    grid: {
      left: '3%',
      right: '4%',
      bottom: legend.length ? '10%' : '3%',
      top: title ? '15%' : '3%',
      containLabel: true
    },
    xAxis: horizontal
      ? {
          type: 'value',
          axisLine: { show: false },
          splitLine: { lineStyle: { type: 'dashed' } }
        }
      : {
          type: 'category',
          data: xData,
          axisLine: { lineStyle: { type: 'dashed' } }
        },
    yAxis: horizontal
      ? {
          type: 'category',
          data: xData,
          axisLine: { lineStyle: { type: 'dashed' } }
        }
      : {
          type: 'value',
          name: yAxisName,
          axisLine: { show: false },
          splitLine: { lineStyle: { type: 'dashed' } }
        },
    series: series.map(item => ({
      name: item.name,
      type: 'bar',
      data: item.data,
      barWidth: '40%',
      itemStyle: {
        color: item.color,
        borderRadius: [4, 4, 0, 0]
      }
    }))
  }
}

export function getPieChartOption(data = {}) {
  const { data: pieData = [], title = '', legend = true, radius = ['40%', '70%'], center = ['50%', '50%'] } = data
  return {
    title: title
      ? {
          text: title,
          left: 'center',
          top: 'center',
          textStyle: { fontSize: 18, fontWeight: 600 },
          subtext: pieData.reduce((sum, item) => sum + (item.value || 0), 0),
          subtextStyle: { fontSize: 14 }
        }
      : undefined,
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: legend
      ? {
          orient: 'vertical',
          left: 'left',
          top: 'center'
        }
      : undefined,
    series: [
      {
        type: 'pie',
        radius,
        center,
        avoidLabelOverlap: true,
        itemStyle: {
          borderRadius: 6,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: pieData
      }
    ]
  }
}

export function getGaugeChartOption(data = {}) {
  const { value = 0, max = 100, title = '', unit = '%', color = '#409eff' } = data
  return {
    series: [
      {
        type: 'gauge',
        startAngle: 180,
        endAngle: 0,
        min: 0,
        max,
        splitNumber: 10,
        radius: '100%',
        center: ['50%', '70%'],
        axisLine: {
          lineStyle: {
            width: 12,
            color: [[value / max, color], [1, '#eee']]
          }
        },
        pointer: {
          icon: 'path://M12.8,0.7l12,40.1H0.7L12.8,0.7z',
          length: '60%',
          width: 8,
          offsetCenter: [0, '-10%'],
          itemStyle: { color: color }
        },
        axisTick: {
          length: 4,
          lineStyle: { color: '#999', width: 1 }
        },
        splitLine: {
          length: 8,
          lineStyle: { color: '#666', width: 2 }
        },
        axisLabel: {
          color: '#999',
          fontSize: 10,
          distance: -20
        },
        title: {
          show: true,
          offsetCenter: [0, '10%'],
          fontSize: 14,
          color: '#666'
        },
        detail: {
          valueAnimation: true,
          fontSize: 24,
          offsetCenter: [0, '35%'],
          formatter: `{value}${unit}`,
          color: color
        },
        data: [{ value, name: title }]
      }
    ]
  }
}

export default {
  getLineChartOption,
  getBarChartOption,
  getPieChartOption,
  getGaugeChartOption
}
