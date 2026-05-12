import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useTrendStore = defineStore('trend', () => {
  const lisHistory = ref<number[]>([])
  const tasHistory = ref<number[]>([])

  const lisCumulative = computed(() => {
    let sum = 0
    return lisHistory.value.map(v => (sum += v))
  })

  const tasCumulative = computed(() => {
    let sum = 0
    return tasHistory.value.map(v => (sum += v))
  })

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
