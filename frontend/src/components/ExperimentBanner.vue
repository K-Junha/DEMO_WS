<template>
  <!-- 실험 진행 중 팝업: 현재 장치명 + 보고서 넘기는 애니메이션 -->
  <q-dialog v-model="showDialog" persistent>
    <q-card class="exp-popup">
      <!-- 장치명 + 상태 -->
      <div class="popup-title">
        <q-icon name="science" size="18px" color="indigo-4" />
        <span class="device-label">
          [{{ currentDeviceName }}]
          <span v-if="isDone" class="done-text">실험 완료</span>
          <span v-else-if="experimentStore.currentPhase.phase === 'complete'" class="done-text">완료</span>
          <span v-else class="running-text">실험 중</span>
        </span>
      </div>

      <!-- 시뮬레이션 중지 버튼 -->
      <div v-if="experimentStore.simulating" style="text-align: right; margin-bottom: 8px">
        <q-btn
          flat dense size="sm"
          icon="stop" label="중지"
          color="orange-4"
          style="font-size: 11px; border: 1px solid rgba(251,146,60,0.4); border-radius: 5px; padding: 2px 8px"
          @click="experimentStore.setSimulating(false)"
        />
      </div>

      <!-- 보고서 페이지 넘기는 애니메이션 -->
      <div class="paper-stage">
        <div v-for="n in 4" :key="n" class="paper" :style="`animation-delay: ${(n - 1) * 0.45}s`">
          <div class="pline full" />
          <div class="pline short" />
          <div class="pline full" />
          <div class="pline mid" />
          <div class="pline full" />
          <div class="pline short" />
          <div class="pline mid" />
        </div>
      </div>

      <!-- 진행률 바 -->
      <div class="popup-progress">
        <div class="prog-track">
          <div class="prog-fill" :style="{ width: progressPct + '%' }" />
        </div>
        <span class="prog-label">{{ Math.round(progressPct) }}%</span>
      </div>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useExperimentStore } from 'src/stores/experiment'
import { useConfigStore } from 'src/stores/config'
import { useTrendStore } from 'src/stores/trend'
import { calcLIS, calcTAS } from 'src/utils/scores'

const experimentStore = useExperimentStore()
const configStore = useConfigStore()
const trendStore = useTrendStore()

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

const showDialog = ref(false)
const isDone     = ref(false)

// 현재 진행 중인 장치 이름
const currentDeviceName = computed(() => {
  const idx = experimentStore.currentPhase.deviceIndex
  return DEVICES[idx]?.name ?? ''
})

// 진행률: running=0.5 / complete=1.0 단위로 부드럽게 증가
const progressPct = computed(() => {
  const { deviceIndex, phase } = experimentStore.currentPhase
  const step = deviceIndex + (phase === 'complete' ? 1 : 0.5)
  return Math.min(100, (step / DEVICES.length) * 100)
})

// 실험 시작 → 팝업 열기 / 완료 → 잠시 후 닫기
watch(() => experimentStore.state, state => {
  if (state === 'running') {
    isDone.value = false
    showDialog.value = true
    runExperiment(experimentStore.incrementRunId())
  } else if (state === 'done') {
    isDone.value = true
    setTimeout(() => { showDialog.value = false }, 1600)
  }
})

function timing() {
  const t = configStore.config?.timing
  return {
    running:  t?.experiment_running_ms  ?? 2000,
    complete: t?.experiment_complete_ms ?? 1000,
    gap:      t?.experiment_gap_ms      ?? 500,
  }
}

// 장치별 순차 애니메이션 (runId로 stale 방지)
function runExperiment(id: number) {
  const t = timing()

  function step(i: number) {
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

function finishExperiment() {
  const cfg = configStore.config
  if (!cfg) return
  const rows = experimentStore.rows
  const lastRow = rows[rows.length - 1]
  if (!lastRow) return

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
/* ── 팝업 카드 ── */
.exp-popup {
  background: #131e30;
  border: 1px solid rgba(97, 95, 255, 0.45);
  border-radius: 14px;
  padding: 28px 32px 22px;
  min-width: 320px;
  text-align: center;
  overflow: hidden;
}

/* ── 제목 영역 ── */
.popup-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 24px;
}
.device-label {
  font-size: 18px;
  font-weight: 700;
  color: #e2e8f0;
  letter-spacing: 0.04em;
}
.running-text {
  color: #615fff;
  margin-left: 4px;
}
.done-text {
  color: #10b981;
  margin-left: 4px;
}

/* ── 보고서 페이지 넘기는 애니메이션 ── */
.paper-stage {
  position: relative;
  width: 140px;
  height: 100px;
  margin: 0 auto 22px;
}

.paper {
  position: absolute;
  inset: 0;
  background: rgba(226, 232, 240, 0.05);
  border: 1px solid rgba(97, 95, 255, 0.25);
  border-radius: 5px;
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 7px;
  animation: pageFlip 1.8s ease-in-out infinite;
  transform-origin: bottom center;
}

@keyframes pageFlip {
  0%   { transform: translateY(30px) rotate(4deg) scale(0.88); opacity: 0; }
  12%  { transform: translateY(0) rotate(0deg) scale(1);       opacity: 1; }
  70%  { transform: translateY(0) rotate(0deg) scale(1);       opacity: 1; }
  100% { transform: translateY(-30px) rotate(-4deg) scale(0.88); opacity: 0; }
}

.pline {
  height: 7px;
  background: rgba(97, 95, 255, 0.35);
  border-radius: 3px;
  animation: shimmerLine 1.8s ease-in-out infinite;
}
.pline.short { width: 50%; }
.pline.mid   { width: 70%; }
.pline.full  { width: 100%; }

@keyframes shimmerLine {
  0%, 100% { opacity: 0.3; }
  50%       { opacity: 0.8; }
}

/* ── 진행률 바 ── */
.popup-progress {
  display: flex;
  align-items: center;
  gap: 10px;
}
.prog-track {
  flex: 1;
  height: 5px;
  background: rgba(255, 255, 255, 0.07);
  border-radius: 3px;
  overflow: hidden;
}
.prog-fill {
  height: 100%;
  background: linear-gradient(90deg, #615fff, #10b981);
  border-radius: 3px;
  transition: width 0.6s ease;
}
.prog-label {
  font-size: 12px;
  color: #615fff;
  font-weight: 700;
  min-width: 36px;
  text-align: right;
}
</style>
