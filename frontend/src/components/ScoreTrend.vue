<template>
  <div>
    <div style="font-size:13px; font-weight:700; color:#94a3b8; letter-spacing:0.06em; text-transform:uppercase; margin-bottom:12px">
      Score Trend
    </div>

    <div v-if="trendStore.lisHistory.length" class="row q-gutter-md q-mb-md">
      <div class="score-badge">
        <div class="score-badge-label">예측 정확도 (LIS)</div>
        <div class="score-badge-value" :style="{ color: lisColor }">{{ lisDisplay }}%</div>
        <div class="gauge-track"><div class="gauge-fill" :style="{ width: lisDisplay + '%', background: lisColor }" /></div>
      </div>
      <div class="score-badge">
        <div class="score-badge-label">목표 달성도 (TAS)</div>
        <div class="score-badge-value" :style="{ color: tasColor }">{{ tasDisplay }}%</div>
        <div class="gauge-track"><div class="gauge-fill" :style="{ width: tasDisplay + '%', background: tasColor }" /></div>
      </div>
    </div>

    <div class="row" style="gap: 16px">
      <div ref="lisChart" style="flex:1; min-height:280px" />
      <div ref="tasChart" style="flex:1; min-height:280px" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useTrendStore } from 'src/stores/trend'

const trendStore = useTrendStore()
const lisChart = ref<HTMLElement | null>(null)
const tasChart = ref<HTMLElement | null>(null)

const lisDisplay = computed(() => Math.round((trendStore.lisHistory.at(-1) ?? 0) * 100))
const tasDisplay = computed(() => Math.round((trendStore.tasHistory.at(-1) ?? 0) * 100))
function scoreColor(pct: number) {
  if (pct >= 80) return '#10b981'
  if (pct >= 60) return '#f59e0b'
  return '#ef4444'
}
const lisColor = computed(() => scoreColor(lisDisplay.value))
const tasColor = computed(() => scoreColor(tasDisplay.value))
let Plotly: typeof import('plotly.js-basic-dist') | null = null

const AXIS_BASE = { gridcolor: '#314158', zerolinecolor: '#314158', tickfont: { color: '#64748b' } }

const DARK_LAYOUT = {
  paper_bgcolor: '#1d293d',
  plot_bgcolor:  '#162032',
  font:  { color: '#94a3b8', size: 12 },
  xaxis: { title: { text: 'Num of Samples', font: { color: '#64748b', size: 11 } }, ...AXIS_BASE },
  yaxis: { rangemode: 'tozero' as const, ...AXIS_BASE },
  margin: { t: 58, b: 48, l: 60, r: 20 },
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
    { ...DARK_LAYOUT, title: { text: '예측 모델 영향력 추이<br><span style="font-size:11px">Learning Impact Score</span>', font: { color: '#e2e8f0', size: 14 } }, yaxis: YAXIS_LIS },
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
    { ...DARK_LAYOUT, title: { text: '목표 달성도 추이<br><span style="font-size:11px">Target Achievement Score</span>', font: { color: '#e2e8f0', size: 14 } }, yaxis: YAXIS_TAS },
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

<style scoped>
.score-badge {
  flex: 1;
  background: #1d293d;
  border: 1px solid rgba(49, 65, 88, 0.8);
  border-radius: 10px;
  padding: 12px 16px;
  min-width: 160px;
}
.score-badge-label {
  font-size: 11px;
  color: #64748b;
  font-weight: 600;
  letter-spacing: 0.04em;
  margin-bottom: 4px;
}
.score-badge-value {
  font-size: 26px;
  font-weight: 800;
  line-height: 1;
  margin-bottom: 8px;
}
.gauge-track {
  height: 5px;
  background: rgba(255, 255, 255, 0.07);
  border-radius: 3px;
  overflow: hidden;
}
.gauge-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.6s ease;
}
</style>
