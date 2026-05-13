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
        <!-- 샘플 ID -->
        <q-input
          v-model="form.sampleId"
          label="ID (샘플명)"
          outlined dense dark
          class="q-mb-md"
          label-color="blue-grey-4"
          hint="테이블 ID 열에 표시됩니다"
        />

        <!-- 조성 입력 (산화물 드롭다운 + wt%) -->
        <q-separator color="blue-grey-8" class="q-mb-sm" />
        <div class="text-caption q-mb-sm" style="color: #64748b; text-transform: uppercase; letter-spacing: 0.06em">
          조성 (wt%)
        </div>

        <div v-for="(row, i) in form.oxides" :key="i" class="row items-center q-gutter-sm q-mb-xs">
          <!-- 산화물 선택 드롭다운 (이미 선택된 것 제외) -->
          <q-select
            v-model="row.oxide"
            :options="availableOxides(i)"
            outlined dense dark
            style="width: 120px"
            label-color="blue-grey-4"
            popup-content-style="background: #1d293d; color: #e2e8f0"
          />
          <!-- wt% 입력 -->
          <q-input
            v-model.number="row.wt"
            type="number"
            min="0" max="100"
            outlined dense dark
            style="width: 100px"
            label-color="blue-grey-4"
            suffix="wt%"
          />
          <!-- 행 삭제 -->
          <q-btn
            flat round dense
            icon="close"
            color="grey-5"
            size="sm"
            :disable="form.oxides.length <= 1"
            @click="removeOxide(i)"
          />
        </div>

        <!-- 산화물 추가 버튼 + 합계 표시 -->
        <div class="row items-center q-mt-sm q-mb-md" style="gap: 12px">
          <q-btn
            flat dense
            icon="add"
            label="산화물 추가"
            color="indigo-4"
            size="sm"
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

        <!-- 공통 목표치 -->
        <q-separator color="blue-grey-8" class="q-mb-sm" />
        <div class="text-caption q-mb-sm" style="color: #64748b; text-transform: uppercase; letter-spacing: 0.06em">
          공통 목표치
        </div>
        <div class="row q-gutter-sm q-mb-sm">
          <q-input v-model.number="form.targetTg"             type="number" label="Tg (°C)"      outlined dense dark class="col" label-color="blue-grey-4" />
          <q-input v-model.number="form.targetCte"            type="number" label="CTE (×10⁻⁶/K)" outlined dense dark class="col" label-color="blue-grey-4" />
        </div>
        <div class="row q-gutter-sm q-mb-md">
          <q-input v-model.number="form.targetDielectric"     type="number" label="유전율"       outlined dense dark class="col" label-color="blue-grey-4" />
          <q-input v-model.number="form.targetDielectricConst" type="number" label="유전상수"    outlined dense dark class="col" label-color="blue-grey-4" />
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

// 데모에서 사용할 산화물 3종
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
  sampleId: '',
  oxides: [{ oxide: 'SiO2', wt: 0 }] as OxideRow[],
  targetTg: 0,
  targetCte: 0,
  targetDielectric: 0,
  targetDielectricConst: 0,
})

const form = ref(defaultForm())

// 모달이 열릴 때 공통 목표치를 현재 YAML 값으로 초기화
watch(open, v => {
  if (v) {
    const gt = configStore.config?.global_target
    if (gt) {
      form.value.targetTg              = gt.tg
      form.value.targetCte             = gt.cte
      form.value.targetDielectric      = gt.dielectric
      form.value.targetDielectricConst = gt.dielectric_const
    }
  }
})

// 이미 선택된 산화물을 제외한 드롭다운 옵션 반환
function availableOxides(rowIdx: number): string[] {
  const selected = form.value.oxides
    .filter((_, i) => i !== rowIdx)
    .map(r => r.oxide)
  return OXIDES.filter(o => !selected.includes(o))
}

// 새 행 추가: 아직 선택 안 된 첫 번째 산화물로 초기화
function addOxide() {
  const used = form.value.oxides.map(r => r.oxide)
  const next = OXIDES.find(o => !used.includes(o))
  if (next) form.value.oxides.push({ oxide: next, wt: 0 })
}

function removeOxide(i: number) {
  form.value.oxides.splice(i, 1)
}

// wt% 합계 계산
const oxideSum = computed(() =>
  form.value.oxides.reduce((acc, r) => acc + (r.wt ?? 0), 0)
)

// 합계가 100%인지 확인 (부동소수점 오차 허용)
const sumOk = computed(() => Math.abs(oxideSum.value - 100) < 0.1)

// "SiO2:70, Al2O3:18, B2O3:12" 형태 문자열 자동 생성
const compositionStr = computed(() =>
  form.value.oxides
    .filter(r => (r.wt ?? 0) > 0)
    .map(r => `${r.oxide}:${r.wt}`)
    .join(', ')
)

// YAML에서 자동 연결되는 샘플 (실험 회차 순서로 순환)
const linkedSample = computed(() => {
  const samples  = configStore.config?.samples ?? []
  const rowCount = experimentStore.rows.length
  return samples[rowCount % samples.length] ?? null
})

const previewItems = computed(() => {
  const s = linkedSample.value
  if (!s) return []
  return [
    { label: 'Tg',      predicted: s.predicted.tg,               measured: s.measurement.tg },
    { label: 'CTE',     predicted: s.predicted.cte,              measured: s.measurement.cte },
    { label: '유전율',  predicted: s.predicted.dielectric,       measured: s.measurement.dielectric },
    { label: '유전상수', predicted: s.predicted.dielectric_const, measured: s.measurement.dielectric_const },
  ]
})

// ID 입력 + wt% 합계 100% 모두 충족해야 확인 버튼 활성화
const isValid = computed(
  () => form.value.sampleId.trim().length > 0 && sumOk.value
)

function confirm() {
  if (!isValid.value) return

  // 공통 목표치 업데이트
  configStore.updateGlobalTarget({
    tg:               form.value.targetTg,
    cte:              form.value.targetCte,
    dielectric:       form.value.targetDielectric,
    dielectric_const: form.value.targetDielectricConst,
  })

  const sample = linkedSample.value
  experimentStore.design({
    id:          form.value.sampleId.trim(),
    composition: compositionStr.value,
    predicted: sample
      ? { tg: sample.predicted.tg, cte: sample.predicted.cte, dielectric: sample.predicted.dielectric, dielectric_const: sample.predicted.dielectric_const }
      : { tg: 0, cte: 0, dielectric: 0, dielectric_const: 0 },
    sourceId: sample?.id ?? null,
  })

  form.value = defaultForm()
  open.value = false
}

function cancel() {
  form.value = defaultForm()
  open.value = false
}
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
