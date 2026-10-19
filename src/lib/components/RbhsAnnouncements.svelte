<script lang="ts">
  import { onMount } from 'svelte';
  import { toolsApi } from '$lib/paths';

  let announcements: string[][] = [];
  let loaded = false;
  let error = '';

  function toggle(event: MouseEvent & { currentTarget: HTMLButtonElement }): void {
    const accordion = event.currentTarget;
    accordion.classList.toggle('active');
    const panel = accordion.nextElementSibling as HTMLElement | null;
    if (!panel) return;
    panel.style.maxHeight = panel.style.maxHeight ? '' : `${panel.scrollHeight}px`;
    const open = Array.from(document.querySelectorAll('.accordion.active')).map((item) => item.id);
    history.replaceState({}, document.title, window.location.pathname + (open.length ? `#${open[open.length - 1]}` : ''));
  }

  onMount(async () => {
    try {
      const response = await fetch(toolsApi('announcements/'));
      if (!response.ok) throw new Error('failed');
      announcements = await response.json();
    } catch {
      error = 'Could not load announcements right now.';
    } finally {
      loaded = true;
      const hash = window.location.hash.slice(1);
      if (hash) {
        const target = document.getElementById(hash);
        if (target?.classList.contains('accordion')) target.click();
      }
    }
  });
</script>

<h1>Announcements</h1>

{#if !loaded}
  <p>Loading announcements…</p>
{:else if error}
  <p style="color: white;">{error}</p>
{:else if announcements.length === 0}
  <p style="color: white;">There are no announcements for today</p>
{:else}
  {#each announcements as announcement, i}
    <button class="accordion" id={`no.${i + 1}`} onclick={toggle}>{announcement[0]}</button>
    <div class="panel"><p id="panel-text">{@html announcement[1]}</p></div>
  {/each}
{/if}

<style>
  @media screen and (max-width: 1460px) {
    :global(h1) {
      font-size: 40px;
    }
  }

  @media screen and (max-width: 640px) {
    :global(h1) {
      font-size: 25px;
      letter-spacing: 5px;
    }
  }
</style>