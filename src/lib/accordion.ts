export interface AccordionOptions {
  /** Open today's accordion when there is no valid hash (used by the pool schedule). */
  openToday?: boolean;
}

function toggleAccordion(accordion: HTMLElement): void {
  accordion.classList.toggle('active');
  const panel = accordion.nextElementSibling as HTMLElement | null;
  if (!panel) return;
  if (panel.style.maxHeight) {
    panel.style.maxHeight = '';
  } else {
    panel.style.maxHeight = `${panel.scrollHeight * 1.25}px`;
  }
}

/** Wire up the Flask-era .accordion/.panel markup. */
export function initAccordions(options: AccordionOptions = {}): void {
  const accordions = Array.from(document.getElementsByClassName('accordion')) as HTMLElement[];
  for (const accordion of accordions) {
    accordion.addEventListener('click', () => {
      toggleAccordion(accordion);
      const open = accordions.filter((item) => item.classList.contains('active')).map((item) => item.id);
      const suffix = open.length ? `#${open[open.length - 1]}` : '';
      history.replaceState({}, document.title, window.location.pathname + suffix);
    });
  }

  const onReady = () => {
    const hash = window.location.hash;
    if (hash) {
      const target = document.getElementById(hash.slice(1));
      if (target?.classList.contains('accordion')) {
        target.click();
        return;
      }
    }
    if (options.openToday) {
      const day = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'][
        new Date().getDay()
      ];
      document.getElementById(day)?.click();
    }
  };

  if (document.readyState === 'loading') {
    window.addEventListener('DOMContentLoaded', onReady, { once: true });
  } else {
    onReady();
  }
}