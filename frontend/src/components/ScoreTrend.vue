<template>
  <div>
    <div style="font-size:13px; font-weight:700; color:#94a3b8; letter-spacing:0.06em; text-transform:uppercase; margin-bottom:16px">
      Score Trend
    </div>
    <div class="row" style="gap: 16px">
      <div ref="lisChart" style="flex:1; min-height:280px" />
      <div ref="tasChart" style="flex:1; min-height:280px" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useTrendStore } from 'src/stores/trend'

const trendStore = useTrendStore()
const lisChart = ref<HTMLElement | null>(null)
const tasChart = ref<HTMLElement | null>(null)
let Plotly: typeof import('plotly.js-basic-dist') | null = null

const AXIS_BASE = { gridcolor: '#314158', zerolinecolor: '#314158', tickfont: { color: '#64748b' } }

const DARK_LAYOUT = {
  paper_bgcolor: '#1d293d',
  plot_bgcolor:  '#162032',
  font:  { color: '#94a3b8', size: 12 },
  xaxis: { title: { text: 'Num of Samples', font: { color: '#64748b', size: 11 } }, ...AXIS_BASE },
  yaxis: { rangemode: 'tozero' as const, ...AXIS_BASE },
  margin: { t: 44, b: 48, l: 60, r: 20 },
}

async function loadPlotly() {
  Plotly = (await import('plotly.js-basic-dist')) as typeof import('plotly.js-basic-dist')
  renderCharts()
}

function xArr(len: number): number[] { return Array.from({ length: len }, (_, i) => i + 1) }

function renderCharts() {
  if (!Plotly || !lisChart.value || !tasChart.value) return
  const lisCum  = trendStore.lisCumulative  // 누적합 (LIS: 전체 정확도 추이)
  const tasRaw  = trendStore.tasHistory      // 회차별 원본값 (TAS: 목표 근접도 변화)

  const YAXIS_LIS = { rangemode: 'tozero' as const, ...AXIS_BASE, title: { text: 'LIS', font: { color: '#64748b', size: 11 } } }
  const YAXIS_TAS = { rangemode: 'tozero' as const, ...AXIS_BASE, title: { text: 'TAS', font: { color: '#64748b', size: 11 } } }

  Plotly!.react(
    lisChart.value,
    [{
      x: xArr(lisCum.length), y: lisCum,
      type: 'scatter', mode: 'lines+markers',
      line: { color: '#3b82f6', width: 2 },
      marker: { color: '#3b82f6', size: 7 },
      fill: 'tozeroy', fillcolor: 'rgba(59,130,246,0.08)',
      name: 'LIS cumulative',
    }],
    { ...DARK_LAYOUT, title: { text: '예측 모델 영향력 추이<br><span style="font-size:11px">LIS: Learning Impact Score</span>', font: { color: '#e2e8f0', size: 14 } }, yaxis: YAXIS_LIS },
    { responsive: true }
  )

  Plotly!.react(
    tasChart.value,
    [{
      x: xArr(tasRaw.length), y: tasRaw,
      type: 'scatter', mode: 'lines+markers',
      line: { color: '#10b981', width: 2 },
      marker: { color: '#10b981', size: 7 },
      fill: 'tozeroy', fillcolor: 'rgba(16,185,129,0.08)',
      name: 'TAS per experiment',
    }],
    { ...DARK_LAYOUT, title: { text: '목표 달성도 추이<br><span style="font-size:11px">TAS: Target Achievement Score</span>', font: { color: '#e2e8f0', size: 14 } }, yaxis: YAXIS_TAS },
    { responsive: true }
  )
}

watch(() => [trendStore.lisCumulative, trendStore.tasHistory], renderCharts, { deep: true })
onMounted(loadPlotly)
onUnmounted(() => {
  if (Plotly && lisChart.value) Plotly.purge(lisChart.value)
  if (Plotly && tasChart.value) Plotly.purge(tasChart.value)
})
</script>
