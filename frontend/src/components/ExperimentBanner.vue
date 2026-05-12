<template>
  <!-- 실험 진행 중일 때만 배너 표시 -->
  <div v-if="experimentStore.state === 'running'" class="exp-stepper">
    <!-- 상단: 제목 + 진행률 바 -->
    <div class="stepper-header">
      <q-icon name="science" size="13px" color="indigo-4" />
      <span>실험 진행 중</span>
      <div class="progress-track">
        <div class="progress-fill" :style="{ width: progressPct + '%' }" />
      </div>
      <span style="font-size: 11px; color: #615fff; min-width: 34px; text-align: right">
        {{ Math.round(progressPct) }}%
      </span>
    </div>

    <!-- 9단계 스텝퍼: 완료(초록) / 진행중(인디고 스피너) / 대기(반투명) -->
    <div class="steps-row">
      <div
        v-for="(d, i) in DEVICES"
        :key="d.name"
        class="step-item"
        :class="{
          'step-done':    i < curDeviceIdx || (i === curDeviceIdx && curPhase === 'complete'),
          'step-active':  i === curDeviceIdx && curPhase === 'running',
          'step-pending': i > curDeviceIdx,
        }"
      >
        <div class="step-icon-wrap">
          <q-spinner v-if="i === curDeviceIdx && curPhase === 'running'" size="11px" />
          <q-icon
            v-else-if="i < curDeviceIdx || (i === curDeviceIdx && curPhase === 'complete')"
            name="check"
            size="11px"
          />
          <q-icon v-else :name="d.icon" size="11px" />
        </div>
        <div class="step-name">{{ d.name }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'
import { useExperimentStore } from 'src/stores/experiment'
import { useConfigStore } from 'src/stores/config'
import { useTrendStore } from 'src/stores/trend'
import { calcLIS, calcTAS } from 'src/utils/scores'

const experimentStore = useExperimentStore()
const configStore = useConfigStore()
const trendStore = useTrendStore()

// 9개 장치 순서 (YAML devices 순서와 일치해야 함)
const DEVICES = [
  { name: '저울',         icon: 'balance' },
  { name: '믹서',         icon: 'rotate_right' },
  { name: '전기로',       icon: 'whatshot' },
  { name: '서냉로',       icon: 'thermostat' },
  { name: '프레스',       icon: 'vertical_align_center' },
  { name: 'DTA',          icon: 'show_chart' },
  { name: 'DSC',          icon: 'analytics' },
  { name: '딜라토미터',   icon: 'straighten' },
  { name: '유전율측정기', icon: 'bolt' },
]

const curDeviceIdx = computed(() => experimentStore.currentPhase.deviceIndex)
const curPhase     = computed(() => experimentStore.currentPhase.phase)

// 진행률: 각 장치를 running(0.5) → complete(1.0)로 세분화하여 부드럽게 표시
const progressPct = computed(() => {
  if (experimentStore.state !== 'running') return 0
  const step = curDeviceIdx.value + (curPhase.value === 'complete' ? 1 : 0.5)
  return Math.min(100, (step / DEVICES.length) * 100)
})

// YAML 타이밍 설정을 가져오는 헬퍼 (기본값 포함)
function timing() {
  const t = configStore.config?.timing
  return {
    running:  t?.experiment_running_ms  ?? 2000,
    complete: t?.experiment_complete_ms ?? 1000,
    gap:      t?.experiment_gap_ms      ?? 500,
  }
}

// state가 'running'이 될 때마다 새 실험 애니메이션 시작
// incrementRunId()로 이전 타이머 체인을 무효화하여 중복 실행 방지
watch(
  () => experimentStore.state,
  state => { if (state === 'running') runExperiment(experimentStore.incrementRunId()) }
)

// 장치별 순차 애니메이션: running → complete → (gap) → 다음 장치
function runExperiment(id: number) {
  const t = timing()

  function step(i: number) {
    // runId가 다르면 리셋/재시작된 것이므로 중단
    if (id !== experimentStore.getRunId()) return
    if (i >= DEVICES.length) { finishExperiment(); return }

    experimentStore.setPhase(i, 'running')

    setTimeout(() => {
      if (id !== experimentStore.getRunId()) return
      experimentStore.setPhase(i, 'complete')

      setTimeout(() => {
        if (id !== experimentStore.getRunId()) return
        setTimeout(() => {
          if (id !== experimentStore.getRunId()) return
          step(i + 1)
        }, t.gap)
      }, t.complete)
    }, t.running)
  }

  step(0)
}

// 모든 장치 완료 후 호출: 측정값 저장, LIS/TAS 계산, trend 누적
function finishExperiment() {
  const cfg = configStore.config
  if (!cfg) return
  const rows = experimentStore.rows
  const lastRow = rows[rows.length - 1]
  if (!lastRow) return

  // sourceId로 YAML 샘플을 찾아 실제 측정값 사용; 없으면 예측값으로 대체
  const srcSample = cfg.samples.find(s => s.id === lastRow.sourceId || s.id === lastRow.id)
  const measurement = srcSample?.measurement ?? lastRow.predicted

  const gt  = cfg.global_target
  const lis = calcLIS(lastRow.predicted, measurement)
  const tas = calcTAS(measurement, gt, gt.weights)

  experimentStore.completeExperiment(
    { tg: measurement.tg, cte: measurement.cte, dielectric: measurement.dielectric, dielectric_const: measurement.dielectric_const },
    lis, tas
  )
  trendStore.addEntry(lis, tas)
}
</script>

<style scoped>
.exp-stepper {
  background: rgba(97,95,255,0.07);
  border: 1px solid rgba(97,95,255,0.22);
  border-radius: 10px;
  padding: 12px 16px;
}

.stepper-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  font-weight: 700;
  color: #94a3b8;
  letter-spacing: 0.07em;
  text-transform: uppercase;
  margin-bottom: 12px;
}

.progress-track {
  flex: 1;
  height: 4px;
  background: rgba(255,255,255,0.07);
  border-radius: 2px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #615fff, #10b981);
  border-radius: 2px;
  transition: width 0.6s ease;
}

.steps-row {
  display: flex;
  gap: 4px;
}

.step-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  padding: 8px 2px;
  border-radius: 7px;
  transition: background 0.3s, opacity 0.3s;
}

.step-done    { background: rgba(16,185,129,0.13); }
.step-active  { background: rgba(97,95,255,0.18); }
.step-pending { opacity: 0.3; }

.step-icon-wrap {
  width: 24px; height: 24px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
}
.step-done   .step-icon-wrap { background: rgba(16,185,129,0.25); color: #10b981; }
.step-active .step-icon-wrap { background: rgba(97,95,255,0.35);  color: #615fff; }
.step-pending .step-icon-wrap { color: #4b5563; }

.step-name {
  font-size: 9px;
  color: #64748b;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}
.step-done   .step-name { color: #10b981; }
.step-active .step-name { color: #a5b4fc; font-weight: 600; }
</style>
