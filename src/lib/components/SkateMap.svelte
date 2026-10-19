<script lang="ts">
  import { onMount } from 'svelte';
  import type { SkateLocation } from '$lib/skate';

  export let locations: SkateLocation[] = [];
  export let apiKey = '';

  let status = '';

  const TORONTO = { lat: 43.7001, lng: -79.4163 };
  const PIN_COLORS: Record<string, string> = { Outdoor: 'green', Indoor: 'blue', Trails: 'orange' };
  const pinIcon = (color: string) => `https://maps.google.com/mapfiles/ms/icons/${color}-dot.png`;

  function loadGoogleMaps(key: string): Promise<any> {
    const existing = (window as any).google?.maps;
    if (existing) return Promise.resolve(existing);
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = `https://maps.googleapis.com/maps/api/js?key=${encodeURIComponent(key)}`;
      script.async = true;
      script.onload = () => resolve((window as any).google.maps);
      script.onerror = () => reject(new Error('Could not load Google Maps'));
      document.head.appendChild(script);
    });
  }

  onMount(async () => {
    if (!apiKey) return;
    let maps: any;
    try {
      maps = await loadGoogleMaps(apiKey);
    } catch {
      status = 'Could not load Google Maps.';
      return;
    }

    const map = new maps.Map(document.getElementById('map'), { center: TORONTO, zoom: 11 });
    const geocoder = new maps.Geocoder();
    const infoWindow = new maps.InfoWindow();
    let userMarker: any;

    function geocodeCached(address: string): Promise<{ lat: number; lng: number } | null> {
      const cacheKey = `skate-geo:${address}`;
      const cached = localStorage.getItem(cacheKey);
      if (cached) return Promise.resolve(JSON.parse(cached));
      return new Promise((resolve) => {
        geocoder.geocode({ address: `${address}, Toronto, ON, Canada` }, (results: any[], geocodeStatus: string) => {
          if (geocodeStatus === 'OK' && results[0]) {
            const location = results[0].geometry.location;
            const coords = { lat: location.lat(), lng: location.lng() };
            localStorage.setItem(cacheKey, JSON.stringify(coords));
            resolve(coords);
          } else if (geocodeStatus === 'OVER_QUERY_LIMIT') {
            setTimeout(() => geocodeCached(address).then(resolve), 1500);
          } else {
            console.warn('Geocode failed for', address, geocodeStatus);
            resolve(null);
          }
        });
      });
    }

    function addMarker(location: SkateLocation, coords: { lat: number; lng: number }, bounds: any): void {
      const marker = new maps.Marker({
        position: coords,
        map,
        title: location.name,
        icon: pinIcon(PIN_COLORS[location.category] || 'red'),
      });
      const directions =
        'https://www.google.com/maps/dir/?api=1&destination=' +
        encodeURIComponent(`${location.address}, Toronto, ON`);
      const html =
        `<div class="gm-info-title">${location.name}</div>` +
        `<div class="gm-info-body">${location.category}<br>${location.address}<br>` +
        `<a href="${directions}" target="_blank" rel="noopener">Directions →</a></div>`;
      marker.addListener('click', () => {
        infoWindow.setContent(html);
        infoWindow.open(map, marker);
      });
      bounds.extend(coords);
    }

    const bounds = new maps.LatLngBounds();
    let placed = 0;
    status = 'Loading spots…';
    for (const location of locations) {
      const coords = await geocodeCached(location.address);
      if (coords) {
        addMarker(location, coords, bounds);
        placed += 1;
      }
    }
    if (placed > 0) map.fitBounds(bounds);
    status = `Showing ${placed} of ${locations.length} spots.`;

    document.getElementById('locate-btn')?.addEventListener('click', () => {
      if (!navigator.geolocation) {
        status = 'Geolocation is not supported by your browser.';
        return;
      }
      status = 'Locating you…';
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const here = { lat: position.coords.latitude, lng: position.coords.longitude };
          if (userMarker) userMarker.setMap(null);
          userMarker = new maps.Marker({
            position: here,
            map,
            title: 'You are here',
            icon: pinIcon('red'),
            zIndex: 9999,
            animation: maps.Animation.DROP,
          });
          map.setCenter(here);
          map.setZoom(13);
          status = 'Centred on your location.';
        },
        (geoError) => {
          status = `Could not get your location: ${geoError.message}`;
        },
      );
    });
  });
</script>

<div class="map-controls">
  {#if apiKey}
    <button id="locate-btn" class="locate-btn" type="button">📍 Find me</button>
  {/if}
  <div class="legend">
    <span class="legend-item"><span class="legend-dot outdoor"></span> Outdoor ({locations.filter((item) => item.category === 'Outdoor').length})</span>
    <span class="legend-item"><span class="legend-dot indoor"></span> Indoor ({locations.filter((item) => item.category === 'Indoor').length})</span>
    <span class="legend-item"><span class="legend-dot trails"></span> Trails / BMX ({locations.filter((item) => item.category === 'Trails').length})</span>
  </div>
</div>

{#if !apiKey}
  <div id="map" class="missing">
    <p style="padding: 1em">
      ⚠️ The map needs a Google Maps API key. Set <code>PUBLIC_GOOGLE_MAPS_API_KEY</code> at build time to enable it.
    </p>
  </div>
{:else}
  <div id="map"></div>
{/if}
<div id="map-status">{status}</div>

<style>
  #map {
    width: 100%;
    height: 70vh;
    min-height: 420px;
    border-radius: 8px;
    margin-top: 1em;
  }

  #map.missing {
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(0, 0, 0, 0.35);
  }

  #map-status {
    margin-top: 0.5em;
    opacity: 0.8;
    font-size: 0.9em;
  }

  .map-controls {
    display: flex;
    flex-wrap: wrap;
    gap: 1.5em;
    align-items: center;
    margin-top: 1em;
  }

  .legend {
    display: flex;
    flex-wrap: wrap;
    gap: 1em;
    align-items: center;
  }

  .legend-item {
    display: inline-flex;
    align-items: center;
    gap: 0.4em;
    white-space: nowrap;
  }

  .legend-dot {
    width: 14px;
    height: 14px;
    border-radius: 50%;
    display: inline-block;
    border: 1px solid rgba(0, 0, 0, 0.3);
  }

  .legend-dot.outdoor { background: #2ecc40; }
  .legend-dot.indoor { background: #0074d9; }
  .legend-dot.trails { background: #ff851b; }

  .locate-btn {
    font-family: Montserrat;
    font-weight: 100;
    padding: 8px 16px;
    background: -webkit-linear-gradient(45deg, rgba(30, 143, 255, 0.9), rgba(0, 128, 0, 0.9));
    color: #eeeeee;
    border: none;
    cursor: pointer;
    border-radius: 5px;
  }

  .locate-btn:hover {
    background: linear-gradient(45deg, dodgerBlue, purple);
  }

  :global(.gm-info-title) { font-weight: bold; margin-bottom: 2px; }
  :global(.gm-info-body) { color: #333; }
  :global(.gm-info-body a) { color: #0074d9; }
</style>