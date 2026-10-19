import { readFileSync } from 'node:fs';

export const prerender = true;

export function GET(): Response {
  const key = readFileSync(new URL('../../static/elijahllopezz@gmail.com.gpg', import.meta.url), 'utf-8');
  return new Response(key, {
    headers: {
      'Content-Type': 'text/plain; charset=utf-8',
      'Cache-Control': 'public, max-age=86400',
    },
  });
}