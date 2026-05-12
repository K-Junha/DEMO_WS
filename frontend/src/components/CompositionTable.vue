<template>
  <div>
    <!-- Experiment Banner -->
    <ExperimentBanner class="q-mb-md" />

    <!-- Table -->
    <div class="table-wrap q-mb-md">
      <table class="comp-table">
        <thead>
          <tr>
            <th rowspan="2" style="width:70px">ID</th>
            <th rowspan="2" style="min-width:180px; text-align:left">조성</th>
            <th colspan="2">Tg (°C)</th>
            <th colspan="2">CTE (×10⁻⁶/K)</th>
            <th colspan="2">유전율</th>
            <th colspan="2">유전상수</th>
            <th class="lis-group" colspan="5">— LIS 그룹 —</th>
            <th class="tas-group" colspan="5">— TAS 그룹 —</th>
            <th rowspan="2" style="width:90px">튜닝</th>
          </tr>
          <tr>
            <th>예측</th><th>측정</th>
            <th>예측</th><th>측정</th>
            <th>예측</th><th>측정</th>
            <th>예측</th><th>측정</th>
            <th class="lis-group" style="font-size:10px">오차Tg</th>
            <th class="lis-group" style="font-size:10px">오차CTE</th>
            <th class="lis-group" style="font-size:10px">오차유전율</th>
            <th class="lis-group" style="font-size:10px">오차유전상수</th>
            <th class="lis-group">LIS</th>
            <th class="tas-group" style="font-size:10px">오차Tg</th>
            <th class="tas-group" style="font-size:10px">오차CTE</th>
            <th class="tas-group" style="font-size:10px">오차유전율</th>
            <th class="tas-group" style="font-size:10px">오차유전상수</th>
            <th class="tas-group">TAS</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="experimentStore.rows.length === 0">
            <td colspan="21" style="text-align:center; color:#4b5563; padding: 32px; font-size:13px">
              실험 설계 후 시작하세요
            </td>
          </tr>
          <tr v-for="row in experimentStore.rows" :key="row.id">
            <td style="font-family:monospace; font-size:12px; color:#94a3b8">{{ row.id }}</td>
            <td style="text-align:left; color:#e2e8f0; font-weight:500">{{ row.composition }}</td>
            <td>{{ row.predicted.tg }}</td>
            <td :class="row.measurement.tg !== null ? 'measured-val' : ''">{{ fmt(row.measurement.tg) }}</td>
            <td>{{ row.predicted.cte }}</td>
            <td :class="row.measurement.cte !== null ? 'measured-val' : ''">{{ fmt(row.measurement.cte) }}</td>
            <td>{{ row.predicted.dielectric }}</td>
            <td :class="row.measurement.dielectric !== null ? 'measured-val' : ''">{{ fmt(row.measurement.dielectric) }}</td>
            <td>{{ row.predicted.dielectric_const }}</td>
            <td :class="row.measurement.dielectric_const !== null ? 'measured-val' : ''">{{ fmt(row.measurement.dielectric_const) }}</td>
            <!-- LIS -->
            <td class="lis-group">{{ fmtErr(predErr(row, 'tg')) }}</td>
            <td class="lis-group">{{ fmtErr(predErr(row, 'cte')) }}</td>
            <td class="lis-group">{{ fmtErr(predErr(row, 'dielectric')) }}</td>
            <td class="lis-group">{{ fmtErr(predErr(row, 'dielectric_const')) }}</td>
            <td class="lis-group score-val">{{ row.lis !== null ? row.lis.toFixed(3) : '—' }}</td>
            <!-- TAS -->
            <td class="tas-group">{{ fmtErr(targetErr(row, 'tg')) }}</td>
            <td class="tas-group">{{ fmtErr(targetErr(row, 'cte')) }}</td>
            <td class="tas-group">{{ fmtErr(targetErr(row, 'dielectric')) }}</td>
            <td class="tas-group">{{ fmtErr(targetErr(row, 'dielectric_const')) }}</td>
            <td class="tas-group score-val">{{ row.tas !== null ? row.tas.toFixed(3) : '—' }}</td>
            <!-- Tune -->
            <td>
              <q-btn
                v-if="row.experimentDone"
                unelevated
                size="xs"
                label="튜닝"
                color="indigo"
                style="border-radius:5px; font-size:11px"
                @click="handleTune(row)"
              />
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Global Target Card -->
    <div v-if="configStore.config" class="target-card">
      <div style="font-size:11px; font-weight:700; color:#94a3b8; letter-spacing:0.08em; text-transform:uppercase; margin-bottom:12px">
        전체 공통 목표치
      </div>
      <div class="row q-gutter-md">
        <div v-for="item in targetItems" :key="item.label" class="target-item">
          <div class="target-label">{{ item.label }}</div>
          <div class="target-value">{{ item.value }}</div>
          <div class="target-unit">{{ item.unit }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useExperimentStore, type SampleRow } from 'src/stores/experiment'
import { useConfigStore } from 'src/stores/config'
import ExperimentBanner from './ExperimentBanner.vue'

type Prop4Key = 'tg' | 'cte' | 'dielectric' | 'dielectric_const'

const experimentStore = useExperimentStore()
const configStore = useConfigStore()

const targetItems = computed(() => {
  const gt = configStore.config?.global_target
  if (!gt) return []
  return [
    { label: 'Tg',    value: gt.tg,              unit: '°C' },
    { label: 'CTE',   value: gt.cte,             unit: '×10⁻⁶/K' },
    { label: '유전율', value: gt.dielectric,      unit: '' },
    { label: '유전상수', value: gt.dielectric_const, unit: '' },
  ]
})

function fmt(v: number | null): string { return v !== null ? String(v) : '—' }
function fmtErr(v: number | null): string { return v !== null ? (v * 100).toFixed(1) + '%' : '—' }

function predErr(row: SampleRow, key: Prop4Key): number | null {
  const m = row.measurement[key]
  if (m === null) return null
  return Math.abs(row.predicted[key] - m) / Math.abs(m)
}

function targetErr(row: SampleRow, key: Prop4Key): number | null {
  const m = row.measurement[key]
  if (m === null || !configStore.config) return null
  const target = configStore.config.global_target[key] as number
  return Math.abs(m - target) / Math.abs(target)
}

function handleTune(row: SampleRow) {
  const samples = configStore.config?.samples
  if (!samples) return
  const srcId = row.sourceId ?? row.id
  const src = samples.find(s => s.id === srcId)
  if (!src) return
  const nextIdx = samples.indexOf(src) + 1
  if (nextIdx < samples.length) experimentStore.addAutoTuneRow(samples[nextIdx])
}
</script>

<style scoped>
.measured-val { color: #22c55e; font-weight: 600; }
.score-val    { font-weight: 700; font-size: 13px; }

.target-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 100px;
}
.target-label {
  font-size: 11px;
  color: #94a3b8;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: 4px;
}
.target-value {
  font-size: 22px;
  font-weight: 700;
  color: #e2e8f0;
  line-height: 1;
}
.target-unit {
  font-size: 10px;
  color: #64748b;
  margin-top: 3px;
}
</style>
