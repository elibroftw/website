<script lang="ts">
  import { toolsApi } from '$lib/paths';
  import { downloadBlob, readError, responseFilename } from '$lib/download';

  let fileInput: HTMLInputElement;
  let files: File[] = [];
  let newName = '';
  let highlighting = false;
  let loading = false;
  let error = '';

  function pick(list: FileList | null): void {
    files = list ? Array.from(list).filter((file) => file.name.toLowerCase().endsWith('.pdf')) : [];
    if (list?.length && files.length !== list.length) {
      error = 'Only PDF files are supported.';
    } else {
      error = '';
    }
  }

  function drop(event: DragEvent): void {
    event.preventDefault();
    highlighting = false;
    const dropped = event.dataTransfer?.files;
    if (!dropped?.length) return;
    if (fileInput) fileInput.files = dropped;
    pick(dropped);
  }

  async function submit(event: SubmitEvent): Promise<void> {
    event.preventDefault();
    if (!files.length) {
      error = 'Please select at least one PDF file.';
      return;
    }
    error = '';
    loading = true;
    const formData = new FormData();
    for (const file of files) formData.append('files', file);
    formData.append('new-name', newName);
    try {
      const response = await fetch(toolsApi('pdf/combine/'), { method: 'POST', body: formData });
      if (!response.ok) {
        error = await readError(response);
        return;
      }
      const fallback = files[0].name.replace(/\.pdf$/i, '') + '_combined.pdf';
      downloadBlob(await response.blob(), responseFilename(response, fallback));
    } catch {
      error = 'Could not reach the PDF service.';
    } finally {
      loading = false;
    }
  }
</script>

<h1>PDF Combiner</h1>
<br />
<div
  id="drop-area"
  class:highlight={highlighting}
  ondragover={(event) => { event.preventDefault(); highlighting = true; }}
  ondragleave={() => (highlighting = false)}
  ondrop={drop}
>
  <form class="my-form" onsubmit={submit} enctype="multipart/form-data">
    <p>Upload PDFs via drag and drop or button</p>
    <input type="text" name="new-name" placeholder="new file name" bind:value={newName} />
    <input
      name="files"
      multiple
      required
      type="file"
      id="fileElem"
      accept=".pdf"
      bind:this={fileInput}
      onchange={() => pick(fileInput.files)}
    />
    <label class="button" for="fileElem">Select PDFs</label>
    <p class="file-name" style="margin-top: 3%;">{files.map((file) => file.name).join(', ')}</p>
    <button type="submit" disabled={loading}>{loading ? 'Combining…' : 'Combine PDFs and Download'}</button>
  </form>
</div>

{#if error}
  <p style="color: #ff8080">{error}</p>
{/if}

<style>
  #drop-area {
    border: 2px solid #ccc;
    border-radius: 20px;
    width: min(480px, 90vw);
    font-family: sans-serif;
    margin: auto;
    padding: 20px;
  }

  #drop-area.highlight {
    border-color: lightskyblue;
  }

  p {
    margin-top: 0;
  }

  .my-form {
    margin-bottom: 10px;
  }

  .button {
    display: inline-block;
    font-family: Montserrat;
    font-weight: 100;
    padding: 10px;
    background: -webkit-linear-gradient(45deg, rgba(30, 143, 255, 0.9), rgba(0, 128, 0, 0.9));
    color: #eeeeee;
    border: none;
    cursor: pointer;
    border-radius: 5px;
  }

  .button:hover {
    background: linear-gradient(45deg, dodgerBlue, purple);
  }

  #fileElem {
    display: none;
  }
</style>