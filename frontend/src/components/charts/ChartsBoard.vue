<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import 'echarts-wordcloud'

const containerRef = ref(null)
const pieChartRef = ref(null)
const wordCloudRef = ref(null)
let pieChartInstance = null
let wordCloudInstance = null
let ro = null

function initCharts() {
  if (pieChartRef.value && !pieChartInstance) {
    pieChartInstance = echarts.init(pieChartRef.value)
    pieChartInstance.setOption({
      title: { text: '心愿类别分布', left: 'center', top: '6%', textStyle: { fontSize: 26, fontFamily: 'serif' } },
      tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
      legend: { bottom: '0%', left: 'center', icon: 'circle', itemGap: 10, textStyle: { fontSize: 10 } },
      series: [{
        name: '类别', type: 'pie', radius: ['30%', '55%'], center: ['50%', '56%'], avoidLabelOverlap: true,
        itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
        label: { show: false },
        emphasis: { label: { show: false } },
        labelLine: { show: false },
        data: [
          { value: 1048, name: '红色传承', itemStyle: { color: '#ef4444' } },
          { value: 735, name: '乡村建设', itemStyle: { color: '#f59e0b' } },
          { value: 580, name: '产业发展', itemStyle: { color: '#3b82f6' } },
          { value: 484, name: '生态环保', itemStyle: { color: '#10b981' } }
        ]
      }]
    })
  }

  if (wordCloudRef.value && !wordCloudInstance) {
    wordCloudInstance = echarts.init(wordCloudRef.value)
    wordCloudInstance.setOption({
      title: { text: '热门心愿词云', left: 'center', top: '6%', textStyle: { fontSize: 26, fontFamily: 'serif' } },
      series: [{
        type: 'wordCloud', shape: 'circle', left: 'center', top: '10%', width: '95%', height: '95%',
        sizeRange: [10, 22], rotationRange: [0, 0], rotationStep: 0, gridSize: 10, drawOutOfBound: false,
        layoutAnimation: true,
        textStyle: {
          fontFamily: 'sans-serif', fontWeight: 'bold', color: () => 'rgb(' + [
            Math.round(Math.random() * 160), Math.round(Math.random() * 160), Math.round(Math.random() * 160)
          ].join(',') + ')'
        },
        emphasis: { focus: 'self', textStyle: { shadowBlur: 10, shadowColor: '#333' } },
        data: [
          { name: '红色基因', value: 100 }, { name: '乡村振兴', value: 92 }, { name: '德兴', value: 80 },
          { name: '科技赋能', value: 73 }, { name: '旅游', value: 65 }, { name: '传承', value: 60 },
          { name: '创新', value: 55 }, { name: '富裕', value: 48 }, { name: '美好生活', value: 42 }, { name: '生态', value: 39 }
        ]
      }]
    })
  }
}

function resizeCharts() {
  try {
    pieChartInstance?.resize()
    wordCloudInstance?.resize()
  } catch (e) {
    // ignore
  }
}

onMounted(async () => {
  await nextTick()
  initCharts()
  setTimeout(resizeCharts, 80)

  if (containerRef.value && 'ResizeObserver' in window) {
    ro = new ResizeObserver(() => resizeCharts())
    ro.observe(containerRef.value)
  }
  window.addEventListener('orientationchange', resizeCharts)
})

onUnmounted(() => {
  pieChartInstance?.dispose()
  wordCloudInstance?.dispose()
  if (ro && containerRef.value) ro.unobserve(containerRef.value)
  window.removeEventListener('orientationchange', resizeCharts)
})
</script>

<template>
  <div ref="containerRef" class="w-full max-w-5xl mx-auto px-4 mb-8">
    <div class="flex flex-col md:flex-row gap-4">
      <div class="flex-1 bg-white p-4 rounded-xl shadow-sm border border-gray-100">
        <div ref="pieChartRef" class="w-full" style="height:220px; min-height:180px;"></div>
      </div>
      <div class="flex-1 bg-white p-4 rounded-xl shadow-sm border border-gray-100">
        <div ref="wordCloudRef" class="w-full" style="height:220px; min-height:180px;"></div>
      </div>
    </div>
  </div>
</template>
