#!/usr/bin/env node
/**
 * Export Cursor agent transcripts (JSONL) to readable Markdown.
 * Run from repo root. Output: ./cursor-chats-export/
 *
 * Usage: node scripts/export-cursor-transcripts.js [transcripts-dir]
 * Default transcripts dir: ~/.cursor/projects
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');

const PROJECTS = process.argv[2] || path.join(process.env.HOME || '', '.cursor', 'projects');
const OUT_DIR = path.join(process.cwd(), 'cursor-chats-export');

function findJsonlFiles(dir, acc = []) {
  if (!fs.existsSync(dir)) return acc;
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const e of entries) {
    const full = path.join(dir, e.name);
    if (e.isDirectory()) findJsonlFiles(full, acc);
    else if (e.name.endsWith('.jsonl')) acc.push(full);
  }
  return acc;
}

function extractText(content) {
  if (!Array.isArray(content)) return '';
  return content
    .map((c) => {
      if (c.type === 'text' && c.text) return c.text;
      if (c.type === 'tool_use' && c.name) return `[Tool: ${c.name}]`;
      return '';
    })
    .filter(Boolean)
    .join('\n');
}

function firstLine(s, max = 80) {
  const line = (s || '').replace(/\s+/g, ' ').trim();
  return line.length > max ? line.slice(0, max) + '…' : line;
}

function titleFromFirstUserQuery(text) {
  const m = text.match(/<user_query>\s*\n?(.*?)(?:\n<\/user_query>|$)/is);
  const raw = m ? m[1].trim() : text.trim();
  return firstLine(raw, 60);
}

async function exportOne(jsonlPath) {
  const lines = [];
  const fileStream = fs.createReadStream(jsonlPath);
  const rl = readline.createInterface({ input: fileStream, crlfDelay: Infinity });
  let title = path.basename(jsonlPath, '.jsonl');

  for await (const line of rl) {
    if (!line.trim()) continue;
    try {
      const row = JSON.parse(line);
      const role = row.role;
      const text = extractText(row.message?.content);
      if (!text) continue;
      if (role === 'user' && title === path.basename(jsonlPath, '.jsonl')) {
        title = titleFromFirstUserQuery(text);
      }
      const label = role === 'user' ? '**User**' : '**Assistant**';
      lines.push(`${label}\n\n${text}\n\n---\n`);
    } catch (_) {}
  }

  return { title, body: lines.join('\n') };
}

function safeFilename(s) {
  return s.replace(/[<>:"/\\|?*]/g, '-').slice(0, 100);
}

async function main() {
  const files = findJsonlFiles(PROJECTS);
  if (!files.length) {
    console.error('No .jsonl files under:', PROJECTS);
    process.exit(1);
  }

  fs.mkdirSync(OUT_DIR, { recursive: true });
  const index = [];
  let n = 0;
  for (const f of files) {
    const { title, body } = await exportOne(f);
    const slug = safeFilename(title || path.basename(f, '.jsonl'));
    const base = `${String(n + 1).padStart(3, '0')}-${slug}`;
    const mdPath = path.join(OUT_DIR, base + '.md');
    const rel = path.relative(process.cwd(), f);
    const header = `# ${title || 'Chat'}\n\nSource: \`${rel}\`\n\n---\n\n`;
    fs.writeFileSync(mdPath, header + body, 'utf8');
    index.push({ path: base + '.md', title: title || base, source: rel });
    n++;
  }

  const indexMd = [
    '# Cursor chat export',
    '',
    `Exported ${n} conversations from \`${PROJECTS}\`.`,
    '',
    '| # | Title | File |',
    '|---|-------|------|',
    ...index.map((e, i) => `| ${i + 1} | ${e.title} | [${e.path}](${e.path}) |`),
  ].join('\n');
  fs.writeFileSync(path.join(OUT_DIR, 'INDEX.md'), indexMd, 'utf8');
  console.log('Exported', n, 'chats to', OUT_DIR);
  console.log('Open INDEX.md for a list.');
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
