import test from 'node:test';
import assert from 'node:assert/strict';
import { scoreView } from './score-view.mjs';

test('unavailable compatibility number is hidden', () => {
  assert.deepEqual(scoreView(50,'unavailable'), {label:'待确认',plotValue:null,note:'当前可确认的课堂记录尚不足以形成该项评价'});
});
test('valid zero stays visible', () => {
  assert.equal(scoreView(0,'available').plotValue, 0);
  assert.equal(scoreView(0,'available').label, '0');
});
test('partial evidence has a scope note', () => assert.equal(scoreView(80,'partial').note,'基于本次可评价内容'));
test('legacy fifty is not automatically hidden', () => assert.equal(scoreView(50).plotValue,50));
test('missing value is not a numerical fallback', () => assert.equal(scoreView(null,'available').plotValue,null));
test('invalid input fails', () => {
  for (const v of [NaN,Infinity,-1,101,'50',true,undefined]) assert.throws(() => scoreView(v));
  assert.throws(() => scoreView(50,'low-confidence'));
});
