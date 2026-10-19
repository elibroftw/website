<script lang="ts">
  import { onDestroy } from 'svelte';
  import { toolsApi } from '$lib/paths';
  import { readError } from '$lib/download';

  let text = '';
  let logoInput: HTMLInputElement;
  let imageUrl = '';
  let loading = false;
  let error = '';

  function revoke(): void {
    if (imageUrl) URL.revokeObjectURL(imageUrl);
    imageUrl = '';
  }

  async function submit(event: SubmitEvent): Promise<void> {
    event.preventDefault();
    error = '';
    revoke();
    const formData = new FormData();
    formData.append('text', text);
    const logo = logoInput?.files?.[0];
    if (logo) formData.append('logo', logo);

    loading = true;
    try {
      const response = await fetch(toolsApi('qr-code/'), { method: 'POST', body: formData });
      if (!response.ok) {
        error = await readError(response);
        return;
      }
      imageUrl = URL.createObjectURL(await response.blob());
    } catch {
      error = 'Could not reach the QR code service.';
    } finally {
      loading = false;
    }
  }

  onDestroy(revoke);
</script>

<h1>QR Code Generator</h1><br />
<form onsubmit={submit} style="margin-bottom: 1em" enctype="multipart/form-data">
  <input
    class="text-input"
    style="padding: 0.35em 1.2em;"
    id="text"
    type="text"
    name="text"
    placeholder="Text to encode"
    autofocus
    required
    bind:value={text}
  />
  <input id="fileElem" type="file" name="logo" accept="image/*" bind:this={logoInput} />
  <label class="button" for="fileElem">Upload Logo (optional)</label>
  <button class="ui-btn submit-btn" type="submit" disabled={loading}>
    {loading ? 'Generating…' : 'Generate QR Code'}
  </button>
</form>

{#if error}
  <p style="color: #ff8080">{error}</p>
{/if}

{#if imageUrl}
  <div>
    <a class="button" style="text-decoration: none;" download="qr-code.png" href={imageUrl}>
      <i class="fa fa-download"></i> Download
    </a>
    <br /><br />
    <img id="album-cover" download="qr-code.png" src={imageUrl} alt="your QR code" />
  </div>
{/if}

<style>
  #fileElem {
    display: none;
  }
</style>