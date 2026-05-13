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

    <!-- 튜닝 팝업: 조성 분석 중 → 추천 조성 표시 -->
    <q-dialog v-model="tuneDialog" persistent>
      <q-card class="tune-popup">
        <!-- 분석 중 애니메이션 -->
        <template v-if="tuneAnalyzing">
          <div class="tune-title">
            <q-icon name="biotech" size="20px" color="indigo-4" />
            <span>조성 분석 중...</span>
          </div>
          <div class="dna-stage">
            <div v-for="n in 5" :key="n" class="dna-bar" :style="`animation-delay: ${(n-1)*0.15}s`" />
          </div>
          <div style="font-size:12px; color:#64748b; text-align:center">실험 데이터를 기반으로 최적 조성을 계산하고 있습니다</div>
        </template>

        <!-- 추천 결과 표시 -->
        <template v-else>
          <div class="tune-title">
            <q-icon name="auto_fix_high" size="20px" color="positive" />
            <span style="color:#10b981">추천 조성</span>
          </div>
          <div class="tune-result">
            <div style="font-size:11px; color:#64748b; margin-bottom:6px; text-transform:uppercase; letter-spacing:0.06em">다음 실험 조성</div>
            <div class="comp-chip">{{ tuneNextComp }}</div>
          </div>
          <div class="row justify-end q-gutter-sm q-mt-md">
            <q-btn flat label="취소" color="grey-5" size="sm" @click="tuneDialog = false" />
            <q-btn unelevated label="실험 설계 추가" color="indigo" size="sm" style="border-radius:6px" @click="confirmTune" />
          </div>
        </template>
      </q-card>
    </q-dialog>

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
import { ref, computed } from 'vue'
import { useExperimentStore, type SampleRow } from 'src/stores/experiment'
import { useConfigStore, type Sample } from 'src/stores/config'
import ExperimentBanner from './ExperimentBanner.vue'

type Prop4Key = 'tg' | 'cte' | 'dielectric' | 'dielectric_const'

const experimentStore = useExperimentStore()
const configStore = useConfigStore()

// ── 튜닝 팝업 상태 ──
const tuneDialog      = ref(false)
const tuneAnalyzing   = ref(true)   // true: 분석 중 / false: 추천 결과 표시
const tuneNextSample  = ref<Sample | null>(null)
const tuneNextComp    = ref('')

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

// 튜닝 버튼 클릭 → 팝업 열기 + 분석 중 애니메이션 → 추천 조성 표시
function handleTune(row: SampleRow) {
  const samples = configStore.config?.samples
  if (!samples) return
  const srcId = row.sourceId ?? row.id
  const src = samples.find(s => s.id === srcId)
  if (!src) return
  const nextIdx = samples.indexOf(src) + 1
  if (nextIdx >= samples.length) return

  tuneNextSample.value = samples[nextIdx]
  tuneNextComp.value   = src.next_composition  // YAML에서 현재 샘플의 next_composition
  tuneAnalyzing.value  = true
  tuneDialog.value     = true

  // 1.8초 분석 애니메이션 후 추천 조성 표시
  setTimeout(() => { tuneAnalyzing.value = false }, 1800)
}

// 팝업 확인 → 다음 샘플 행 추가
function confirmTune() {
  if (tuneNextSample.value) {
    experimentStore.addAutoTuneRow(tuneNextSample.value)
  }
  tuneDialog.value = false
}
</script>

<style scoped>
.measured-val { color: #22c55e; font-weight: 600; }
.score-val    { font-weight: 700; font-size: 13px; }

/* ── 튜닝 팝업 ── */
.tune-popup {
  background: #131e30;
  border: 1px solid rgba(97,95,255,0.45);
  border-radius: 14px;
  padding: 28px 32px 22px;
  min-width: 300px;
}
.tune-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 700;
  color: #e2e8f0;
  margin-bottom: 20px;
  justify-content: center;
}
.tune-result {
  background: rgba(97,95,255,0.06);
  border: 1px solid rgba(97,95,255,0.2);
  border-radius: 8px;
  padding: 14px 16px;
  text-align: center;
}
.comp-chip {
  font-size: 15px;
  font-weight: 700;
  color: #e2e8f0;
  font-family: monospace;
  letter-spacing: 0.04em;
}

/* 분석 중 막대 애니메이션 */
.dna-stage {
  display: flex;
  justify-content: center;
  align-items: flex-end;
  gap: 6px;
  height: 50px;
  margin-bottom: 16px;
}
.dna-bar {
  width: 8px;
  border-radius: 4px;
  background: linear-gradient(180deg, #615fff, #10b981);
  animation: dnaWave 0.9s ease-in-out infinite alternate;
}
@keyframes dnaWave {
  0%   { height: 10px; opacity: 0.5; }
  100% { height: 44px; opacity: 1.0; }
}

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
