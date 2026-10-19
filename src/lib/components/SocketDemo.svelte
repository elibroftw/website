<script lang="ts">
  import { onMount, onDestroy } from 'svelte';

  const quotes = [
    'quote1',
    'quote2',
    'quote3',
    'The best way to predict the future is to invent it.',
    'Simplicity is the soul of efficiency.',
    'Make it work, make it right, make it fast.',
  ];

  let shown: string[] = [];
  let timer: ReturnType<typeof setTimeout>;
  let stopped = false;

  function nextQuote(): void {
    if (shown.length >= 10 || stopped) return;
    shown = [...shown, quotes[Math.floor(Math.random() * quotes.length)]];
    timer = setTimeout(nextQuote, 3000);
  }

  onMount(() => {
    timer = setTimeout(nextQuote, 0);
    return () => {
      stopped = true;
      clearTimeout(timer);
    };
  });

  onDestroy(() => clearTimeout(timer));
</script>

<h1>SocketIO Example</h1>
<p>A random quote will come up every 3 seconds until there are 10 quotes.</p>
<p style="font-size: 1rem; opacity: 0.8;">The original server-backed Socket.IO demo is available in the preserved Flask source.</p>
<ul id="quotes">
  {#each shown as quote}
    <li>{quote}</li>
  {/each}
</ul>

<style>
  li {
    font-family: Montserrat;
    font-size: 18px;
    color: white;
    padding-bottom: 0.5em;
    text-align: left;
  }
</style>