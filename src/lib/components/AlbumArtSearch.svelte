<script lang="ts">
  import { toolsApi } from '$lib/paths';
  import { readError } from '$lib/download';

  let artist = '';
  let track = '';
  let imageUrl = '';
  let altText = '';
  let loading = false;
  let error = '';

  async function submit(event: SubmitEvent): Promise<void> {
    event.preventDefault();
    imageUrl = '';
    error = '';
    loading = true;
    try {
      const params = new URLSearchParams({ artist, track });
      const response = await fetch(`${toolsApi('search-album-art/')}?${params}`);
      if (!response.ok) {
        error = await readError(response);
        return;
      }
      const data = await response.json();
      imageUrl = data.image_url;
      altText = data.alt_text;
    } catch {
      error = 'Could not reach the album art service.';
    } finally {
      loading = false;
    }
  }
</script>

<h1>Search Album Art</h1><br />
<form onsubmit={submit} style="margin-bottom: 1em">
  <input
    class="text-input"
    id="artist-input"
    type="text"
    name="artist"
    placeholder="Artist name"
    autofocus
    required
    bind:value={artist}
  />
  <input
    class="text-input"
    id="track-input"
    type="text"
    name="track"
    placeholder="Track title"
    required
    bind:value={track}
  />
  <button class="ui-btn submit-btn" id="search" type="submit" disabled={loading}>
    {loading ? 'Searching…' : 'Search'}
  </button>
</form>

{#if error}
  <p style="color: #ff8080">{error}</p>
{/if}

{#if imageUrl}
  <img id="album-cover" src={imageUrl} alt={altText} />
{/if}

<style>
  #album-cover {
    max-width: 500px;
    width: 100%;
  }

  @media screen and (max-width: 1024px) {
    #album-cover {
      max-width: 400px;
    }
  }

  @media screen and (max-width: 640px) {
    #album-cover {
      max-width: 300px;
    }
  }
</style>