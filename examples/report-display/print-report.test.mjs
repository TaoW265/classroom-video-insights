import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {reportViews} from './print-report.mjs';

const source = new URL('../../samples/report/report.sample.json', import.meta.url);
const report = JSON.parse(await readFile(source, 'utf8'));

test('JSON reaches all four existing display states without changing input', () => {
  const before = structuredClone(report);
  const views = reportViews(report);
  assert.deepEqual(views.map(({label, plotValue}) => [label, plotValue]), [['85',85], ['待确认',null], ['80',80], ['0',0]]);
  assert.equal(views[2].note, '基于本次可评价内容');
  assert.deepEqual(report, before);
});

test('legacy evaluation remains optional and unavailable compatibility numbers stay hidden', () => {
  const chapters = [{id:'legacy', title:'旧数据', score:50}, {id:'missing', title:'不可评价', score:50, evaluation:'unavailable'}];
  assert.deepEqual(reportViews({sample_kind:'synthetic', chapters}).map(v => v.label), ['50', '待确认']);
});

test('report boundary rejects non-synthetic, malformed and invalid display input', () => {
  for (const value of [null, {sample_kind:'real', chapters:[]}, {...report, chapters:[]}, {...report, chapters:[null]}, {...report, chapters:[{id:'', title:'x', score:0}]}, {...report, chapters:[report.chapters[0],report.chapters[0]]}]) {
    assert.throws(() => reportViews(value));
  }
  assert.throws(() => reportViews({...report, chapters:[{id:'a', title:'x', score:NaN}]}));
});

test('the CLI reads the generated JSON and prints actual scoreView results', () => {
  const cli = fileURLToPath(new URL('./print-report.mjs', import.meta.url));
  const result = spawnSync(process.execPath, [cli, fileURLToPath(source)], {encoding:'utf8'});
  assert.equal(result.status, 0, result.stderr);
  assert.deepEqual(JSON.parse(result.stdout).chapters, reportViews(report));
  assert.notEqual(spawnSync(process.execPath, [cli], {encoding:'utf8'}).status, 0);
});
