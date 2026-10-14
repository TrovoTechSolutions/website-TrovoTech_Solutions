(() => {
  'use strict';
  const header = document.querySelector('.bp-header');
  if (!header) return;
  const navigation = header.querySelector('#site-navigation');
  const menuButton = header.querySelector('.nav-toggle');
  const products = header.querySelector('.bp-products');
  const productButton = header.querySelector('.bp-products-toggle');
  const panel = header.querySelector('#baylior-products-panel');
  const mobile = window.matchMedia('(max-width: 1023px)');
  const setProducts = open => {
    productButton.setAttribute('aria-expanded', String(open));
    panel.hidden = !open;
  };
  const setMenu = open => {
    navigation.classList.toggle('is-open', open);
    navigation.inert = mobile.matches && !open;
    menuButton.setAttribute('aria-expanded', String(open));
    menuButton.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
    menuButton.querySelector('span').textContent = open ? 'close' : 'menu';
    if (!open) setProducts(false);
  };
  productButton.addEventListener('click', () => setProducts(panel.hidden));
  menuButton.addEventListener('click', () => setMenu(menuButton.getAttribute('aria-expanded') !== 'true'));
  header.addEventListener('keydown', event => {
    if (event.key !== 'Escape') return;
    if (!panel.hidden) {
      event.preventDefault(); event.stopPropagation(); setProducts(false); productButton.focus();
    } else if (mobile.matches && navigation.classList.contains('is-open')) {
      event.preventDefault(); setMenu(false); menuButton.focus();
    }
  });
  document.addEventListener('click', event => {
    if (!products.contains(event.target)) setProducts(false);
    if (mobile.matches && !header.contains(event.target)) setMenu(false);
  });
  products.addEventListener('focusout', event => {
    if (!products.contains(event.relatedTarget)) setProducts(false);
  });
  navigation.querySelectorAll('a').forEach(link => link.addEventListener('click', () => {
    setMenu(false);
    // Closing the mobile disclosure must not leave focus inside inert content.
    if (mobile.matches) menuButton.focus();
  }));
  const reset = () => {
    const focusInNavigation = navigation.contains(document.activeElement);
    setMenu(false);
    if (mobile.matches && focusInNavigation) menuButton.focus();
  };
  if (mobile.addEventListener) mobile.addEventListener('change', reset);
  else mobile.addListener(reset);
  reset();
})();
