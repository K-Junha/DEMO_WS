<template>
  <!-- 9개 장치 카드를 가로로 나열 -->
  <div class="row q-gutter-sm flex-wrap">
    <DeviceCard
      v-for="(device, i) in devices"
      :key="device.id"
      :device="device"
      :active="activeIndex >= i"
      :exp-data="expDataFor(i)"
      :measurement="measurementFor(i)"
      :loading="isDeviceLoading(i)"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { useConfigStore, type SampleExperiment, type SampleMeasurement } from 'src/stores/config'
import { useExperimentStore } from 'src/stores/experiment'
import DeviceCard from './DeviceCard.vue'

const configStore = useConfigStore()
const experimentStore = useExperimentStore()

// 순차 점등 진행 상태: -1이면 모두 비활성, i이면 0~i 인덱스 카드가 활성화
const activeIndex = ref(-1)

// 로컬 runId: 리셋 또는 설정 재로드 시 이전 setTimeout 체인 무효화
let runId = 0

const devices = computed(() => configStore.config?.devices ?? [])

// 장치 카드를 device_activation_interval_ms 간격으로 순차 점등
function startActivation() {
  const id = ++runId
  activeIndex.value = -1
  const interval = configStore.config?.timing.device_activation_interval_ms ?? 1000
  devices.value.forEach((_, i) => {
    setTimeout(() => {
      if (id !== runId) return  // 재시작됐으면 중단
      activeIndex.value = i
    }, (i + 1) * interval)
  })
}

// 실험이 idle로 돌아올 때(리셋) 재점등, 앱 첫 로드 시에도 즉시 실행
watch(
  () => experimentStore.state,
  state => { if (state === 'idle') startActivation() },
  { immediate: true }
)
// 설정이 새로 로드되면 장치 목록이 바뀔 수 있으므로 재점등
watch(() => configStore.config, cfg => { if (cfg) startActivation() })

/**
 * 현재 표시할 샘플 데이터를 결정
 * - running/done 상태: 마지막 행의 sourceId로 샘플 조회
 * - designed 상태 + 완료된 행 있음: 마지막 완료 행의 샘플 조회
 *   (auto-tune이 state를 'designed'로 되돌려도 이전 실험 데이터를 유지)
 */
function getSample() {
  const rows = experimentStore.rows

  if (experimentStore.state === 'designed') {
    // 튜닝 후 state='designed'가 돼도 직전 완료 실험 데이터를 계속 표시
    const doneRow = [...rows].reverse().find(r => r.experimentDone)
    if (doneRow) {
      const srcId = doneRow.sourceId ?? doneRow.id
      return configStore.config?.samples.find(s => s.id === srcId) ?? null
    }
  }

  const lastRow = rows[rows.length - 1]
  if (!lastRow) return null
  const srcId = lastRow.sourceId ?? lastRow.id
  return configStore.config?.samples.find(s => s.id === srcId) ?? null
}

/**
 * 해당 장치가 "데이터를 표시할 수 있는 완료 상태"인지 판단
 * - running 중: 해당 장치가 complete 됐거나 이미 지나간 경우만 true
 *   (phase='running'인 현재 장치는 false → 로딩 상태로 표시)
 * - done/designed(완료 행 있음): 전체 완료로 모두 표시
 */
function isStepReached(deviceIdx: number): boolean {
  const { state, currentPhase, rows } = experimentStore
  if (state === 'running') {
    if (currentPhase.deviceIndex > deviceIdx) return true
    if (currentPhase.deviceIndex === deviceIdx && currentPhase.phase === 'complete') return true
    return false
  }
  if (state === 'done') return true
  if (state === 'designed' && rows.some(r => r.experimentDone)) return true
  return false
}

// 해당 장치가 현재 실험 진행 중(running phase)인지 → DeviceCard shimmer 로딩용
function isDeviceLoading(deviceIdx: number): boolean {
  const { state, currentPhase } = experimentStore
  return (
    state === 'running' &&
    currentPhase.deviceIndex === deviceIdx &&
    currentPhase.phase === 'running'
  )
}

// 장치 카드에 전달할 실험 파라미터 (저울 세팅값, 전기로 온도 등)
function expDataFor(deviceIdx: number): SampleExperiment | null {
  if (activeIndex.value < deviceIdx) return null
  if (!isStepReached(deviceIdx)) return null
  return getSample()?.experiment ?? null
}

// 장치 카드에 전달할 측정값 (DTA/DSC → Tg, 딜라토미터 → CTE 등)
function measurementFor(deviceIdx: number): SampleMeasurement | null {
  if (activeIndex.value < deviceIdx) return null
  if (!isStepReached(deviceIdx)) return null
  return getSample()?.measurement ?? null
}
</script>
