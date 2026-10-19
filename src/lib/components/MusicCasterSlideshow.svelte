<script lang="ts">
  export let images: Array<[string, string]>;

  let index = 0;

  function showSlide(next: number): void {
    index = (next + images.length) % images.length;
  }
</script>

<div class="imagesContainer">
  {#each images as image, i}
    <div class="slide" style:display={i === index ? 'block' : 'none'}>
      <div class="numbertext">{i + 1} / {images.length}</div>
      <img src={image[0]} alt={image[1]} />
    </div>
  {/each}
  <a class="prev" onclick={() => showSlide(index - 1)} aria-label="Previous screenshot">❮</a>
  <a class="next" onclick={() => showSlide(index + 1)} aria-label="Next screenshot">❯</a>
  <div class="caption-container"><p id="caption">{images[index]?.[1] || ''}</p></div>
  <div class="row">
    {#each images as image, i}
      <div class="column">
        <img
          class="preview"
          class:active={i === index}
          src={image[0]}
          onclick={() => showSlide(i)}
          alt={image[1]}
          title={image[1]}
        />
      </div>
    {/each}
  </div>
</div>

<style>
  img {
    vertical-align: middle;
  }

  .imagesContainer {
    position: relative;
    margin-top: 1em;
  }

  .slide img {
    border-radius: 0.5em;
    max-width: 100%;
    max-height: 400px;
  }

  .prev,
  .next {
    cursor: pointer;
    position: absolute;
    top: 37%;
    background-color: rgba(0, 0, 0, 0.2);
    width: auto;
    padding: 16px;
    margin-top: -50px;
    color: white;
    font-weight: bold;
    font-size: 20px;
    border-radius: 0 3px 3px 0;
    user-select: none;
    -webkit-user-select: none;
  }

  .next {
    right: 0;
    border-radius: 3px 0 0 3px;
  }

  .prev {
    left: -5px;
  }

  .prev:hover,
  .next:hover {
    background-color: rgba(0, 0, 0, 0.8);
  }

  .numbertext {
    color: #f2f2f2;
    background-color: rgba(0, 0, 0, 0.7);
    border-radius: 0 0.5em 0 0.5em;
    font-size: 12px;
    padding: 4px 6px;
    position: absolute;
    top: 0;
    right: 0;
    font-family: Manrope;
  }

  .caption-container {
    text-align: center;
    padding: 2px 16px;
    color: white;
  }

  #caption {
    padding: 2px 16px;
    margin-top: 10px;
  }

  .row {
    display: flex;
    flex-direction: row;
  }

  .column {
    width: calc(100% / 4);
  }

  .preview {
    opacity: 0.6;
    cursor: pointer;
    max-width: 100%;
    max-height: 10em;
  }

  .preview.active,
  .preview:hover {
    opacity: 1;
  }
</style>