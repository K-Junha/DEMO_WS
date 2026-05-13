# WS Lab Pilot — Demo Day App SPEC

## 1. Objective

투자자 대상 데모데이용 WS Lab Pilot 경량 버전.  
실제 하드웨어·DB 없이 YAML 더미 데이터로 전체 실험 워크플로를 시뮬레이션하는 단일 페이지 웹앱.  
Docker 컨테이너로 패키징하여 HuggingFace Spaces에 배포.

**타겟 사용자:** 투자자 / 데모 발표자  
**핵심 가치:** 조성 설계 → 실험 → 측정 → 점수 누적 흐름을 직관적으로 시연

---

## 2. Tech Stack

| 레이어 | 기술 |
|---|---|
| Frontend | Vue 3 + TypeScript 5 + Quasar v2 + Plotly.js (basic-dist) |
| Backend | FastAPI (async) + uvicorn |
| 상태 관리 | Pinia (3 stores) |
| 패키지 매니저 | pnpm |
| 설정 | YAML (`config/demo_data.yaml`, 외부 편집 가능) |
| 컨테이너 | Docker multi-stage (node:20-alpine → python:3.11-slim) |
| 배포 | HuggingFace Spaces, port 7860 |

---

## 3. Commands

```bash
# 개발
cd frontend && pnpm dev                                    # Vue dev server (포트 5173)
cd backend && uvicorn app.main:app --reload --port 7860   # FastAPI

# 빌드 & 실행
cd frontend && pnpm build
docker build -t ws-demo .
docker run -p 7860:7860 ws-demo

# 설정 수정 (앱 재시작 불필요 — mtime hot-reload)
# config/demo_data.yaml 직접 편집
```

---

## 4. Project Structure

```
demoday/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, StaticFiles mount, SPA fallback
│   │   ├── routers/
│   │   │   └── config.py        # GET /api/config (ETag + mtime 캐시)
│   │   └── schemas.py           # Pydantic config shape 모델
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── DevicePanel.vue            # ① Connected Devices
│   │   │   ├── CompositionTable.vue       # ② Glass Composition + 측정결과
│   │   │   ├── ExperimentBanner.vue       # 실험중/완료 배너
│   │   │   ├── ExperimentDesignModal.vue  # 실험 설계 모달
│   │   │   └── ScoreTrend.vue             # ③ Score Trend (Plotly)
│   │   ├── stores/
│   │   │   ├── config.ts        # useConfigStore — YAML 데이터·타이밍 (read-only)
│   │   │   ├── experiment.ts    # useExperimentStore — 상태머신·측정값·LIS/TAS
│   │   │   └── trend.ts         # useTrendStore — 누적 LIS/TAS 배열 (Plotly용)
│   │   ├── App.vue
│   │   └── main.ts
│   ├── package.json
│   └── quasar.config.ts
├── config/
│   └── demo_data.yaml           # 더미 데이터 (외부 편집 가능)
├── Dockerfile
└── SPEC.md
```

---

## 5. Screen Layout

단일 페이지, 3행 풀width:

```
┌──────────────────────────────────────────────────────┐
│  ① Connected Devices                                 │
├──────────────────────────────────────────────────────┤
│  ② Glass Composition Samples + 측정결과               │
├──────────────────────────────────────────────────────┤
│  ③ Score Trend                                       │
└──────────────────────────────────────────────────────┘
```

---

## 6. Feature Specifications

### ① Connected Devices (`DevicePanel.vue`)

**장치 목록 (9개, 순서 고정):**

| 순서 | 장치명 | 측정 항목 |
|---|---|---|
| 1 | 저울 | — |
| 2 | 믹서 | — |
| 3 | 전기로 | — |
| 4 | 서냉로 | — |
| 5 | 프레스 | — |
| 6 | DTA | Tg |
| 7 | DSC | Tg |
| 8 | 딜라토미터 | CTE |
| 9 | 유전율측정기 | 유전율, 유전상수 |

**활성화 애니메이션:**
- 최초 로드 / RESET 시: 모든 카드 비활성(회색/불투명) 상태로 시작
- `device_activation_interval_ms`(기본 2000ms) 간격으로 순차 활성화
- 활성화 효과: 카드 밝아짐 + 초록 LED 점등 (CSS transition)

**카드 구성:** 장치명, 모델명, 프로토콜 배지, IP:Port, 연결 상태 LED

**실험 진행 중 카드 내 데이터 표시 (해당 장치 스텝 도달 시):**

| 장치 | 카드 내 표시 항목 |
|---|---|
| 저울 | 세팅무게 (g), 현재무게 (g) |
| 믹서 | 가동시간 |
| 전기로 | STEP별: 세팅온도 / 측정온도 / 유지시간 / 승온속도 |
| 서냉로 | 세팅온도, 정지온도, 시간 |
| 프레스 | 가해지는 압력 (MPa) |
| DTA / DSC / 딜라토미터 / 유전율측정기 | 측정 완료 표시 |

- 데이터는 YAML `samples[id].experiment` 섹션에서 로드
- 실험 완료 후에도 마지막 값 유지, RESET 시 초기화

---

### ② Glass Composition Samples + 측정결과 (`CompositionTable.vue`)

**테이블 컬럼 구조:**

| 구분 | 컬럼 | 배경색 |
|---|---|---|
| 기본 | ID, 조성 | 기본 |
| 기본 | TG 예측/측정, CTE 예측/측정, 유전율 예측/측정, 유전상수 예측/측정 | 기본 |
| LIS 그룹 | 예측오차(TG, CTE, 유전율, 유전상수), **LIS** | 초록 (`#d1fae5`) |
| TAS 그룹 | 타겟오차(TG, CTE, 유전율, 유전상수), **TAS** | 주황 (`#ffedd5`) |
| 액션 | [조성 튜닝] | 파랑 (실험 완료 후만 활성) |

**오차·점수 계산 (자동, 측정값 입력 시):**

예측 오차(항목) — 상대오차:
```
예측오차_i = |예측값_i - 측정값_i| / |측정값_i|
타겟오차_j = |측정값_j - 목표값_j| / |목표값_j|
```

LIS — 예측 정확도 점수 (N=4 속성):
```
LIS = max(0, 1 - (1/N) × Σ 예측오차_i)       범위: [0, 1]
```

TAS — 목표 달성 점수 (가중 평균, Phase R 연동):
```
TAS = Σ(w_j × max(0, 1 - 타겟오차_j)) / Σw_j  범위: [0, 1]
```
- `w_j` 가중치는 YAML `global_target.weights`에서 설정
- 두 점수 모두 1에 가까울수록 우수

**버튼 상태 흐름:**
```
초기:         [실험 설계 ✓활성]  [실험 시작 ✗비활성]
설계 완료 후: [실험 설계 ✗비활성] [실험 시작 ✓활성]
실험 완료 후: 해당 행 [조성 튜닝 ✓활성]
```

**하단 고정 행:** 전체 공통 목표치 표시 — TG / CTE / 유전율 / 유전상수  
- 모든 샘플이 동일한 단일 목표를 공유 (YAML `global_target` 섹션)
- TAS 계산 시 이 값이 기준

**좌하단:** `[RESET]` 버튼 — 전체 초기화 + 장치 애니메이션 재실행

**조성 샘플 수 규칙:**
- YAML에 S-001 ~ S-020 사전 정의
- 20개 초과 시: YAML `random_range` 내에서 랜덤 값 자동 생성

---

### 실험 설계 모달 (`ExperimentDesignModal.vue`)

> 내용은 추후 보완 예정 (다른 작업자 담당)  
> 현재 구현 범위: 아래 필드만 포함

입력 필드:
- 조성명 (문자열)
- 예측값: TG, CTE, 유전율, 유전상수

> 목표값은 전체 공통 (`global_target`) — 모달에서 입력하지 않음

확인 시: 테이블에 행 추가, `[실험 시작]` 활성화

---

### 실험 진행 배너 (`ExperimentBanner.vue`)

테이블 상단 고정. 실험 시작 시 표시, 완전 완료 후 사라짐.

**각 스텝 시퀀스 (YAML `timing` 섹션에서 설정):**

```
[⏳ 스피너 + "저울 실험중..."]   experiment_running_ms  (기본 2000ms)
[✓  "저울 실험 완료"]            experiment_complete_ms (기본 1000ms)
    (공백)                       experiment_gap_ms      (기본 500ms)
[⏳ "믹서 실험중..."]            ...
```

- 9개 장치 순서대로 반복
- 기본 총 소요 시간: 9 × (2000 + 1000 + 500) = 31.5초
- 모든 장치 완료 후:
  - 해당 행 TG/CTE/유전율/유전상수 측정값 YAML 값으로 자동 입력
  - 상대오차 / LIS / TAS 자동 계산 및 표시
  - `[조성 튜닝]` 버튼 활성화
  - Score Trend 업데이트
  - `auto_tune_enabled: true`이면 다음 추천 조성을 새 행으로 자동 추가

**RESET 안전장치:** 실험 진행 중 RESET 클릭 시 진행 중인 타이머 전부 취소 (`runId` 방식으로 stale timeout 방지)

---

### ③ Score Trend (`ScoreTrend.vue`)

Plotly.js (`plotly.js-basic-dist`) 사용.  
좌우 반반 2개 그래프:

| | LIS (좌) | TAS (우) |
|---|---|---|
| X축 | num of samples | num of samples |
| Y축 | 누적합 LIS (각 실험 완료 시 +LIS) | 누적합 TAS (각 실험 완료 시 +TAS) |
| 색상 | 파랑 | 주황 |
| 범위 | Y ≥ 0 (개별 LIS ∈ [0,1]) | Y ≥ 0 (개별 TAS ∈ [0,1]) |

- 실험 완료 시마다 해당 행의 LIS/TAS 값을 누적합 배열에 추가
- RESET 시 전체 초기화

---

## 7. YAML Config (`config/demo_data.yaml`)

```yaml
timing:
  device_activation_interval_ms: 2000
  experiment_running_ms: 2000
  experiment_complete_ms: 1000
  experiment_gap_ms: 500

# 전체 공통 목표치 — 모든 샘플이 동일한 목표를 공유
# TAS 계산 기준값 + 가중치
global_target:
  tg:              520.0
  cte:             8.5
  dielectric:      6.2
  dielectric_const: 3.5
  weights:           # TAS 가중 평균용 w_j
    tg:              1.0
    cte:             1.0
    dielectric:      1.0
    dielectric_const: 1.0

# 조성 튜닝 자동 추가 on/off
# true: 실험 완료 시 next_composition 새 행 자동 추가
# false: [조성 튜닝] 버튼만 활성화, 사용자가 수동 클릭
auto_tune_enabled: true

random_range:
  tg:              { min: 500, max: 560 }
  cte:             { min: 7.5, max: 9.5 }
  dielectric:      { min: 5.5, max: 7.0 }
  dielectric_const: { min: 2.8, max: 4.0 }

devices:
  - id: scale
    name: 저울
    model: "A&D FX-3000i"
    protocol: RS-232
    ip: 192.168.1.10
    port: 5001
    connected: true
  - id: mixer
    name: 믹서
    model: "IKA RW 20"
    protocol: RS-485
    ip: 192.168.1.11
    port: 5002
    connected: true
  - id: furnace
    name: 전기로
    model: "Carbolite RHF 14/8"
    protocol: Ethernet
    ip: 192.168.1.12
    port: 5003
    connected: true
  - id: anneal
    name: 서냉로
    model: "Nabertherm L3/11"
    protocol: Ethernet
    ip: 192.168.1.13
    port: 5004
    connected: true
  - id: press
    name: 프레스
    model: "Struers Tegramin-25"
    protocol: RS-485
    ip: 192.168.1.14
    port: 5005
    connected: true
  - id: dta
    name: DTA
    model: "Netzsch STA 449 F3"
    protocol: Ethernet
    ip: 192.168.1.16
    port: 5007
    connected: true
    measures: [Tg]
  - id: dsc
    name: DSC
    model: "TA Instruments DSC 250"
    protocol: Ethernet
    ip: 192.168.1.17
    port: 5008
    connected: true
    measures: [Tg]
  - id: dilatometer
    name: 딜라토미터
    model: "Netzsch DIL 402 C"
    protocol: RS-232
    ip: 192.168.1.18
    port: 5009
    connected: false
    measures: [CTE]
  - id: permittivity
    name: 유전율측정기
    model: "Agilent E4980A"
    protocol: Ethernet
    ip: 192.168.1.19
    port: 5010
    connected: true
    measures: [유전율, 유전상수]

samples:
  - id: S-001
    composition: "SiO2:70, Al2O3:18, B2O3:12"
    predicted:                           # 실험 설계 시 입력 (예측값)
      tg: 515.0
      cte: 8.2
      dielectric: 6.0
      dielectric_const: 3.2
    measurement:                         # 실험 완료 시 자동 입력될 값
      tg: 520.3
      cte: 8.5
      dielectric: 6.2
      dielectric_const: 3.48
    next_composition: "SiO2:68, Al2O3:20, B2O3:12"   # 조성 튜닝 추천값
    experiment:
      scale:
        target_weight: 150.0
        current_weight: 149.8
      mixer:
        operation_time: "30min"
      furnace:
        steps:
          - { step: 1, target_temp: 800,  measured_temp: 798,  hold_time: "30min", heating_rate: 5  }
          - { step: 2, target_temp: 1400, measured_temp: 1398, hold_time: "60min", heating_rate: 10 }
      annealing:
        target_temp: 500
        stop_temp: 50
        time: "120min"
      press:
        pressure: 20
  # S-002 ~ S-020 동일 구조로 작성
```

---

## 8. State Machine (`useExperimentStore`)

```
idle
 └─[실험 설계 완료]─→ designed
     └─[실험 시작]──→ running { deviceIndex: 0..8, phase: 'running' | 'complete' }
         └─[모든 스텝 완료]─→ done
             └─[RESET]──────→ idle
```

- RESET: 모든 store 초기화 + 장치 애니메이션 재실행 트리거
- 진행 중 RESET: `runId` 증가로 stale timeout 자동 무효화

---

## 9. API Endpoints

| Method | Path | 설명 |
|---|---|---|
| GET | `/api/config` | YAML 전체 반환 (ETag + mtime 캐시, hot-reload) |
| GET | `/health` | 헬스체크 (`{"status": "ok"}`) |
| GET | `/*` | Vue SPA 정적 파일 서빙 (fallback → index.html) |

YAML 경로: 환경변수 `DEMO_CONFIG_PATH` (기본 `/app/config/demo_data.yaml`)

---

## 10. Docker

```dockerfile
# Stage 1: Frontend build
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/ .
RUN npm install -g pnpm && pnpm install && pnpm build

# Stage 2: Runtime
FROM python:3.11-slim
WORKDIR /app
COPY backend/ ./backend/
COPY config/ ./config/
COPY --from=frontend-build /app/frontend/dist ./frontend/dist
RUN pip install -e ./backend
EXPOSE 7860
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
```

- FastAPI `StaticFiles`로 `frontend/dist` 마운트
- 모든 미매칭 경로 → `index.html` fallback (SPA routing)
- HuggingFace Spaces 데모 전 `/health` 사전 워밍 권장

---

## 11. Code Style

### Frontend
- `<script setup lang="ts">` 형태 통일
- `any` 타입 금지 — 명시적 타입 사용
- SCSS 주석: `/* */` 사용 (`//` 금지)
- 전역 상태만 Pinia, 나머지는 composables

### Backend
- 모든 핸들러 `async def`
- 환경변수: pydantic-settings
- YAML 파싱: `PyYAML` (`safe_load`)

---

## 12. Testing Strategy

데모 앱이므로 최소 범위:
- **Backend:** `pytest` — `/api/config` 응답 shape 검증, YAML 파싱 오류 케이스
- **Frontend:** 없음 (데모 범위 외)
- **수동 체크리스트:**
  - [ ] 최초 로드 → 장치 순차 활성화 애니메이션
  - [ ] 실험 설계 → 실험 시작 버튼 전환
  - [ ] 실험 시작 → 배너 표시 → 순차 완료 메시지
  - [ ] 실험 완료 → 측정값 자동 입력, LIS/TAS 계산, Score Trend 업데이트
  - [ ] 조성 튜닝 버튼 활성화 확인
  - [ ] RESET → 전체 초기화 + 애니메이션 재실행
  - [ ] YAML 수정 → 앱 재시작 없이 반영 확인

---

## 13. Boundaries

### Never
- 실제 하드웨어 연결 코드
- DB (SQLAlchemy, asyncpg 등)
- 인증 / JWT
- YAML 프론트엔드 write-back
- 포트 7860 이외 포트 사용
- `any` 타입 (TypeScript)
- SCSS `//` 주석
- `secrets` 또는 API 키를 YAML에 포함

### Ask First
- nginx 추가 (현재 단일 프로세스로 충분)
- supervisord 추가
- 20개 초과 샘플의 영구 저장
- 실험 설계 모달 내용 변경 (다른 작업자 담당)
- Plotly 외 차트 라이브러리 교체
- HuggingFace 외 배포 타겟 추가
