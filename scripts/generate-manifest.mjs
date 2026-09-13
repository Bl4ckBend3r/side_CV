import { readdir, readFile, writeFile, mkdir } from 'node:fs/promises';
import { basename, join } from 'node:path';

const jobsDir = new URL('../jobs/', import.meta.url);
const files = (await readdir(jobsDir)).filter(file => file.endsWith('.html')).sort();
const getMeta = (html, name) => html.match(new RegExp(`<meta\\s+name=["']${name}["']\\s+content=["']([^"']+)["']`, 'i'))?.[1];
const grouped = new Map();
const downloadsDir = new URL('../downloads/', import.meta.url);
await mkdir(downloadsDir, { recursive: true });
const css = await readFile(new URL('../css/cv.css', import.meta.url), 'utf8');

for (const file of files) {
  const html = await readFile(new URL(file, jobsDir), 'utf8');
  const key = getMeta(html, 'cv-key') || basename(file, '.html').replace(/-en$/, '');
  const lang = getMeta(html, 'cv-lang') || (file.endsWith('-en.html') ? 'en' : 'pl');
  const profile = grouped.get(key) || { key, versions: {} };
  if (!/^[a-z0-9-]+$/.test(key) || !['pl', 'en'].includes(lang)) {
    throw new Error('Invalid CV key or language: ' + file);
  }
  const filename = `Witold_Grzesiak_${key}_${lang.toUpperCase()}.html`;
  // Export the original CV body, without website navigation or external styles.
  // Do not modify any source CV (including General PL/EN).
  const standalone = html
    .replace(/<link\b[^>]*>/gi, '')
    .replace(/<div class="top-widgets">[\s\S]*?(?=<div class="profile-header">)/, '')
    .replace('</head>', '<style>\n' + css + '\n</style>\n</head>');
  await writeFile(new URL(filename, downloadsDir), standalone);
  profile.versions[lang] = {
    title: getMeta(html, 'cv-title') || key.replaceAll('-', ' '),
    description: getMeta(html, 'cv-description') || 'Professional profile',
    path: `./jobs/${file}`,
    downloadPath: `./downloads/${filename}`
  };
  grouped.set(key, profile);
}

const profiles = [...grouped.values()]
  .filter(profile => profile.versions.pl && profile.versions.en)
  .sort((a, b) => (a.key === 'ogolne' ? -1 : b.key === 'ogolne' ? 1 : a.versions.pl.title.localeCompare(b.versions.pl.title, 'pl')));
if (profiles.length * 2 !== files.length) throw new Error('Każdy profil CV musi mieć dokładnie wersję PL i EN.');
await writeFile(join(new URL(jobsDir).pathname, 'manifest.json'), `${JSON.stringify(profiles, null, 2)}\n`);
console.log(`Wygenerowano ${profiles.length} profili CV w wersjach PL i EN.`);
