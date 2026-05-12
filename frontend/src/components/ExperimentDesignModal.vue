<template>
  <q-dialog v-model="open" persistent>
    <q-card style="min-width: 440px; background: #1d293d; border: 1px solid #314158">
      <q-card-section class="row items-center q-pb-sm">
        <div class="text-h6" style="color: #e2e8f0">실험 설계</div>
        <q-space />
        <q-btn icon="close" flat round dense color="grey-5" @click="cancel" />
      </q-card-section>

      <q-separator color="blue-grey-8" />

      <q-card-section class="q-pt-md">
        <!-- ID + 조성 -->
        <div class="row q-gutter-sm q-mb-sm">
          <q-input
            v-model="form.sampleId"
            label="ID (샘플명)"
            outlined dense dark
            class="col"
            label-color="blue-grey-4"
            hint="테이블 ID 열에 표시됩니다"
          />
        </div>
        <q-input
          v-model="form.composition"
          label="조성 (예: SiO2:70, Al2O3:18, B2O3:12)"
          outlined dense dark
          class="q-mb-md"
          label-color="blue-grey-4"
          hint="조성 값을 직접 입력하세요"
        />

        <!-- 공통 목표치 -->
        <q-separator color="blue-grey-8" class="q-mb-sm" />
        <div class="text-caption q-mb-sm" style="color: #64748b; text-transform: uppercase; letter-spacing: 0.06em">
          공통 목표치
        </div>
        <div class="row q-gutter-sm q-mb-sm">
          <q-input
            v-model.number="form.targetTg"
            type="number"
            label="Tg (°C)"
            outlined dense dark
            class="col"
            label-color="blue-grey-4"
          />
          <q-input
            v-model.number="form.targetCte"
            type="number"
            label="CTE (×10⁻⁶/K)"
            outlined dense dark
            class="col"
            label-color="blue-grey-4"
          />
        </div>
        <div class="row q-gutter-sm q-mb-md">
          <q-input
            v-model.number="form.targetDielectric"
            type="number"
            label="유전율"
            outlined dense dark
            class="col"
            label-color="blue-grey-4"
          />
          <q-input
            v-model.number="form.targetDielectricConst"
            type="number"
            label="유전상수"
            outlined dense dark
            class="col"
            label-color="blue-grey-4"
          />
        </div>

        <!-- YAML 샘플 예측값 미리보기 -->
        <div v-if="linkedSample">
          <div class="text-caption q-mb-xs" style="color: #64748b; text-transform: uppercase; letter-spacing: 0.06em">
            예측값 · 측정값 (YAML 자동 로드 — {{ linkedSample.id }})
          </div>
          <div class="row q-gutter-sm">
            <div v-for="item in previewItems" :key="item.label" class="preview-chip">
              <span class="preview-label">{{ item.label }}</span>
              <span class="preview-val">{{ item.predicted }}</span>
              <span class="preview-sep">→</span>
              <span class="preview-meas">{{ item.measured }}</span>
            </div>
          </div>
        </div>
      </q-card-section>

      <q-card-actions align="right" class="q-px-md q-pb-md">
        <q-btn flat label="취소" color="grey-5" @click="cancel" />
        <q-btn unelevated label="확인" color="indigo" :disable="!isValid" @click="confirm" style="border-radius: 6px" />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useExperimentStore } from 'src/stores/experiment'
import { useConfigStore } from 'src/stores/config'

const props = defineProps<{ modelValue: boolean }>()
const emit  = defineEmits<{ (e: 'update:modelValue', v: boolean): void }>()

const open = computed({
  get: () => props.modelValue,
  set: v  => emit('update:modelValue', v),
})

const experimentStore = useExperimentStore()
const configStore     = useConfigStore()

const form = ref({
  sampleId: '',
  composition: '',
  targetTg: 0,
  targetCte: 0,
  targetDielectric: 0,
  targetDielectricConst: 0,
})

// Initialize target fields from current global_target when modal opens
watch(open, v => {
  if (v) {
    const gt = configStore.config?.global_target
    if (gt) {
      form.value.targetTg             = gt.tg
      form.value.targetCte            = gt.cte
      form.value.targetDielectric     = gt.dielectric
      form.value.targetDielectricConst = gt.dielectric_const
    }
  }
})

const linkedSample = computed(() => {
  const samples  = configStore.config?.samples ?? []
  const rowCount = experimentStore.rows.length
  return samples[rowCount % samples.length] ?? null
})

const previewItems = computed(() => {
  const s = linkedSample.value
  if (!s) return []
  return [
    { label: 'Tg',      predicted: s.predicted.tg,              measured: s.measurement.tg },
    { label: 'CTE',     predicted: s.predicted.cte,             measured: s.measurement.cte },
    { label: '유전율',  predicted: s.predicted.dielectric,      measured: s.measurement.dielectric },
    { label: '유전상수', predicted: s.predicted.dielectric_const, measured: s.measurement.dielectric_const },
  ]
})

const isValid = computed(
  () => form.value.sampleId.trim().length > 0 && form.value.composition.trim().length > 0
)

function confirm() {
  if (!isValid.value) return

  // Update global target
  configStore.updateGlobalTarget({
    tg:               form.value.targetTg,
    cte:              form.value.targetCte,
    dielectric:       form.value.targetDielectric,
    dielectric_const: form.value.targetDielectricConst,
  })

  const sample = linkedSample.value
  experimentStore.design({
    id:          form.value.sampleId.trim(),
    composition: form.value.composition.trim(),
    predicted: sample
      ? { tg: sample.predicted.tg, cte: sample.predicted.cte, dielectric: sample.predicted.dielectric, dielectric_const: sample.predicted.dielectric_const }
      : { tg: 0, cte: 0, dielectric: 0, dielectric_const: 0 },
    sourceId: sample?.id ?? null,
  })

  form.value = { sampleId: '', composition: '', targetTg: 0, targetCte: 0, targetDielectric: 0, targetDielectricConst: 0 }
  open.value = false
}

function cancel() { open.value = false }
</script>

<style scoped>
.preview-chip {
  display: flex;
  align-items: center;
  gap: 4px;
  background: rgba(97,95,255,0.08);
  border: 1px solid rgba(97,95,255,0.2);
  border-radius: 6px;
  padding: 4px 10px;
  font-size: 11px;
}
.preview-label { color: #64748b; font-weight: 600; min-width: 40px; }
.preview-val   { color: #94a3b8; }
.preview-sep   { color: #4b5563; }
.preview-meas  { color: #22c55e; font-weight: 600; }
</style>
