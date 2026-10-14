/* Phase 2 stays local. A URL alone cannot enable live actions: release review must also enable integration. */
(() => {
  'use strict';
  const navbar = document.querySelector('.navbar');
  const measureHeader = () => document.documentElement.style.setProperty('--baylior-header-height', `${Math.ceil(navbar.getBoundingClientRect().height)}px`);
  if (navbar) {
    measureHeader();
    if ('ResizeObserver' in window) new ResizeObserver(measureHeader).observe(navbar);
    else window.addEventListener('resize', measureHeader);
  }
  const destinations = Object.freeze({ integrationVerified: false, signupOrigin: '' });
  let origin;
  try {
    const candidate = new URL(destinations.signupOrigin);
    if (destinations.integrationVerified && candidate.protocol === 'https:' && candidate.pathname === '/' && !candidate.search && !candidate.hash && !candidate.username && !candidate.password) origin = candidate.origin;
  } catch { /* Empty configuration intentionally leaves inert, labelled preview links. */ }
  if (!origin) return;
  document.querySelectorAll('[data-destination]').forEach(link => {
    link.href = origin + (link.dataset.destination === 'signup' ? '/signup' : '/');
    link.classList.add('b-live');
  });
})();
