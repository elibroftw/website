<script lang="ts">
  import { onMount } from 'svelte';

  let time = '';
  let date = '';
  let timer: ReturnType<typeof setTimeout>;

  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December',
  ];
  const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  const endings: Record<number, string> = { 1: 'ˢᵗ', 2: 'ⁿᵈ', 3: 'ʳᵈ' };

  function update(): void {
    const now = new Date();
    const day = now.getDate();
    const ending = endings[day] || 'ᵗʰ';
    date = `${days[now.getDay()]} ${months[now.getMonth()]} ${day}<sup>${ending}</sup> ${now.getFullYear()}`;
    const seconds = now.getSeconds().toString().padStart(2, '0');
    const minutes = now.getMinutes().toString().padStart(2, '0');
    let hours = now.getHours();
    let ampm = 'pm';
    if (hours > 12) hours -= 12;
    else ampm = 'am';
    time = `${hours}:${minutes}:${seconds} ${ampm}`;
    timer = setTimeout(update, 1000);
  }

  onMount(() => {
    update();
    return () => clearTimeout(timer);
  });
</script>

<h1>{time}</h1>
<p id="date">{@html date}</p>