/* ==========================================================================
   Trovo Tech Solutions — Product Landing Page Navigation & Header Sizing
   - Measures fixed navbar height and publishes CSS variables
   - Highlights active sub-header section links during scroll
   - Supports keyboard accessibility
   ========================================================================== */
(() => {
  'use strict';

  // 1. Header height measurement
  const navbar = document.querySelector('.navbar');
  const measureHeader = () => {
    if (!navbar) return;
    const h = `${Math.ceil(navbar.getBoundingClientRect().height)}px`;
    document.documentElement.style.setProperty('--product-site-header-height', h);
    document.documentElement.style.setProperty('--baylior-header-height', h);
  };

  if (navbar) {
    measureHeader();
    if ('ResizeObserver' in window) {
      new ResizeObserver(measureHeader).observe(navbar);
    } else {
      window.addEventListener('resize', measureHeader);
    }
  }

  // 2. Active section link highlighting on scroll
  const navLinks = document.querySelectorAll('.b-product-nav .b-nav-links a[href^="#"]');
  if (!navLinks.length) return;

  const targets = [];
  navLinks.forEach(link => {
    const id = link.getAttribute('href').slice(1);
    const target = document.getElementById(id);
    if (target) targets.push({ id, link, target });
  });

  if (!targets.length) return;

  const onScroll = () => {
    const scrollPos = window.scrollY + 200;
    let currentId = '';

    for (let i = 0; i < targets.length; i++) {
      const top = targets[i].target.offsetTop;
      if (scrollPos >= top) {
        currentId = targets[i].id;
      }
    }

    targets.forEach(({ id, link }) => {
      const isActive = id === currentId;
      link.classList.toggle('is-active', isActive);
      if (isActive) {
        link.setAttribute('aria-current', 'true');
      } else {
        link.removeAttribute('aria-current');
      }
    });
  };

  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
})();
