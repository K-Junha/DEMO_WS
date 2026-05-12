// 유리 조성 실험 점수 계산 유틸리티
// LIS (Linear Improvement Score): 예측 정확도 점수
// TAS (Target Achievement Score): 목표치 달성도 점수

// 4가지 물성 (Tg, CTE, 유전율, 유전상수)을 묶는 타입
export type Props4 = {
  tg: number
  cte: number
  dielectric: number
  dielectric_const: number
}

export type Weights4 = Props4

// 반복 계산에 사용할 속성 키 배열
const PROPS: (keyof Props4)[] = ['tg', 'cte', 'dielectric', 'dielectric_const']

/**
 * LIS 계산: 예측값과 측정값의 평균 상대 오차로 정확도를 0~1로 표현
 * - 오차가 0이면 LIS = 1.0 (완벽한 예측)
 * - 평균 오차가 100% 이상이면 LIS = 0.0 (하한선 0)
 */
export function calcLIS(predicted: Props4, measured: Props4): number {
  const errs = PROPS.map(k => Math.abs(predicted[k] - measured[k]) / Math.abs(measured[k]))
  return Math.max(0, 1 - errs.reduce((a, b) => a + b, 0) / errs.length)
}

/**
 * TAS 계산: 각 물성의 목표치 달성도를 가중 평균으로 합산
 * - 측정값이 목표치와 같으면 해당 물성 점수 = 1.0
 * - weights로 중요도(Tg, CTE 등)를 다르게 적용 가능
 */
export function calcTAS(measured: Props4, target: Props4, weights: Weights4): number {
  let num = 0
  let den = 0
  for (const k of PROPS) {
    const err = Math.abs(measured[k] - target[k]) / Math.abs(target[k])
    const score = Math.max(0, 1 - err)
    num += weights[k] * score
    den += weights[k]
  }
  // 가중치 합이 0이면 NaN 방지
  return den > 0 ? num / den : 0
}
