---
title: WS Lab Pilot
emoji: 🧪
colorFrom: indigo
colorTo: blue
sdk: docker
pinned: false
app_port: 7860
---

# WS LAB PILOT — DEMO DAY

유리 조성 최적화 실험을 Bayesian Optimization(BO) 워크플로우로 시뮬레이션하는 투자자 데모 앱.

## 스택

| 영역 | 기술 |
|---|---|
| Frontend | Vue 3 + TypeScript + Quasar v2 (`@quasar/app-vite@2.6.0`) |
| 상태관리 | Pinia |
| 차트 | Plotly.js (plotly.js-basic-dist) |
| Backend | FastAPI (Python 3.11) |
| 데이터 | `config/demo_data.yaml` (YAML 더미 데이터) |
| 배포 | Docker multi-stage → HuggingFace Spaces (port 7860) |

## 주요 개념

**상태 머신**: `idle → designed → running → done`

**LIS (Learning Impact Score)**: 예측 모델 영향력 — 예측값 vs 실측값의 근접도. BO 모델이 학습될수록 향상.

**TAS (Target Achievement Score)**: 목표 달성도 — 실측값 vs 목표치의 근접도. 조성이 최적화될수록 향상.

**BO 수렴 시나리오 (S-001 ~ S-010)**:
- S-001~003: 예측=목표(낙관적), 실측=목표와 괴리 → LIS/TAS 낮음
- S-004: 모델 캘리브레이션 돌파 → LIS 0.65→0.91 급등
- S-005: LIS↑(0.96) TAS↓(0.57) — 모델은 정확해졌으나 조성 성능 미달
- S-008: LIS 유지, TAS 소폭 하락 (비단조 구간)
- S-010: 수렴 완료 (LIS≈0.997, TAS≈0.993)

## 프로젝트 구조

```
demoday/
├── config/
│   └── demo_data.yaml        # 실험 시나리오 데이터 (S-001~S-020)
├── frontend/
│   └── src/
│       ├── App.vue            # 레이아웃, 시뮬레이션 버튼, RESET
│       ├── components/
│       │   ├── DevicePanel.vue           # 장치 카드 목록
│       │   ├── DeviceCard.vue            # 개별 장치 카드 (shimmer 로딩)
│       │   ├── CompositionTable.vue      # 실험 결과 테이블 + 튜닝 팝업
│       │   ├── ExperimentDesignModal.vue # 조성 설계 모달 (AI 예측 버튼)
│       │   ├── ExperimentBanner.vue      # 실험 진행 팝업 (pageFlip 애니메이션)
│       │   └── ScoreTrend.vue            # LIS/TAS 트렌드 차트
│       ├── stores/
│       │   ├── experiment.ts  # 실험 상태 머신
│       │   ├── config.ts      # YAML 설정 로드
│       │   └── trend.ts       # LIS/TAS 히스토리
│       └── utils/
│           └── scores.ts      # calcLIS, calcTAS
├── worklog/
│   └── worklog_YYYY-MM-DD.md
└── README.md
```

## 개발

```bash
# 프론트엔드 빌드
cd frontend
pnpm install
pnpm build        # dist/spa/ 생성

# 개발 서버
pnpm dev          # localhost:9000
```

## 배포

```bash
git push origin main   # GitHub
git push hf main       # HuggingFace Spaces (자동 빌드)
```

## 주요 기능

- **조성 설계**: 산화물(SiO2/Al2O3/B2O3) 드롭다운 + wt% 입력, 합계 100% 검증
- **AI 조성 예측**: 예측 버튼 → 1초 로딩 → YAML 연결 샘플의 predicted 값 표시
- **실험 진행**: 9개 장치 순차 애니메이션 (저울→믹서→전기로→…→유전율측정기)
- **BO 튜닝**: 실험 완료 후 튜닝 버튼 → DNA-wave 분석 애니메이션 → 다음 추천 조성 표시
- **시뮬레이션**: 현재 시점부터 S-010까지 자동 순차 실험 (툴바 버튼)
- **ScoreTrend**: 예측 모델 영향력 추이(LIS) / 목표 달성도 추이(TAS) Plotly 차트
