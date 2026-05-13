# Demo Day App — Implementation Plan

## Context
WS Lab Pilot 투자자 데모용 경량 웹앱. Streamlit → FastAPI + Vue 3 + Quasar v2로 완전 재작성.
새 폴더 `C:\JUNHA\11.code\project\demoday\`에서 시작. DB·인증 없음, YAML 더미 데이터만 사용.
HuggingFace Spaces Docker 배포 (port 7860).

## Architecture Decision
- **표 구현**: 커스텀 HTML table (Quasar q-table 미사용) — 멀티 헤더 행, 컬럼 그룹 색상 제어 필요
- **State machine**: useExperimentStore 단일 소스. runId로 RESET 레이스 컨디션 방지
- **애니메이션**: setTimeout chain (runId 게이팅), cleanup on unmount/RESET
- **Docker**: node:20-alpine → python:3.11-slim, uvicorn이 Vue dist 직접 서빙 (nginx 없음)

---

## Phase 1 — Project Scaffold

### Task 1-1: 프로젝트 폴더 초기화
**What:** `demoday/` 디렉토리 생성, pnpm + Quasar CLI로 frontend 초기화, FastAPI backend 스켈레톤
**Files:**
- `demoday/frontend/` — `pnpm create quasar` (Vue 3 + TS + Quasar v2)
- `demoday/backend/app/main.py` — FastAPI 스켈레톤
- `demoday/backend/pyproject.toml` — fastapi, uvicorn, pyyaml, pydantic-settings
- `demoday/config/demo_data.yaml` — 빈 구조 stub
- `demoday/.gitignore`

**Acceptance:**
- `cd frontend && pnpm dev` → Quasar 기본 페이지 포트 5173에서 실행
- `cd backend && uvicorn app.main:app --port 7860` → FastAPI 기동

---

### Task 1-2: Dockerfile + 빌드 검증
**What:** multi-stage Dockerfile 작성 및 로컬 빌드 검증
**Files:**
- `demoday/Dockerfile`
- `demoday/frontend/quasar.config.ts` — publicPath `/`, vueRouterMode `hash`

**Key:**
```dockerfile
FROM node:20-alpine AS build
WORKDIR /app/frontend
COPY frontend/ .
RUN npm install -g pnpm && pnpm install && pnpm build

FROM python:3.11-slim
WORKDIR /app
COPY backend/ ./backend/
COPY config/ ./config/
COPY --from=build /app/frontend/dist ./frontend/dist
RUN pip install -e ./backend
EXPOSE 7860
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
```
**Acceptance:**
- `docker build -t ws-demo .` 성공
- `docker run -p 7860:7860 ws-demo` → localhost:7860 접속 시 Vue 앱 반환

---

## Phase 2 — Data Layer

### Task 2-1: YAML 설정파일 작성
**What:** `config/demo_data.yaml` 전체 작성 (S-001~S-020 샘플, 장치 9개, global_target, timing)
**Files:**
- `demoday/config/demo_data.yaml`

**Structure:**
```yaml
timing: { device_activation_interval_ms, experiment_running_ms, experiment_complete_ms, experiment_gap_ms }
global_target: { tg, cte, dielectric, dielectric_const, weights: {tg, cte, dielectric, dielectric_const} }
auto_tune_enabled: true
random_range: { tg, cte, dielectric, dielectric_const }
devices: [ 9개 장치 ]
samples: [ S-001~S-020, 각 샘플: id, composition, predicted, measurement, next_composition, experiment{scale,mixer,furnace,annealing,press} ]
```
**Acceptance:** PyYAML `safe_load`로 파싱 오류 없음

---

### Task 2-2: /api/config 엔드포인트
**What:** YAML 읽어서 반환, mtime 기반 hot-reload, ETag 캐싱
**Files:**
- `demoday/backend/app/main.py` — StaticFiles mount, SPA fallback
- `demoday/backend/app/routers/config.py` — GET /api/config
- `demoday/backend/app/schemas.py` — Pydantic 응답 모델

**Key logic:**
```python
_cache: dict = {"data": None, "mtime": 0.0, "etag": ""}

async def get_config(request: Request):
    mtime = Path(CONFIG_PATH).stat().st_mtime
    if mtime != _cache["mtime"]:
        _cache["data"] = yaml.safe_load(Path(CONFIG_PATH).read_text())
        _cache["mtime"] = mtime
        _cache["etag"] = str(hash(mtime))
    if request.headers.get("if-none-match") == _cache["etag"]:
        return Response(status_code=304)
    return JSONResponse(_cache["data"], headers={"ETag": _cache["etag"]})
```
**Acceptance:**
- `GET /api/config` → 200 + 전체 YAML JSON 반환
- YAML 수정 후 재요청 → 새 데이터 반환 (재시작 없이)
- 동일 ETag 요청 → 304

---

### Task 2-3: Pinia 스토어 3개
**What:** useConfigStore, useExperimentStore, useTrendStore 정의
**Files:**
- `demoday/frontend/src/stores/config.ts`
- `demoday/frontend/src/stores/experiment.ts`
- `demoday/frontend/src/stores/trend.ts`

**State machine (useExperimentStore):**
```
idle → designed → running{deviceIndex:0..8, phase:'running'|'complete'} → done
```
runId: `let runId = 0` — 모든 setTimeout 콜백에서 `if (id !== runId) return` 게이팅

**useTrendStore:** `lisHistory: number[]`, `tasHistory: number[]` (누적합 배열)

**Acceptance:**
- `useExperimentStore().state` 초기값 `'idle'`
- RESET 호출 시 모든 store 초기화 + runId 증가

---

## Phase 3 — Core UI: CompositionTable

### Task 3-1: CompositionTable + LIS/TAS 계산
**What:** 컬럼 그룹 색상 테이블, 오차/LIS/TAS 자동계산, 버튼 상태 연동
**Files:**
- `demoday/frontend/src/components/CompositionTable.vue`
- `demoday/frontend/src/utils/scores.ts` — LIS/TAS 계산 함수

**scores.ts:**
```typescript
export function calcLIS(predicted: Props4, measured: Props4): number {
  const errs = PROPS.map(k => Math.abs(predicted[k] - measured[k]) / Math.abs(measured[k]))
  return Math.max(0, 1 - errs.reduce((a,b) => a+b, 0) / errs.length)
}
export function calcTAS(measured: Props4, target: Props4, weights: Weights4): number {
  let num = 0, den = 0
  for (const k of PROPS) {
    const score = Math.max(0, 1 - Math.abs(measured[k] - target[k]) / Math.abs(target[k]))
    num += weights[k] * score; den += weights[k]
  }
  return den > 0 ? num / den : 0
}
```

**Table structure:**
- 커스텀 HTML `<table>` (2행 헤더: 그룹명 + 속성명)
- LIS 그룹 컬럼 배경 `#d1fae5`, TAS 그룹 `#ffedd5`
- 하단 고정 행: global_target 값 표시
- 우하단: [RESET] 버튼
- 우상단: [실험 설계] [실험 시작] — store 상태에 따라 전환

**Acceptance:**
- 샘플 행 추가 시 측정값 없으면 오차/LIS/TAS = `—`
- 측정값 입력(시뮬레이션) 후 LIS/TAS 자동 계산
- [실험 설계] → modal 열림, [실험 시작] → store state `running`으로 전환

---

### Task 3-2: ExperimentDesignModal
**What:** 조성명 + 예측값 4개 입력 폼
**Files:**
- `demoday/frontend/src/components/ExperimentDesignModal.vue`

**Acceptance:**
- 확인 시: store에 샘플 행 추가, state `designed`로 전환
- 취소: 닫힘만
- 이미 designed/running/done 상태이면 [실험 설계] 버튼 비활성

---

## Phase 4 — Device Panel + Experiment Banner

### Task 4-1: DevicePanel 애니메이션
**What:** 9개 카드, 순차 활성화, 실험 중 카드 내 데이터 표시
**Files:**
- `demoday/frontend/src/components/DevicePanel.vue`
- `demoday/frontend/src/components/DeviceCard.vue`

**Animation logic:**
```typescript
function startActivation() {
  const id = ++runId
  devices.forEach((_, i) => {
    setTimeout(() => {
      if (id !== runId) return
      activeIndex.value = i
    }, i * config.timing.device_activation_interval_ms)
  })
}
// watch: store.state === 'idle' → startActivation()
```

**실험 중 카드 데이터**: `store.deviceIndex >= i`이면 해당 샘플의 experiment[device.id] 값 표시

**Acceptance:**
- 최초 로드 → 2초 간격 순차 점등
- RESET → 모두 꺼졌다가 재시작
- 실험 deviceIndex=2(전기로) 도달 시 전기로 카드에 STEP 데이터 표시

---

### Task 4-2: ExperimentBanner
**What:** 실험중/완료 배너, spinner 애니메이션, 타이밍 YAML 연동
**Files:**
- `demoday/frontend/src/components/ExperimentBanner.vue`

**Flow per step:**
```
show("OO 실험중...", spinner)   → wait(running_ms)
show("OO 실험 완료", checkmark) → wait(complete_ms)
                                   wait(gap_ms)
→ next device
→ after all 9: triggerExperimentComplete()
```

**triggerExperimentComplete():**
- 현재 샘플 행에 측정값 자동 입력 (YAML samples[id].measurement)
- LIS/TAS 계산 → 행 업데이트
- useTrendStore에 누적
- auto_tune_enabled → next_composition 새 행 추가
- store.state → `done`

**Acceptance:**
- 실험 시작 후 9스텝 × (running + complete + gap)ms 후 배너 사라짐
- RESET 시 중간 취소 (runId 방식)
- 측정값 자동 입력 확인

---

## Phase 5 — Score Trend

### Task 5-1: ScoreTrend + Plotly
**What:** 누적 LIS/TAS 꺾은선 2개 그래프
**Files:**
- `demoday/frontend/src/components/ScoreTrend.vue`

**Plotly import:**
```typescript
import Plotly from 'plotly.js-basic-dist'
// lazy-load via defineAsyncComponent if needed
```

**Data:** useTrendStore.lisHistory / tasHistory (누적합 배열)

**Acceptance:**
- 실험 완료 시마다 그래프 자동 업데이트
- RESET 시 초기화
- 좌우 반반, LIS=파랑, TAS=주황

---

## Phase 6 — Integration & Deploy

### Task 6-1: App.vue 통합 + 최종 레이아웃
**What:** 3행 전체 레이아웃 조립, 스타일 통일
**Files:**
- `demoday/frontend/src/App.vue`
- `demoday/frontend/src/css/app.css`

**Acceptance:**
- 전체 플로우 E2E 수동 검증 (RESET → 설계 → 시작 → 완료 → 튜닝 → Score Trend 업데이트)

---

### Task 6-2: HuggingFace 배포
**What:** Docker 이미지 빌드 + HF Spaces 배포
**Files:** `Dockerfile` (최종 검증)

**Acceptance:**
- `/health` 200 반환
- HF Spaces에서 접속 → 전체 기능 동작

---

## Risk Mitigations

| Risk | 대응 |
|---|---|
| R1: 상태머신 레이스 | useExperimentStore 단일 소스, runId 게이팅 |
| R2: 타이밍 drift | setTimeout chain (setInterval 사용 금지), cleanup 반드시 |
| R3: Plotly 번들 크기 | plotly.js-basic-dist, defineAsyncComponent lazy-load |
| R4: ETag 오작동 | mtime hash, 304 처리 프론트에서 검증 |
| R5: Docker 경로 | 환경변수 DEMO_CONFIG_PATH, dist 절대경로 검증 |

---

## Verification Checklist

- [ ] YAML 수정 → 재시작 없이 반영
- [ ] RESET → 장치 애니메이션 재실행
- [ ] 실험 설계 → [실험 시작] 활성화
- [ ] 실험 시작 → 배너 순차 표시 → 측정값 자동 입력
- [ ] LIS/TAS 계산 정확성 (unit test: scores.ts)
- [ ] Score Trend 누적 업데이트
- [ ] 조성 튜닝 새 행 추가 (auto_tune_enabled=true)
- [ ] Docker 빌드 → port 7860 정상 서빙
