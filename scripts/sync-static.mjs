// Keep the Flask-era `static/` directory as the single source of truth while
// Astro serves it from `public/static`. The copied directory is git-ignored.
import { cp, mkdir, rm } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const source = resolve(root, 'static');
const destination = resolve(root, 'public/static');

if (!existsSync(source)) {
  console.warn(`[sync-static] ${source} does not exist, skipping`);
  process.exit(0);
}

await mkdir(dirname(destination), { recursive: true });
await rm(destination, { recursive: true, force: true });
await cp(source, destination, { recursive: true });
console.log('[sync-static] copied static/ -> public/static/');