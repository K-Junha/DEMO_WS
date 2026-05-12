import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Sample } from './config'

export type ExperimentState = 'idle' | 'designed' | 'running' | 'done'

export interface ExperimentPhase {
  deviceIndex: number
  phase: 'running' | 'complete'
}

export interface SampleRow {
  id: string
  composition: string
  predicted: { tg: number; cte: number; dielectric: number; dielectric_const: number }
  measurement: { tg: number | null; cte: number | null; dielectric: number | null; dielectric_const: number | null }
  lis: number | null
  tas: number | null
  experimentDone: boolean
  sourceId: string | null
}

export const useExperimentStore = defineStore('experiment', () => {
  const state = ref<ExperimentState>('idle')
  const currentPhase = ref<ExperimentPhase>({ deviceIndex: 0, phase: 'running' })
  const rows = ref<SampleRow[]>([])
  let runId = 0

  const currentRunId = computed(() => runId)

  function getRunId() {
    return runId
  }

  function incrementRunId() {
    runId++
    return runId
  }

  function design(row: Omit<SampleRow, 'measurement' | 'lis' | 'tas' | 'experimentDone'>) {
    rows.value.push({
      ...row,
      measurement: { tg: null, cte: null, dielectric: null, dielectric_const: null },
      lis: null,
      tas: null,
      experimentDone: false
    })
    state.value = 'designed'
  }

  function startExperiment() {
    if (state.value !== 'designed') return
    state.value = 'running'
    currentPhase.value = { deviceIndex: 0, phase: 'running' }
  }

  function setPhase(deviceIndex: number, phase: 'running' | 'complete') {
    currentPhase.value = { deviceIndex, phase }
  }

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

  function addAutoTuneRow(yamlSample: Sample) {
    const nextRow: SampleRow = {
      id: yamlSample.id,
      composition: yamlSample.composition,
      predicted: { ...yamlSample.predicted },
      measurement: { tg: null, cte: null, dielectric: null, dielectric_const: null },
      lis: null,
      tas: null,
      experimentDone: false,
      sourceId: yamlSample.id
    }
    rows.value.push(nextRow)
    state.value = 'designed'
  }

  function reset() {
    runId++
    state.value = 'idle'
    currentPhase.value = { deviceIndex: 0, phase: 'running' }
    rows.value = []
  }

  return {
    state,
    currentPhase,
    rows,
    currentRunId,
    getRunId,
    incrementRunId,
    design,
    startExperiment,
    setPhase,
    completeExperiment,
    addAutoTuneRow,
    reset
  }
})
