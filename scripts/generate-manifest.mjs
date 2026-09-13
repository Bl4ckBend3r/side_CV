import { readdir, readFile, writeFile } from 'node:fs/promises';
import { basename, join } from 'node:path';

const jobsDir = new URL('../jobs/', import.meta.url);
const files = (await readdir(jobsDir)).filter(file => file.endsWith('.html')).sort();
const getMeta = (html, name) => html.match(new RegExp(`<meta\\s+name=["']${name}["']\\s+content=["']([^"']+)["']`, 'i'))?.[1];
const grouped = new Map();

for (const file of files) {
  const html = await readFile(new URL(file, jobsDir), 'utf8');
  const key = getMeta(html, 'cv-key') || basename(file, '.html').replace(/-en$/, '');
  const lang = getMeta(html, 'cv-lang') || (file.endsWith('-en.html') ? 'en' : 'pl');
  const profile = grouped.get(key) || { key, versions: {} };
  profile.versions[lang] = {
    title: getMeta(html, 'cv-title') || key.replaceAll('-', ' '),
    description: getMeta(html, 'cv-description') || 'Professional profile',
    path: `./jobs/${file}`
  };
  grouped.set(key, profile);
}

const profiles = [...grouped.values()]
  .filter(profile => profile.versions.pl && profile.versions.en)
  .sort((a, b) => (a.key === 'ogolne' ? -1 : b.key === 'ogolne' ? 1 : a.versions.pl.title.localeCompare(b.versions.pl.title, 'pl')));
if (profiles.length * 2 !== files.length) throw new Error('Każdy profil CV musi mieć dokładnie wersję PL i EN.');
await writeFile(join(new URL(jobsDir).pathname, 'manifest.json'), `${JSON.stringify(profiles, null, 2)}\n`);
console.log(`Wygenerowano ${profiles.length} profili CV w wersjach PL i EN.`);
