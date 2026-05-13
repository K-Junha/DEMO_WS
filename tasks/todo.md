# Demo Day App — Task List

## Phase 1: Project Scaffold
- [x] 1-1: 프로젝트 폴더 초기화 (pnpm + Quasar + FastAPI)
- [ ] 1-2: Dockerfile + 빌드 검증

## Phase 2: Data Layer
- [x] 2-1: YAML 설정파일 작성 (S-001~S-020, 장치, global_target, timing)
- [x] 2-2: /api/config 엔드포인트 (mtime hot-reload, ETag)
- [x] 2-3: Pinia 스토어 3개 (useConfigStore, useExperimentStore, useTrendStore)

## Phase 3: Core UI — CompositionTable
- [x] 3-1: CompositionTable + LIS/TAS 계산 (scores.ts)
- [x] 3-2: ExperimentDesignModal

## Phase 4: Device Panel + Banner
- [x] 4-1: DevicePanel 애니메이션 + DeviceCard
- [x] 4-2: ExperimentBanner (순차 스텝, runId 안전장치)

## Phase 5: Score Trend
- [x] 5-1: ScoreTrend + Plotly.js

## Phase 6: Integration & Deploy
- [x] 6-1: App.vue 통합 + 최종 레이아웃
- [ ] 6-2: HuggingFace 배포
