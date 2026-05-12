<template>
  <q-layout view="hHh lpR fFf">
    <q-header>
      <q-toolbar style="min-height: 52px">
        <q-icon name="science" size="22px" color="indigo-4" class="q-mr-sm" />
        <q-toolbar-title style="font-size: 15px; font-weight: 600; letter-spacing: 0.03em; color: #e2e8f0">
          WS LAB PILOT — DEMO DAY
        </q-toolbar-title>
        <q-btn
          flat
          dense
          label="RESET"
          icon="refresh"
          color="red-4"
          style="font-size: 12px; border: 1px solid rgba(239,68,68,0.4); border-radius: 6px; padding: 4px 12px"
          @click="handleReset"
        />
      </q-toolbar>
    </q-header>

    <q-page-container>
      <q-page class="q-pa-md" style="background: #0f172b">
        <template v-if="configStore.loading">
          <div class="row justify-center items-center" style="height: 60vh">
            <q-spinner color="indigo-4" size="3em" />
            <span class="q-ml-md text-h6" style="color:#94a3b8">설정 로딩 중...</span>
          </div>
        </template>

        <template v-else-if="configStore.error">
          <q-banner class="bg-red-10 text-white rounded-borders">
            설정 로드 실패: {{ configStore.error }}
          </q-banner>
        </template>

        <template v-else>
          <!-- Row 1: Connected Devices -->
          <q-card flat class="q-mb-md" style="border-radius: 12px">
            <q-card-section class="q-pb-sm">
              <div class="row items-center q-mb-sm">
                <span class="led green q-mr-xs" />
                <span style="font-size: 13px; font-weight: 600; color: #94a3b8; letter-spacing: 0.06em; text-transform: uppercase">
                  Connected Devices
                </span>
              </div>
              <DevicePanel />
            </q-card-section>
          </q-card>

          <!-- Row 2: Glass Composition -->
          <q-card flat class="q-mb-md" style="border-radius: 12px">
            <q-card-section>
              <div class="row items-center q-mb-md">
                <span style="font-size: 13px; font-weight: 600; color: #94a3b8; letter-spacing: 0.06em; text-transform: uppercase">
                  Glass Composition Samples
                </span>
                <q-space />
                <q-btn
                  unelevated
                  size="sm"
                  label="실험 설계"
                  color="indigo"
                  :disable="experimentStore.state !== 'idle'"
                  style="border-radius: 6px; margin-right: 8px"
                  @click="showModal = true"
                />
                <q-btn
                  unelevated
                  size="sm"
                  label="실험 시작"
                  color="positive"
                  :disable="experimentStore.state !== 'designed'"
                  style="border-radius: 6px"
                  @click="experimentStore.startExperiment()"
                />
              </div>
              <CompositionTable />
            </q-card-section>
          </q-card>

          <!-- Row 3: Score Trend -->
          <q-card flat style="border-radius: 12px">
            <q-card-section>
              <ScoreTrend />
            </q-card-section>
          </q-card>
        </template>
      </q-page>
    </q-page-container>

    <ExperimentDesignModal v-model="showModal" />
  </q-layout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useConfigStore } from 'src/stores/config'
import { useExperimentStore } from 'src/stores/experiment'
import { useTrendStore } from 'src/stores/trend'
import DevicePanel from 'src/components/DevicePanel.vue'
import CompositionTable from 'src/components/CompositionTable.vue'
import ScoreTrend from 'src/components/ScoreTrend.vue'
import ExperimentDesignModal from 'src/components/ExperimentDesignModal.vue'

const configStore = useConfigStore()
const experimentStore = useExperimentStore()
const trendStore = useTrendStore()
const showModal = ref(false)

function handleReset() {
  experimentStore.reset()
  trendStore.reset()
}

onMounted(() => {
  configStore.fetchConfig()
})
</script>
