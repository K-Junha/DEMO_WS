<template>
  <q-dialog v-model="open" persistent>
    <q-card style="min-width: 460px; background: #1d293d; border: 1px solid #314158">
      <q-card-section class="row items-center q-pb-sm">
        <div class="text-h6" style="color: #e2e8f0">실험 설계</div>
        <q-space />
        <q-btn icon="close" flat round dense color="grey-5" @click="cancel" />
      </q-card-section>

      <q-separator color="blue-grey-8" />

      <q-card-section class="q-pt-md">
        <!-- 조성 입력 (산화물 드롭다운 + wt%) -->
        <q-separator color="blue-grey-8" class="q-mb-sm" />
        <div class="text-caption q-mb-sm" style="color: #64748b; text-transform: uppercase; letter-spacing: 0.06em">
          조성 (wt%)
        </div>

        <div v-for="(row, i) in form.oxides" :key="i" class="row items-center q-gutter-sm q-mb-xs">
          <q-select
            v-model="row.oxide"
            :options="availableOxides(i)"
            outlined dense dark
            style="width: 120px"
            label-color="blue-grey-4"
            popup-content-style="background: #1d293d; color: #e2e8f0"
          />
          <q-input
            v-model.number="row.wt"
            type="number"
            min="0" max="100"
            outlined dense dark
            style="width: 100px"
            label-color="blue-grey-4"
            suffix="wt%"
          />
          <q-btn
            flat round dense icon="close" color="grey-5" size="sm"
            :disable="form.oxides.length <= 1"
            @click="removeOxide(i)"
          />
        </div>

        <!-- 산화물 추가 + 합계 -->
        <div class="row items-center q-mt-sm q-mb-md" style="gap: 12px">
          <q-btn
            flat dense icon="add" label="산화물 추가" color="indigo-4" size="sm"
            :disable="form.oxides.length >= OXIDES.length"
            @click="addOxide"
          />
          <q-space />
          <span style="font-size: 12px; color: #64748b">합계:</span>
          <span :style="{ color: sumOk ? '#10b981' : '#ef4444', fontWeight: 700, fontSize: '13px' }">
            {{ oxideSum.toFixed(1) }} %
          </span>
          <q-icon :name="sumOk ? 'check_circle' : 'error'" :color="sumOk ? 'positive' : 'negative'" size="16px" />
        </div>

        <!-- AI 조성 예측 버튼 -->
        <q-separator color="blue-grey-8" class="q-mb-sm" />
        <div class="text-caption q-mb-sm" style="color: #64748b; text-transform: uppercase; letter-spacing: 0.06em">
          AI 예측
        </div>

        <div class="row items-center q-mb-md" style="gap: 12px">
          <q-btn
            unelevated icon="auto_fix_high" label="조성 예측"
            color="indigo-8" size="sm"
            style="border-radius: 6px; min-width: 100px"
            :disable="!sumOk || predicting"
            :loading="predicting"
            @click="runPrediction"
          />

          <!-- 예측 완료 후 결과 표시 -->
          <div v-if="hasPredicted" class="row q-gutter-xs">
            <div class="pred-chip">
              <span class="pred-label">Tg</span>
              <span class="pred-val">{{ predictedVals.tg }}°C</span>
            </div>
            <div class="pred-chip">
              <span class="pred-label">CTE</span>
              <span class="pred-val">{{ predictedVals.cte }}</span>
            </div>
            <div class="pred-chip">
              <span class="pred-label">유전율</span>
              <span class="pred-val">{{ predictedVals.dielectric }}</span>
            </div>
            <div class="pred-chip">
              <span class="pred-label">유전상수</span>
              <span class="pred-val">{{ predictedVals.dielectric_const }}</span>
            </div>
          </div>
          <span v-else-if="sumOk" style="font-size: 11px; color: #4b5563">
            ← 조성 예측 후 확인 가능
          </span>
        </div>

        <!-- 공통 목표치 -->
        <q-separator color="blue-grey-8" class="q-mb-sm" />
        <div class="text-caption q-mb-sm" style="color: #64748b; text-transform: uppercase; letter-spacing: 0.06em">
          공통 목표치
        </div>
        <div class="row q-gutter-sm q-mb-sm">
          <q-input v-model.number="form.targetTg"              type="number" label="Tg (°C)"        outlined dense dark class="col" label-color="blue-grey-4" />
          <q-input v-model.number="form.targetCte"             type="number" label="CTE (×10⁻⁶/K)" outlined dense dark class="col" label-color="blue-grey-4" />
        </div>
        <div class="row q-gutter-sm q-mb-md">
          <q-input v-model.number="form.targetDielectric"      type="number" label="유전율"         outlined dense dark class="col" label-color="blue-grey-4" />
          <q-input v-model.number="form.targetDielectricConst" type="number" label="유전상수"       outlined dense dark class="col" label-color="blue-grey-4" />
        </div>
      </q-card-section>

      <q-card-actions align="right" class="q-px-md q-pb-md">
        <q-btn flat label="취소" color="grey-5" @click="cancel" />
        <q-btn
          unelevated label="확인" color="indigo"
          :disable="!isValid"
          style="border-radius: 6px"
          @click="confirm"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useExperimentStore } from 'src/stores/experiment'
import { useConfigStore } from 'src/stores/config'

const OXIDES = ['SiO2', 'Al2O3', 'B2O3']

interface OxideRow { oxide: string; wt: number }

const props = defineProps<{ modelValue: boolean }>()
const emit  = defineEmits<{ (e: 'update:modelValue', v: boolean): void }>()

const open = computed({
  get: () => props.modelValue,
  set: v  => emit('update:modelValue', v),
})

const experimentStore = useExperimentStore()
const configStore     = useConfigStore()

const defaultForm = () => ({
  oxides: [{ oxide: 'SiO2', wt: 0 }] as OxideRow[],
  targetTg: 0,
  targetCte: 0,
  targetDielectric: 0,
  targetDielectricConst: 0,
})

const form = ref(defaultForm())

// AI 예측 상태
const predicting    = ref(false)
const hasPredicted  = ref(false)
const predictedVals = ref({ tg: 0, cte: 0, dielectric: 0, dielectric_const: 0 })

// 조성이 바뀌면 예측을 초기화 (다시 예측 필요)
watch(() => form.value.oxides, () => { hasPredicted.value = false }, { deep: true })

// 모달 열릴 때 목표치 초기화, 예측 상태 리셋
watch(open, v => {
  if (v) {
    hasPredicted.value = false
    const gt = configStore.config?.global_target
    if (gt) {
      form.value.targetTg              = gt.tg
      form.value.targetCte             = gt.cte
      form.value.targetDielectric      = gt.dielectric
      form.value.targetDielectricConst = gt.dielectric_const
    }
  }
})

function availableOxides(rowIdx: number): string[] {
  const selected = form.value.oxides.filter((_, i) => i !== rowIdx).map(r => r.oxide)
  return OXIDES.filter(o => !selected.includes(o))
}

function addOxide() {
  const used = form.value.oxides.map(r => r.oxide)
  const next = OXIDES.find(o => !used.includes(o))
  if (next) form.value.oxides.push({ oxide: next, wt: 0 })
}

function removeOxide(i: number) { form.value.oxides.splice(i, 1) }

const oxideSum = computed(() => form.value.oxides.reduce((acc, r) => acc + (r.wt ?? 0), 0))
const sumOk    = computed(() => Math.abs(oxideSum.value - 100) < 0.1)

const compositionStr = computed(() =>
  form.value.oxides.filter(r => (r.wt ?? 0) > 0).map(r => `${r.oxide}:${r.wt}`).join(', ')
)

// YAML 회차 연결 (sourceId용 — 어떤 측정값을 사용할지 결정)
const linkedSample = computed(() => {
  const samples = configStore.config?.samples ?? []
  return samples[experimentStore.rows.length % samples.length] ?? null
})

// 예측 버튼: 1초 로딩 후 목표치 ±2.5% 범위 내 값 생성
// "AI 모델은 항상 목표에 근접한 조성을 추천한다"는 시나리오를 표현
function runPrediction() {
  predicting.value = true
  setTimeout(() => {
    const gt = configStore.config?.global_target
    if (gt) {
      const noise = (v: number) => v * (1 + (Math.random() * 2 - 1) * 0.025)
      predictedVals.value = {
        tg:               Math.round(noise(gt.tg)),
        cte:              Math.round(noise(gt.cte) * 10) / 10,
        dielectric:       Math.round(noise(gt.dielectric) * 10) / 10,
        dielectric_const: Math.round(noise(gt.dielectric_const) * 100) / 100,
      }
    }
    predicting.value   = false
    hasPredicted.value = true
  }, 1000)
}

// 조성 합계 100% + 예측 완료 시에만 확인 버튼 활성화
const isValid = computed(() => sumOk.value && hasPredicted.value)

function confirm() {
  if (!isValid.value) return

  configStore.updateGlobalTarget({
    tg:               form.value.targetTg,
    cte:              form.value.targetCte,
    dielectric:       form.value.targetDielectric,
    dielectric_const: form.value.targetDielectricConst,
  })

  experimentStore.design({
    composition: compositionStr.value,
    predicted:   { ...predictedVals.value },  // AI 예측값 (목표치 근처)
    sourceId:    linkedSample.value?.id ?? null,
  })

  form.value = defaultForm()
  hasPredicted.value = false
  open.value = false
}

function cancel() {
  form.value = defaultForm()
  hasPredicted.value = false
  open.value = false
}
</script>

<style scoped>
.pred-chip {
  display: flex;
  align-items: center;
  gap: 4px;
  background: rgba(16,185,129,0.08);
  border: 1px solid rgba(16,185,129,0.25);
  border-radius: 6px;
  padding: 3px 8px;
  font-size: 11px;
}
.pred-label { color: #64748b; font-weight: 600; margin-right: 2px; }
.pred-val   { color: #10b981; font-weight: 700; }
</style>
