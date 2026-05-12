// Score Trend 스토어: 실험 회차별 LIS·TAS 이력 관리
// ScoreTrend.vue의 꺾은선 그래프가 이 데이터를 사용함

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useTrendStore = defineStore('trend', () => {
  // 실험 완료될 때마다 push되는 회차별 원본 점수
  const lisHistory = ref<number[]>([])
  const tasHistory = ref<number[]>([])

  // 누적합: 그래프에서 "전체 진행 방향"을 보여주기 위해 회차별로 합산
  const lisCumulative = computed(() => {
    let sum = 0
    return lisHistory.value.map(v => (sum += v))
  })

  const tasCumulative = computed(() => {
    let sum = 0
    return tasHistory.value.map(v => (sum += v))
  })

  // 실험 1회 완료 시 ExperimentBanner에서 호출
  function addEntry(lis: number, tas: number) {
    lisHistory.value.push(lis)
    tasHistory.value.push(tas)
  }

  function reset() {
    lisHistory.value = []
    tasHistory.value = []
  }

  return { lisHistory, tasHistory, lisCumulative, tasCumulative, addEntry, reset }
})
