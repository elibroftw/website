<script lang="ts">
  import { toolsApi } from '$lib/paths';
  import { downloadBlob, readError, responseFilename } from '$lib/download';

  let fileInput: HTMLInputElement;
  let file: File | null = null;
  let template = '';
  let highlighting = false;
  let loading = false;
  let error = '';

  function pick(files: FileList | null): void {
    file = files?.[0] || null;
    if (file && !file.name.toLowerCase().endsWith('.pdf')) {
      file = null;
      if (fileInput) fileInput.value = '';
      error = 'Please select a PDF file.';
    } else {
      error = '';
    }
  }

  function drop(event: DragEvent): void {
    event.preventDefault();
    highlighting = false;
    const files = event.dataTransfer?.files;
    if (!files?.length) return;
    if (fileInput) fileInput.files = files;
    pick(files);
  }

  async function submit(event: SubmitEvent): Promise<void> {
    event.preventDefault();
    if (!file) {
      error = 'Please select a PDF file.';
      return;
    }
    error = '';
    loading = true;
    const formData = new FormData();
    formData.append('file', file);
    formData.append('template', template);
    try {
      const response = await fetch(toolsApi('pdf/split/'), { method: 'POST', body: formData });
      if (!response.ok) {
        error = await readError(response);
        return;
      }
      const filename = responseFilename(response, `${file.name.replace(/\.pdf$/i, '')}.zip`);
      downloadBlob(await response.blob(), filename);
    } catch {
      error = 'Could not reach the PDF service.';
    } finally {
      loading = false;
    }
  }
</script>

<h1>PDF Splitter</h1>
<br />
<div
  id="drop-area"
  class:highlight={highlighting}
  ondragover={(event) => { event.preventDefault(); highlighting = true; }}
  ondragleave={() => (highlighting = false)}
  ondrop={drop}
>
  <form class="my-form" onsubmit={submit} enctype="multipart/form-data">
    <p>Upload PDF via drag and drop or button</p>
    <input type="text" name="template" placeholder={'template{i}.pdf'} bind:value={template} />
    <input
      name="file"
      required
      type="file"
      id="fileElem"
      accept=".pdf"
      bind:this={fileInput}
      onchange={() => pick(fileInput.files)}
    />
    <label class="button" for="fileElem">Select PDF</label>
    <p class="file-name" style="margin-top: 3%;">{file?.name || ''}</p>
    <button type="submit" disabled={loading}>{loading ? 'Splitting…' : 'Split PDF and Download'}</button>
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