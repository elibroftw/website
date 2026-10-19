<script lang="ts">
  import { withBase } from '$lib/paths';

  export let address: string;

  let snackbar = '';

  async function copyText(): Promise<void> {
    try {
      await navigator.clipboard.writeText(address);
    } catch {
      const textarea = document.createElement('textarea');
      textarea.value = address;
      textarea.setAttribute('readonly', '');
      textarea.style.position = 'absolute';
      textarea.style.left = '-9999px';
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      textarea.remove();
    }
    snackbar = 'show';
    setTimeout(() => (snackbar = ''), 2400);
  }
</script>

<h2 id="donation">Donation</h2>
<p><a class="link" href="https://www.paypal.me/elibroftw">PayPal</a></p>
<p>
  <a
    class="link"
    id="monero-address"
    onclick={copyText}
    href={`monero:${address}`}
    title={address}
  >
    <span class="tooltiptext">Click to copy</span>
    <span id="qr-code"><img src={withBase('/static/images/monero.png')} alt="Monero address QR code" /></span>
  </a>
</p>

<div id="snackbar" class={snackbar}>Monero address copied!</div>

<style>
  .link {
    font-size: 1.3em;
  }

  :global(#monero-address) {
    cursor: copy;
  }

  :global(#monero-address > #qr-code) {
    display: none;
    padding-top: 1em;
  }

  :global(#monero-address:hover > #qr-code) {
    display: block;
  }

  :global(#monero-address .tooltiptext) {
    visibility: hidden;
    width: 140px;
    background-color: black;
    color: #fff;
    margin-left: 10px;
    text-align: center;
    border-radius: 6px;
    font-size: 20px;
    padding: 2px 0;
    position: absolute;
    z-index: 1;
  }

  :global(#monero-address::before) {
    content: 'Monero Address';
  }

  :global(#monero-address:hover .tooltiptext) {
    visibility: visible;
  }

  @media screen and (max-width: 640px) {
    .tooltiptext {
      display: none;
    }

    :global(#monero-address > #qr-code) {
      display: block;
    }
  }

  :global(h2) {
    font-size: xx-large;
  }
</style>