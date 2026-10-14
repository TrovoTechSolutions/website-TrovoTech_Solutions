/* Phase 5 integration: a hostname alone does not enable live signup. */
(() => {
  'use strict';
  const destinations = Object.freeze({ integrationVerified: false, signupOrigin: '' });
  let origin;
  try {
    const candidate = new URL(destinations.signupOrigin);
    if (destinations.integrationVerified && candidate.protocol === 'https:' && candidate.pathname === '/' && !candidate.search && !candidate.hash && !candidate.username && !candidate.password) origin = candidate.origin;
  } catch { /* Keep clearly labelled local-preview destinations. */ }
  if (!origin) return;
  document.querySelectorAll('[data-baylior-destination], [data-destination]').forEach(link => {
    const kind = link.dataset.bayliorDestination || link.dataset.destination;
    if (kind !== 'signup' && kind !== 'pricing') return;
    link.href = origin + (kind === 'signup' ? '/signup' : '/');
    link.querySelectorAll('.bp-placeholder, .b-placeholder').forEach(label => { label.hidden = true; });
  });
})();
