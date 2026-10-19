/// <reference types="astro/client" />

interface ImportMetaEnv {
  readonly PUBLIC_TOOLS_API_BASE?: string;
  readonly PUBLIC_GOOGLE_MAPS_API_KEY?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}