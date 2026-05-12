import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from 'src/boot/axios'

export interface DeviceConfig {
  id: string
  name: string
  model: string
  protocol: string
  ip: string
  port: number
  connected: boolean
  measures?: string[]
}

export interface SampleExperimentStep {
  step: number
  target_temp: number
  measured_temp: number
  hold_time: string
  heating_rate: number
}

export interface SampleExperiment {
  scale?: { target_weight: number; current_weight: number }
  mixer?: { operation_time: string }
  furnace?: { steps: SampleExperimentStep[] }
  annealing?: { target_temp: number; stop_temp: number; time: string }
  press?: { pressure: number }
}

export interface SampleMeasurement {
  tg: number
  cte: number
  dielectric: number
  dielectric_const: number
}

export interface Sample {
  id: string
  composition: string
  predicted: SampleMeasurement
  measurement: SampleMeasurement
  next_composition: string
  experiment: SampleExperiment
}

export interface GlobalTarget {
  tg: number
  cte: number
  dielectric: number
  dielectric_const: number
  weights: { tg: number; cte: number; dielectric: number; dielectric_const: number }
}

export interface Timing {
  device_activation_interval_ms: number
  experiment_running_ms: number
  experiment_complete_ms: number
  experiment_gap_ms: number
}

export interface RandomRange {
  tg: { min: number; max: number }
  cte: { min: number; max: number }
  dielectric: { min: number; max: number }
  dielectric_const: { min: number; max: number }
}

export interface AppConfig {
  timing: Timing
  global_target: GlobalTarget
  auto_tune_enabled: boolean
  random_range: RandomRange
  devices: DeviceConfig[]
  samples: Sample[]
}

export const useConfigStore = defineStore('config', () => {
  const config = ref<AppConfig | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchConfig() {
    loading.value = true
    error.value = null
    try {
      const res = await api.get<AppConfig>('/config')
      config.value = res.data
    } catch (e) {
      error.value = String(e)
    } finally {
      loading.value = false
    }
  }

  function updateGlobalTarget(gt: Partial<GlobalTarget>) {
    if (config.value) {
      config.value.global_target = { ...config.value.global_target, ...gt }
    }
  }

  return { config, loading, error, fetchConfig, updateGlobalTarget }
})
