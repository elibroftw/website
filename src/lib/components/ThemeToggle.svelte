<script lang="ts">
  import { onMount } from 'svelte';

  export let lightCss: string;
  export let darkCss: string;

  let checked = false;

  function getCookie(name: string): string | null {
    const prefix = `${name}=`;
    for (let part of document.cookie.split(';')) {
      part = part.trim();
      if (part.startsWith(prefix)) return decodeURIComponent(part.slice(prefix.length));
    }
    return null;
  }

  function setCookie(name: string, value: string): void {
    const expires = new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toUTCString();
    document.cookie = `${name}=${encodeURIComponent(value)}; expires=${expires}; path=/; SameSite=Lax`;
  }

  function applyTheme(dark: boolean, persist = true): void {
    const stylesheet = document.getElementById('style-theme');
    stylesheet?.setAttribute('href', dark ? darkCss : lightCss);
    document.documentElement.classList.toggle('dark', dark);
    if (persist) {
      localStorage.setItem('theme', String(dark));
      setCookie('theme', String(dark));
    }
  }

  onMount(() => {
    const stored = localStorage.getItem('theme');
    checked = stored !== null ? stored === 'true' : getCookie('theme') === 'true';
    applyTheme(checked, false);
  });

  function toggle(): void {
    applyTheme(checked);
  }
</script>

<span id="switch-text" class="noselect">Toggle Theme</span>
<label class="switch">
  <input id="theme-toggle" type="checkbox" bind:checked={checked} onchange={toggle} />
  <span class="slider round"></span>
</label>