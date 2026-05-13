// 실험 상태 관리 스토어
// 상태 머신: idle → designed → running → done
//   idle    : 초기 상태 (실험 설계 전)
//   designed: 조성 설계 완료, 시작 버튼 활성화 대기
//   running : 실험 진행 중 (9단계 장치 순차 동작)
//   done    : 실험 완료, 측정값·LIS·TAS 저장됨

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Sample } from './config'

export type ExperimentState = 'idle' | 'designed' | 'running' | 'done'

// 현재 진행 중인 장치 인덱스와 단계(running/complete)
export interface ExperimentPhase {
  deviceIndex: number
  phase: 'running' | 'complete'
}

// 실험 테이블의 한 행 (조성 1개 실험 결과)
export interface SampleRow {
  id: string
  composition: string
  predicted: { tg: number; cte: number; dielectric: number; dielectric_const: number }
  measurement: { tg: number | null; cte: number | null; dielectric: number | null; dielectric_const: number | null }
  lis: number | null
  tas: number | null
  experimentDone: boolean
  sourceId: string | null  // 연결된 YAML 샘플 ID (측정값·실험 데이터 조회에 사용)
}

export const useExperimentStore = defineStore('experiment', () => {
  const state = ref<ExperimentState>('idle')
  const currentPhase = ref<ExperimentPhase>({ deviceIndex: 0, phase: 'running' })
  const rows = ref<SampleRow[]>([])
  const simulating = ref(false)

  // runId: setTimeout 체인의 stale 실행 방지용 단조 증가 카운터
  // 리셋/새 실험 시작 시 증가 → 이전 타이머 콜백이 체크 후 자동 종료됨
  let runId = 0
  const currentRunId = computed(() => runId)

  function getRunId() { return runId }
  function incrementRunId() { runId++; return runId }

  // 새 조성 행 추가 → state를 'designed'로 전환 (ID는 S-001, S-002... 자동 생성)
  function design(row: Omit<SampleRow, 'id' | 'measurement' | 'lis' | 'tas' | 'experimentDone'>) {
    const id = `S-${String(rows.value.length + 1).padStart(3, '0')}`
    rows.value.push({
      id,
      ...row,
      measurement: { tg: null, cte: null, dielectric: null, dielectric_const: null },
      lis: null,
      tas: null,
      experimentDone: false
    })
    state.value = 'designed'
  }

  // 실험 시작: state를 'running'으로 전환, 장치 인덱스 초기화
  function startExperiment() {
    if (state.value !== 'designed') return
    state.value = 'running'
    currentPhase.value = { deviceIndex: 0, phase: 'running' }
  }

  // ExperimentBanner의 애니메이션 루프가 호출하여 현재 진행 장치 갱신
  function setPhase(deviceIndex: number, phase: 'running' | 'complete') {
    currentPhase.value = { deviceIndex, phase }
  }

  // 실험 완료: 측정값·LIS·TAS를 마지막 행에 저장, state를 'done'으로 전환
  function completeExperiment(measurement: SampleRow['measurement'], lis: number, tas: number) {
    const lastRow = rows.value[rows.value.length - 1]
    if (lastRow) {
      lastRow.measurement = measurement
      lastRow.lis = lis
      lastRow.tas = tas
      lastRow.experimentDone = true
    }
    state.value = 'done'
  }

  // 튜닝 버튼 클릭 시: YAML의 다음 샘플을 새 행으로 추가 → state를 'designed'로 전환 (ID 자동 생성)
  function addAutoTuneRow(yamlSample: Sample) {
    const id = `S-${String(rows.value.length + 1).padStart(3, '0')}`
    rows.value.push({
      id,
      composition: yamlSample.composition,
      predicted: { ...yamlSample.predicted },
      measurement: { tg: null, cte: null, dielectric: null, dielectric_const: null },
      lis: null,
      tas: null,
      experimentDone: false,
      sourceId: yamlSample.id
    })
    state.value = 'designed'
  }

  function setSimulating(v: boolean) { simulating.value = v }

  // 전체 초기화: runId를 증가시켜 진행 중인 타이머 체인 무효화
  function reset() {
    runId++
    simulating.value = false
    state.value = 'idle'
    currentPhase.value = { deviceIndex: 0, phase: 'running' }
    rows.value = []
  }

  return {
    state, currentPhase, rows, currentRunId, simulating,
    getRunId, incrementRunId, setSimulating,
    design, startExperiment, setPhase, completeExperiment, addAutoTuneRow, reset
  }
})
