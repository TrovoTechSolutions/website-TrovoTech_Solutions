/* ==========================================================================
   Trovo Tech Solutions — site navigation (phone/tablet drawer)
   Below 1024px the links slide in from the right. Closed links are inert so
   keyboard users cannot tab into an off-screen drawer.
   ========================================================================== */
(function () {
  "use strict";

  var header = document.querySelector(".site-header");
  if (!header) return;
  var navigation = header.querySelector("#site-navigation");
  var toggle = header.querySelector(".nav-toggle");
  if (!navigation || !toggle) return;
  var icon = toggle.querySelector(".material-symbols-outlined");
  var drawer = window.matchMedia("(max-width: 1023px)");

  function isOpen() {
    return toggle.getAttribute("aria-expanded") === "true";
  }

  function setOpen(open) {
    navigation.classList.toggle("is-open", open);
    navigation.inert = drawer.matches && !open;
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    if (icon) icon.textContent = open ? "close" : "menu";
  }

  toggle.addEventListener("click", function () {
    setOpen(!isOpen());
  });

  // Escape closes the drawer and returns focus to the menu button.
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && drawer.matches && isOpen()) {
      setOpen(false);
      toggle.focus();
    }
  });

  // A click outside the header closes the drawer.
  document.addEventListener("click", function (event) {
    if (drawer.matches && isOpen() && !header.contains(event.target)) setOpen(false);
  });

  // Choosing a link closes the drawer.
  navigation.querySelectorAll("a").forEach(function (link) {
    link.addEventListener("click", function () {
      if (drawer.matches) setOpen(false);
    });
  });

  // Crossing the breakpoint resets the drawer, keeping focus out of inert links.
  function reset() {
    var focusInside = navigation.contains(document.activeElement);
    setOpen(false);
    if (drawer.matches && focusInside) toggle.focus();
  }
  if (drawer.addEventListener) drawer.addEventListener("change", reset);
  else drawer.addListener(reset);
  reset();
})();
