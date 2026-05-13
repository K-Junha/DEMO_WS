<template>
  <div class="device-card q-pa-sm" :class="active ? 'active' : 'inactive'" style="min-width: 158px; max-width: 183px">
    <!-- Header: LED + name [space] icon -->
    <div class="row items-center q-mb-xs" style="gap: 5px">
      <span class="led" :class="active ? (device.connected ? 'green' : 'red') : 'gray'" />
      <span style="font-size: 12px; font-weight: 700; color: #e2e8f0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; flex: 1">
        {{ device.name }}
      </span>
      <q-icon :name="deviceIcon" size="30px" :style="{ color: active ? '#615fff' : '#4b5563' }" />
    </div>

    <!-- Model -->
    <div style="font-size: 10px; color: #64748b; margin-bottom: 3px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis">
      {{ device.model }}
    </div>

    <!-- IP:Port -->
    <div style="font-size: 10px; color: #94a3b8; font-family: monospace; margin-bottom: 5px">
      {{ device.ip }}:{{ device.port }}
    </div>

    <!-- Protocol badge -->
    <span :class="protocolClass" style="font-size: 10px; border-radius: 4px; padding: 2px 7px; font-weight: 600; display: inline-block; margin-bottom: 5px">
      {{ device.protocol }}
    </span>

    <!-- Measures -->
    <div v-if="device.measures?.length" style="font-size: 10px; color: #10b981; margin-bottom: 3px">
      ↳ {{ device.measures.join(' · ') }}
    </div>

    <!-- Data block: always visible when active -->
    <div v-if="active" class="exp-data-block">
      <!-- 해당 장치 실험 진행 중: shimmer 스켈레톤 표시 -->
      <template v-if="loading">
        <div class="skel-line" />
        <div class="skel-line skel-short" />
        <div class="skel-line" />
      </template>
      <template v-else-if="device.id === 'scale'">
        <div class="exp-row"><span class="exp-label">세팅</span><span class="exp-val">{{ expData?.scale?.target_weight ?? '—' }}{{ expData?.scale ? 'g' : '' }}</span></div>
        <div class="exp-row"><span class="exp-label">현재</span><span class="exp-val">{{ expData?.scale?.current_weight ?? '—' }}{{ expData?.scale ? 'g' : '' }}</span></div>
      </template>
      <template v-else-if="device.id === 'mixer'">
        <div class="exp-row"><span class="exp-label">가동</span><span class="exp-val">{{ expData?.mixer?.operation_time ?? '—' }}</span></div>
      </template>
      <template v-else-if="device.id === 'furnace'">
        <template v-if="expData?.furnace">
          <div v-for="s in expData.furnace.steps" :key="s.step" class="exp-col" style="margin-bottom:3px">
            <span class="exp-label">Step {{ s.step }}</span>
            <div class="exp-row"><span class="exp-label">승온</span><span class="exp-val">{{ s.heating_rate }}°/min</span></div>
            <div class="exp-row"><span class="exp-label">목표</span><span class="exp-val">{{ s.target_temp }}°C</span></div>
            <div class="exp-row"><span class="exp-label">유지</span><span class="exp-val">{{ s.hold_time }}</span></div>
          </div>
        </template>
        <div v-else class="exp-row"><span class="exp-label">승온</span><span class="exp-val">—</span></div>
      </template>
      <template v-else-if="device.id === 'anneal'">
        <div class="exp-row"><span class="exp-label">목표</span><span class="exp-val">{{ expData?.annealing ? expData.annealing.target_temp + '°C' : '—' }}</span></div>
        <div class="exp-row"><span class="exp-label">시간</span><span class="exp-val">{{ expData?.annealing?.time ?? '—' }}</span></div>
      </template>
      <template v-else-if="device.id === 'press'">
        <div class="exp-row"><span class="exp-label">압력</span><span class="exp-val">{{ expData?.press ? expData.press.pressure + ' MPa' : '—' }}</span></div>
      </template>
      <template v-else-if="device.id === 'dta' || device.id === 'dsc'">
        <div class="exp-row"><span class="exp-label">Tg</span><span class="exp-val">{{ measurement ? measurement.tg + ' °C' : '—' }}</span></div>
      </template>
      <template v-else-if="device.id === 'dilatometer'">
        <div class="exp-row"><span class="exp-label">CTE</span><span class="exp-val">{{ measurement ? measurement.cte + ' ppm' : '—' }}</span></div>
      </template>
      <template v-else-if="device.id === 'permittivity'">
        <div class="exp-row"><span class="exp-label">유전율</span><span class="exp-val">{{ measurement?.dielectric ?? '—' }}</span></div>
        <div class="exp-row"><span class="exp-label">유전상수</span><span class="exp-val">{{ measurement?.dielectric_const ?? '—' }}</span></div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { DeviceConfig, SampleExperiment, SampleMeasurement } from 'src/stores/config'

const ICON_MAP: Record<string, string> = {
  scale:        'balance',
  mixer:        'rotate_right',
  furnace:      'whatshot',
  anneal:       'thermostat',
  press:        'vertical_align_center',
  dta:          'show_chart',
  dsc:          'analytics',
  dilatometer:  'straighten',
  permittivity: 'bolt',
}

const PROTOCOL_CLASS: Record<string, string> = {
  'RS-232':   'badge-rs232',
  'RS-485':   'badge-rs485',
  'Ethernet': 'badge-ethernet',
  'USB':      'badge-usb',
}

const props = defineProps<{
  device: DeviceConfig
  active: boolean
  expData: SampleExperiment | null
  measurement: SampleMeasurement | null
  loading: boolean
}>()

const deviceIcon    = computed(() => ICON_MAP[props.device.id] ?? 'device_unknown')
const protocolClass = computed(() => PROTOCOL_CLASS[props.device.protocol] ?? 'badge-rs485')
</script>

<style scoped>
.exp-data-block {
  border-top: 1px solid rgba(49,65,88,0.8);
  padding-top: 5px;
  margin-top: 3px;
  display: flex;
  flex-direction: column;
  gap: 3px;
}
.exp-row { display: flex; justify-content: space-between; align-items: center; }
.exp-col { display: flex; flex-direction: column; gap: 1px; }
.exp-label { font-size: 10px; color: #64748b; }
.exp-val   { font-size: 11px; color: #e2e8f0; font-weight: 600; text-align: right; }

/* shimmer 로딩 스켈레톤 */
.skel-line {
  height: 8px;
  border-radius: 4px;
  background: linear-gradient(90deg,
    rgba(97,95,255,0.08) 25%,
    rgba(97,95,255,0.22) 50%,
    rgba(97,95,255,0.08) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.2s ease-in-out infinite;
}
.skel-short { width: 55%; }

@keyframes shimmer {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
