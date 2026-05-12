<template>
  <q-layout view="hHh lpR fFf">
    <!-- 상단 헤더: 앱 제목 + RESET 버튼 -->
    <q-header>
      <q-toolbar style="min-height: 52px">
        <q-icon name="science" size="22px" color="indigo-4" class="q-mr-sm" />
        <q-toolbar-title style="font-size: 15px; font-weight: 600; letter-spacing: 0.03em; color: #e2e8f0">
          WS LAB PILOT — DEMO DAY
        </q-toolbar-title>
        <q-btn
          flat dense
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

        <!-- 로딩 중 -->
        <template v-if="configStore.loading">
          <div class="row justify-center items-center" style="height: 60vh">
            <q-spinner color="indigo-4" size="3em" />
            <span class="q-ml-md text-h6" style="color:#94a3b8">설정 로딩 중...</span>
          </div>
        </template>

        <!-- 로드 실패 -->
        <template v-else-if="configStore.error">
          <q-banner class="bg-red-10 text-white rounded-borders">
            설정 로드 실패: {{ configStore.error }}
          </q-banner>
        </template>

        <!-- 정상: 3개 패널 세로 배치 -->
        <template v-else>
          <!-- 패널 1: 장치 연결 현황 -->
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

          <!-- 패널 2: 조성 실험 테이블 + 실험 설계/시작 버튼 -->
          <q-card flat class="q-mb-md" style="border-radius: 12px">
            <q-card-section>
              <div class="row items-center q-mb-md">
                <span style="font-size: 13px; font-weight: 600; color: #94a3b8; letter-spacing: 0.06em; text-transform: uppercase">
                  Glass Composition Samples
                </span>
                <q-space />
                <!-- 실험 설계: idle 상태에서만 활성화 -->
                <q-btn
                  unelevated size="sm"
                  label="실험 설계"
                  color="indigo"
                  :disable="experimentStore.state !== 'idle'"
                  style="border-radius: 6px; margin-right: 8px"
                  @click="showModal = true"
                />
                <!-- 실험 시작: designed 상태(설계 완료 후)에서만 활성화 -->
                <q-btn
                  unelevated size="sm"
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

          <!-- 패널 3: LIS/TAS 누적 추세 그래프 -->
          <q-card flat style="border-radius: 12px">
            <q-card-section>
              <ScoreTrend />
            </q-card-section>
          </q-card>
        </template>
      </q-page>
    </q-page-container>

    <!-- 실험 설계 모달 (v-model로 열기/닫기 제어) -->
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

// 실험 + 트렌드 데이터를 모두 초기화 (장치 재점등은 experiment watch가 자동 처리)
function handleReset() {
  experimentStore.reset()
  trendStore.reset()
}

// 앱 마운트 시 백엔드에서 YAML 설정 로드
onMounted(() => {
  configStore.fetchConfig()
})
</script>
