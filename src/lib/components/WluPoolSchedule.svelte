<script lang="ts">
  import { onMount } from 'svelte';
  import { toolsApi } from '$lib/paths';

  let schedule: Record<string, string[]> | null = null;
  let openDay = '';
  let error = '';

  function toggle(day: string): void {
    openDay = openDay === day ? '' : day;
    history.replaceState({}, document.title, window.location.pathname + (openDay ? `#${day.toLowerCase()}` : ''));
  }

  onMount(async () => {
    try {
      const response = await fetch(toolsApi('wlu-pool/'));
      if (!response.ok) throw new Error('failed');
      schedule = await response.json();
      const hash = window.location.hash.slice(1).toLowerCase();
      const today = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'][new Date().getDay()];
      const requested = Array.from(document.querySelectorAll('.accordion')).find(
        (element) => element.id === hash,
      );
      openDay = requested?.id || today;
    } catch {
      error = 'Something went awfully wrong. Please send me an email.';
    }
  });
</script>

<h1>WLU Pool Schedule</h1>
<br />

{#if error}
  <p style="color: white;">{error}</p>
{:else if !schedule}
  <p>Loading schedule…</p>
{:else}
  {#each Object.entries(schedule) as [day, times]}
    <button class="accordion" class:active={openDay === day.toLowerCase()} id={day.toLowerCase()} onclick={() => toggle(day)}>
      {day}
    </button>
    <div class="panel" style:max-height={openDay === day.toLowerCase() ? '1000px' : null}>
      <p id="panel-text">
        {#each times as time, i}{time}{#if i < times.length - 1}<br />{/if}{/each}
      </p>
    </div>
  {/each}
{/if}