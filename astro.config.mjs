import { defineConfig } from 'astro/config';
import svelte from '@astrojs/svelte';
import tailwindcss from '@tailwindcss/vite';

// GitHub Pages project sites live under /<repo>/. Custom domains (the default
// for elijahlopez.ca) use /. Set BASE_PATH when deploying without a CNAME.
const base = process.env.BASE_PATH || '/';

export default defineConfig({
  site: process.env.SITE_URL || 'https://elijahlopez.ca',
  base,
  trailingSlash: 'always',
  output: 'static',
  integrations: [svelte()],
  vite: {
    plugins: [tailwindcss()],
    resolve: {
      alias: {
        $lib: new URL('./src/lib', import.meta.url).pathname,
      },
    },
  },
  redirects: {
    '/formula-calculator/': 'https://repl.it/@elilopez/formulas',
    '/repls/': 'https://repl.it/@elilopez/formulas',
    '/programs/': 'https://repl.it/@elilopez/formulas',
    '/shift/': 'https://elijahlopez.itch.io/shift',
    '/metadata-setter/': 'https://github.com/elibroftw/music-caster/',
  },
});