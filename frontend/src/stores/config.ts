// 설정 스토어: 백엔드 /api/config에서 YAML 설정을 가져와 전역 공유
// YAML 파일(config/demo_data.yaml)이 변경되면 백엔드가 자동 감지(hot-reload)

import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from 'src/boot/axios'

// 장치 1개의 설정 (저울, 믹서, 전기로 등)
export interface DeviceConfig {
  id: string
  name: string
  model: string
  protocol: string  // RS-232 / RS-485 / Ethernet
  ip: string
  port: number
  connected: boolean
  measures?: string[]  // 이 장치가 측정하는 물성 목록
}

// 전기로 단계별 승온 정보
export interface SampleExperimentStep {
  step: number
  target_temp: number
  measured_temp: number
  hold_time: string
  heating_rate: number
}

// YAML 샘플에 포함된 장치별 실험 파라미터 (DeviceCard에 표시)
export interface SampleExperiment {
  scale?: { target_weight: number; current_weight: number }
  mixer?: { operation_time: string }
  furnace?: { steps: SampleExperimentStep[] }
  annealing?: { target_temp: number; stop_temp: number; time: string }
  press?: { pressure: number }
}

// 4가지 물성 측정값 (DTA/DSC/딜라토미터/유전율측정기 결과)
export interface SampleMeasurement {
  tg: number
  cte: number
  dielectric: number
  dielectric_const: number
}

// YAML 샘플 1개 (S-001 ~ S-020)
export interface Sample {
  id: string
  composition: string
  predicted: SampleMeasurement   // AI 예측값
  measurement: SampleMeasurement // 실제 측정값 (실험 완료 시 사용)
  next_composition: string        // 다음 튜닝 추천 조성
  experiment: SampleExperiment   // 장치별 실험 파라미터
}

// 전체 목표치와 각 물성의 가중치 (TAS 계산에 사용)
export interface GlobalTarget {
  tg: number
  cte: number
  dielectric: number
  dielectric_const: number
  weights: { tg: number; cte: number; dielectric: number; dielectric_const: number }
}

// 실험 애니메이션 타이밍 설정 (YAML에서 조정 가능)
export interface Timing {
  device_activation_interval_ms: number  // 장치 순차 점등 간격
  experiment_running_ms: number          // 각 장치 '진행중' 표시 시간
  experiment_complete_ms: number         // 각 장치 '완료' 표시 시간
  experiment_gap_ms: number              // 다음 장치로 넘어가는 간격
}

export interface RandomRange {
  tg: { min: number; max: number }
  cte: { min: number; max: number }
  dielectric: { min: number; max: number }
  dielectric_const: { min: number; max: number }
}

// 전체 앱 설정 (YAML 루트 구조와 1:1 대응)
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

  // 앱 시작 시 또는 새로고침 시 백엔드에서 설정 로드
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

  // 실험 설계 모달에서 목표치를 수정할 때 호출
  // 백엔드 재요청 없이 프론트엔드 메모리만 업데이트
  function updateGlobalTarget(gt: Partial<GlobalTarget>) {
    if (config.value) {
      config.value.global_target = { ...config.value.global_target, ...gt }
    }
  }

  return { config, loading, error, fetchConfig, updateGlobalTarget }
})
