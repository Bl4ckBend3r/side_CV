import { readdir, readFile, writeFile } from 'node:fs/promises';
import { basename, join } from 'node:path';

const jobsDir = new URL('../jobs/', import.meta.url);
const files = (await readdir(jobsDir)).filter(file => file.endsWith('.html')).sort();
const getMeta = (html, name) => html.match(new RegExp(`<meta\\s+name=["']${name}["']\\s+content=["']([^"']+)["']`, 'i'))?.[1];
const cvs = [];

for (const file of files) {
  const html = await readFile(new URL(file, jobsDir), 'utf8');
  const slug = getMeta(html, 'cv-slug') || basename(file, '.html');
  cvs.push({
    title: getMeta(html, 'cv-title') || slug.replaceAll('-', ' '),
    slug,
    description: getMeta(html, 'cv-description') || 'Profil zawodowy',
    path: `./jobs/${file}`
  });
}

cvs.sort((a, b) => (a.slug === 'ogolne' ? -1 : b.slug === 'ogolne' ? 1 : a.title.localeCompare(b.title, 'pl')));
await writeFile(join(new URL(jobsDir).pathname, 'manifest.json'), `${JSON.stringify(cvs, null, 2)}\n`);
console.log(`Wygenerowano manifest dla ${cvs.length} CV.`);
