import {readFile} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {scoreView} from './score-view.mjs';

export function reportViews(report) {
  if (report?.sample_kind !== 'synthetic' || !Array.isArray(report.chapters) || !report.chapters.length) {
    throw new TypeError('a nonempty synthetic report is required');
  }
  const seen = new Set();
  return report.chapters.map(chapter => {
    if (!chapter || typeof chapter.id !== 'string' || !chapter.id.trim() || seen.has(chapter.id) || typeof chapter.title !== 'string' || !chapter.title.trim()) {
      throw new TypeError('chapters require unique nonempty ids and titles');
    }
    seen.add(chapter.id);
    return {id:chapter.id, title:chapter.title, ...scoreView(chapter.score, chapter.evaluation)};
  });
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  if (process.argv.length !== 3) throw new Error('usage: node examples/report-display/print-report.mjs report.json');
  const report = JSON.parse(await readFile(process.argv[2], 'utf8'));
  console.log(JSON.stringify({sample_kind:'synthetic', chapters:reportViews(report)}, null, 2));
}
