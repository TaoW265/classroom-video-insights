import {readFile,writeFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {scoreView} from '../examples/report-display/score-view.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const report=JSON.parse(await readFile(path.join(root,'samples/report/report.sample.json'),'utf8'));
if(report.sample_kind!=='synthetic') throw new Error('synthetic data only');
const escape=v=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const cards=report.chapters.map(c=>{
 const v=scoreView(c.score,c.evaluation);
 return '<section><h2>'+escape(c.title)+'</h2><p class="value">'+escape(v.label)+'</p><p>'+escape(v.note)+'</p><p>'+escape(c.narrative)+'</p></section>';
}).join('\n');
const html='<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>合成展示报告 · Classroom Video Insights</title><style>body{font:16px/1.7 system-ui,sans-serif;margin:0;background:#f5f7fa;color:#223047}main{max-width:960px;margin:auto;padding:32px 20px}header{padding:24px;background:#fff;border-radius:12px;border:1px solid #dce3ec}.notice{color:#854d0e;background:#fff7dd;padding:12px;border-radius:8px}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;margin:20px 0}section{background:white;padding:20px;border:1px solid #dce3ec;border-radius:12px}h1{font-size:28px}h2{font-size:20px}.value{font-size:32px;color:#245ea8;margin:8px 0}footer{color:#526175}</style></head><body><main><header><p>Classroom Video Insights</p><h1>'+escape(report.title)+'</h1><p class="notice">全部为合成数据 · 独立静态展示页面 · 不代表真实课堂评价或原产品界面</p></header><div class="cards">'+cards+'</div><footer>真实课堂截图、报告及演示视频尚未公开。本预览由 report.sample.json 自动生成。</footer></main></body></html>\n';
await writeFile(path.join(root,'samples/report/report-preview.html'),html);
console.log('Synthetic report generated.');
