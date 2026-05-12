<template>
  <div class="row q-gutter-sm flex-wrap">
    <DeviceCard
      v-for="(device, i) in devices"
      :key="device.id"
      :device="device"
      :active="activeIndex >= i"
      :exp-data="expDataFor(i)"
      :measurement="measurementFor(i)"
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

const activeIndex = ref(-1)
let runId = 0

const devices = computed(() => configStore.config?.devices ?? [])

function startActivation() {
  const id = ++runId
  activeIndex.value = -1
  const interval = configStore.config?.timing.device_activation_interval_ms ?? 1000
  devices.value.forEach((_, i) => {
    setTimeout(() => {
      if (id !== runId) return
      activeIndex.value = i
    }, (i + 1) * interval)
  })
}

watch(
  () => experimentStore.state,
  state => { if (state === 'idle') startActivation() },
  { immediate: true }
)
watch(() => configStore.config, cfg => { if (cfg) startActivation() })

function isStepReached(deviceIdx: number): boolean {
  const { state, currentPhase, rows } = experimentStore
  if (state === 'running' || state === 'done') {
    return currentPhase.deviceIndex >= deviceIdx
  }
  // After auto-tune adds next row (state → 'designed'), keep showing previous experiment's device data
  if (state === 'designed' && rows.some(r => r.experimentDone)) {
    return true
  }
  return false
}

function getSample() {
  const rows = experimentStore.rows
  // When 'designed' with completed rows, show the last completed experiment (not the pending auto-tune row)
  if (experimentStore.state === 'designed') {
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

function expDataFor(deviceIdx: number): SampleExperiment | null {
  if (activeIndex.value < deviceIdx) return null
  if (!isStepReached(deviceIdx)) return null
  return getSample()?.experiment ?? null
}

function measurementFor(deviceIdx: number): SampleMeasurement | null {
  if (activeIndex.value < deviceIdx) return null
  if (!isStepReached(deviceIdx)) return null
  return getSample()?.measurement ?? null
}
</script>
