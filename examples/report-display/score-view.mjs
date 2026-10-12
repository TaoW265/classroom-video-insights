// Independent display example; no production JSON or model calls.
export function scoreView(score, evaluation) {
  if (score !== null && (typeof score !== 'number' || !Number.isFinite(score) || score < 0 || score > 100)) {
    throw new TypeError('invalid score');
  }
  if (evaluation !== undefined && !['available', 'partial', 'unavailable'].includes(evaluation)) throw new TypeError('invalid evaluation');
  if (evaluation === 'unavailable') return {label:'待确认',plotValue:null,note:'当前可确认的课堂记录尚不足以形成该项评价'};
  if (score === null) return {label:'暂缺',plotValue:null,note:'当前记录缺少该项数值'};
  return {label:String(score),plotValue:score,note:evaluation === 'partial' ? '基于本次可评价内容' : ''};
}
