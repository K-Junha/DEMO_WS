export type Props4 = {
  tg: number
  cte: number
  dielectric: number
  dielectric_const: number
}

export type Weights4 = Props4

const PROPS: (keyof Props4)[] = ['tg', 'cte', 'dielectric', 'dielectric_const']

export function calcLIS(predicted: Props4, measured: Props4): number {
  const errs = PROPS.map(k => Math.abs(predicted[k] - measured[k]) / Math.abs(measured[k]))
  return Math.max(0, 1 - errs.reduce((a, b) => a + b, 0) / errs.length)
}

export function calcTAS(measured: Props4, target: Props4, weights: Weights4): number {
  let num = 0
  let den = 0
  for (const k of PROPS) {
    const err = Math.abs(measured[k] - target[k]) / Math.abs(target[k])
    const score = Math.max(0, 1 - err)
    num += weights[k] * score
    den += weights[k]
  }
  return den > 0 ? num / den : 0
}
