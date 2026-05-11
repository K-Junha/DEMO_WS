# Lab Pilot Dashboard

Streamlit 기반 유리(Glass) 합성 실험실 장비 모니터링 대시보드입니다.  
Sila2 프로토콜로 연결된 장비 상태와 실험 샘플 관리를 한 화면에서 확인할 수 있습니다.

---

## 주요 기능

| 영역 | 기능 |
|---|---|
| **Connected Devices** | 저울 · 믹서 · 용융로 · 서냉로 · 가공 장비 연결 상태 LED 표시 |
| **측정 장비 그룹** | DTA · DSC · 딜라토미터 · 유전율측정기 연결 상태 및 측정 항목 |
| **측정 결과 테이블** | Tg · CTE · 유전율 · 유전상수 — 예측값 / 측정1~3 / 목표값 입력 |
| **Glass Composition Samples** | 샘플 CRUD (추가 · 삭제 · 실험 시작), 조성 / 상태 / 점수 관리 |
| **Score Trend 차트** | Learning Impact Score / Target Achievement Score 누적 라인 차트 |

---

## 화면 구성

```
┌───────────────────────────────────┬──────────────────┐
│  Connected Devices (장비 카드)      │  측정 결과 테이블  │
│  저울 · 믹서 · 용융로 · 서냉로 · 가공 │  Tg / CTE / ε… │
├───────────────────────────────────┼──────────────────┤
│  Glass Composition Samples         │  Score Trend     │
│  샘플 목록 + 추가 / 삭제 / 시작       │  LIS / TAS 차트  │
└───────────────────────────────────┴──────────────────┘
```

---

## 기술 스택

- **[Streamlit](https://streamlit.io/)** `≥ 1.40` — UI 프레임워크
- **[Pandas](https://pandas.pydata.org/)** `≥ 2.0` — 데이터 처리
- **[Altair](https://altair-viz.github.io/)** `≥ 5.0` — 인터랙티브 차트
- **Python** `3.11+`

---

## 실행 방법

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

또는 uv를 사용하는 경우:

```bash
uv pip install -r requirements.txt
```

### 2. 앱 실행

```bash
streamlit run streamlit_app.py
```

브라우저에서 `http://localhost:8501` 접속

---

## 파일 구조

```
demoday_streamlit/
├── streamlit_app.py        # 레이아웃 진입점 — 2×2 그리드 wiring
├── devices.py              # 장비 설정, 카드 HTML 렌더러, 측정 결과 테이블
├── samples.py              # 샘플 CRUD, Score 차트, 버튼 CSS
├── requirements.txt
├── .streamlit/
│   └── config.toml         # 다크 테마 (Space Grotesk, Indigo primary)
└── tests/
    ├── test_devices.py     # 장비 모듈 단위 테스트 (38개)
    └── test_samples.py     # 샘플 모듈 단위 테스트 (20개)
```

---

## 테스트 실행

```bash
pytest tests/
```

---

## 장비 구성 (Mock)

| 장비 | 모델 | 프로토콜 |
|---|---|---|
| 저울 | A&D FX-3000i | RS-232 |
| 믹서 | IKA RW 20 | RS-485 |
| 용융로 | Carbolite RHF 14/8 | Ethernet |
| 서냉로 | Nabertherm L3/11 | Ethernet |
| 가공 | Struers Tegramin-25 | RS-485 |
| DTA | Netzsch STA 449 F3 | Ethernet |
| DSC | TA Instruments DSC 250 | Ethernet |
| 딜라토미터 | Netzsch DIL 402 C | RS-232 |
| 유전율측정기 | Agilent E4980A | Ethernet |

> 현재 장비 연결 상태는 Mock 데이터입니다. 실제 Sila2 연결 시 `devices.py`의 `get_device_status()` 함수를 교체하세요.

---

## 라이선스

MIT
