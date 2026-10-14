/* Product-page header sizing. Shared signup configuration is in /js/baylior-destinations.js. */
(() => {
  'use strict';
  const navbar = document.querySelector('.navbar');
  const measureHeader = () => document.documentElement.style.setProperty('--baylior-header-height', `${Math.ceil(navbar.getBoundingClientRect().height)}px`);
  if (navbar) {
    measureHeader();
    if ('ResizeObserver' in window) new ResizeObserver(measureHeader).observe(navbar);
    else window.addEventListener('resize', measureHeader);
  }
})();
