/* ==========================================================================
   Trovo Tech Solutions — site navigation (phone/tablet drawer)
   Below 1024px the links slide in from the right. Closed links are inert so
   keyboard users cannot tab into an off-screen drawer.
   ========================================================================== */
(function () {
  "use strict";

  function init() {
    var header = document.querySelector(".site-header");
    if (!header) return;
    var navigation = header.querySelector("#site-navigation");
    var toggle = header.querySelector(".nav-toggle");
    if (!navigation || !toggle) return;
    var icon = toggle.querySelector(".material-symbols-outlined");
    var drawer = window.matchMedia("(max-width: 1023px)");

    // Ensure a backdrop element exists for mobile touch outside
    var backdrop = document.querySelector(".nav-backdrop");
    if (!backdrop) {
      backdrop = document.createElement("div");
      backdrop.className = "nav-backdrop";
      backdrop.setAttribute("aria-hidden", "true");
      document.body.appendChild(backdrop);
    }

    function isOpen() {
      return toggle.getAttribute("aria-expanded") === "true";
    }

    function setOpen(open) {
      navigation.classList.toggle("is-open", open);
      if (backdrop) backdrop.classList.toggle("is-open", open);
      document.body.classList.toggle("nav-open", open);
      navigation.inert = drawer.matches && !open;
      toggle.setAttribute("aria-expanded", String(open));
      toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
      if (icon) icon.textContent = open ? "close" : "menu";
    }

    toggle.addEventListener("click", function (event) {
      event.preventDefault();
      event.stopPropagation();
      setOpen(!isOpen());
    });

    if (backdrop) {
      backdrop.addEventListener("click", function (event) {
        event.preventDefault();
        setOpen(false);
      });
    }

    // Escape closes the drawer and returns focus to the menu button.
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && drawer.matches && isOpen()) {
        setOpen(false);
        toggle.focus();
      }
    });

    // A click outside the header and navigation closes the drawer.
    document.addEventListener("click", function (event) {
      if (!drawer.matches || !isOpen()) return;
      var path = event.composedPath ? event.composedPath() : [];
      if (path.length > 0) {
        if (path.indexOf(header) !== -1 || path.indexOf(toggle) !== -1 || path.indexOf(navigation) !== -1) return;
      }
      if (header.contains(event.target) || toggle.contains(event.target) || navigation.contains(event.target)) return;
      setOpen(false);
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
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

