const rawBase = import.meta.env.BASE_URL || '/';
const base = rawBase.endsWith('/') ? rawBase : `${rawBase}/`;

/** Prefix a root-relative path with Astro's configured base path. */
export function withBase(path: string): string {
  if (/^(?:[a-z]+:)?\/\//i.test(path) || path.startsWith('mailto:') || path.startsWith('tel:')) {
    return path;
  }
  return `${base}${path.replace(/^\/+/, '')}`;
}

/** Build an absolute URL for the lenerva.com API. Local dev also defaults to production. */
export function toolsApi(path: string): string {
  const apiBase = (import.meta.env.PUBLIC_TOOLS_API_BASE || 'https://lenerva.com').replace(/\/+$/, '');
  return `${apiBase}/api/${path.replace(/^\/+/, '')}`;
}

export { base };