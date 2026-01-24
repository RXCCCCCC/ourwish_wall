<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import 'echarts-wordcloud'
import { wishAPI } from '@/api'
import { CATEGORY_COLORS, CATEGORY_DEFAULT_COLOR } from '@/constants'

const containerRef = ref(null)
const pieChartRef = ref(null)
const wordCloudRef = ref(null)
let pieChartInstance = null
let wordCloudInstance = null
let ro = null

const statsData = ref(null)

async function loadStats() {
  try {
    const data = await wishAPI.getStats()
    statsData.value = data
  } catch (error) {
    console.error('Failed to load stats:', error)
    statsData.value = { category_stats: [], word_cloud: [] }
  }
}

async function refreshCharts() {
  await loadStats()
  updateCharts()
}

function updateCharts() {
  const categoryStats = statsData.value?.category_stats || []
  const wordCloudData = statsData.value?.word_cloud || []
  const isMobile = window.innerWidth < 768

  if (pieChartInstance) {
    const pieData = categoryStats.map(item => ({
      value: item.count,
      name: item.category,
      itemStyle: { color: CATEGORY_COLORS[item.category] || CATEGORY_DEFAULT_COLOR }
    }))

    pieChartInstance.setOption({
      title: { 
        text: pieData.length > 0 ? '心愿类别分布' : '暂无数据', 
        left: 'center', 
        top: '6%', 
        textStyle: { fontSize: isMobile ? 20 : 24, fontFamily: 'serif' } 
      },
      tooltip: pieData.length > 0 ? { trigger: 'item', formatter: '{b}: {c} ({d}%)' } : { show: false },
      legend: pieData.length > 0 ? { 
        bottom: '0%', 
        left: 'center', 
        icon: 'circle', 
        itemGap: 10, 
        textStyle: { fontSize: 10 } 
      } : { show: false },
      series: pieData.length > 0 ? [{
        name: '类别', 
        type: 'pie', 
        radius: ['35%', '60%'], 
        center: ['50%', '55%'], 
        avoidLabelOverlap: true,
        itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
        label: { show: false },
        emphasis: { label: { show: false } },
        labelLine: { show: false },
        data: pieData
      }] : []
    })
  }

  if (wordCloudInstance) {
    wordCloudInstance.setOption({
      title: { 
        text: wordCloudData.length > 0 ? '热门心愿词云' : '暂无数据', 
        left: 'center', 
        top: '6%', 
        textStyle: { fontSize: isMobile ? 20 : 24, fontFamily: 'serif' } 
      },
      series: [{
        type: 'wordCloud', 
        shape: 'circle', 
        left: 'center', 
        top: '10%', 
        width: '95%', 
        height: '95%',
        sizeRange: [10, 22],
        rotationRange: [0, 0], 
        rotationStep: 0, 
        gridSize: 10, 
        drawOutOfBound: false,
        layoutAnimation: true,
        textStyle: {
          fontFamily: 'sans-serif', 
          fontWeight: 'bold', 
          color: () => 'rgb(' + [
            Math.round(Math.random() * 160), Math.round(Math.random() * 160), Math.round(Math.random() * 160)
          ].join(',') + ')'
        },
        emphasis: { focus: 'self', textStyle: { shadowBlur: 10, shadowColor: '#333' } },
        data: wordCloudData.map(item => ({ name: item.word, value: item.count }))
      }]
    })
  }
}

function initCharts() {
  if (pieChartRef.value && !pieChartInstance) {
    pieChartInstance = echarts.init(pieChartRef.value)
  }

  if (wordCloudRef.value && !wordCloudInstance) {
    wordCloudInstance = echarts.init(wordCloudRef.value)
  }

  updateCharts()
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
  await loadStats()
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

defineExpose({
  refreshCharts
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
