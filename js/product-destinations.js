/* ==========================================================================
   Trovo Tech Solutions — Product Destinations Routing
   Maps sign-up and pricing buttons to verified platform destinations.
   Security rules:
   - Valid origin must use https: (or localhost/127.0.0.1 for local testing)
   - Must have root pathname '/', no query parameters, no hash fragments,
     and no credentials in the origin.
   - When integrationVerified is false or origin is invalid, buttons keep
     their clearly labelled in-page preview targets.
   ========================================================================== */
(() => {
  'use strict';

  const destinations = Object.freeze({
    integrationVerified: false,
    signupOrigin: ''
  });

  let origin;
  try {
    const candidate = new URL(destinations.signupOrigin);
    const isHttps = candidate.protocol === 'https:';
    const isLocalhost = (candidate.protocol === 'http:' || candidate.protocol === 'https:') &&
      (candidate.hostname === 'localhost' || candidate.hostname === '127.0.0.1');

    if (destinations.integrationVerified &&
        (isHttps || isLocalhost) &&
        candidate.pathname === '/' &&
        !candidate.search &&
        !candidate.hash &&
        !candidate.username &&
        !candidate.password) {
      origin = candidate.origin;
    }
  } catch {
    /* Keep clearly labelled preview destinations. */
  }

  if (!origin) return;

  if (typeof document !== 'undefined' && document.body && document.body.classList) {
    document.body.classList.add('b-live');
  }

  document.querySelectorAll('[data-destination], [data-baylior-destination]').forEach(link => {
    const kind = link.dataset.destination || link.dataset.bayliorDestination;
    if (kind !== 'signup' && kind !== 'pricing') return;

    const product = link.dataset.product || 'carspa';
    const route = kind === 'signup' ? `/signup/${product}` : `/pricing/${product}`;
    link.href = origin + route;

    link.querySelectorAll('.bp-placeholder, .b-placeholder').forEach(label => {
      label.hidden = true;
      label.style.display = 'none';
    });
  });
})();
