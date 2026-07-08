/* ==========================================================================
   Trovotech Solutions — Site interactions
   Progressive enhancement only: the site is fully usable without JS.
   ========================================================================== */
(function () {
  "use strict";

  /* ---- Mobile nav toggle ---- */
  const toggle = document.querySelector(".nav-toggle");
  const links = document.querySelector(".nav-links");
  if (toggle && links) {
    toggle.addEventListener("click", function () {
      const open = links.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", String(open));
    });
    // Close menu after choosing a link (mobile)
    links.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () { links.classList.remove("is-open"); });
    });
  }

  /* ---- Navbar shadow on scroll ---- */
  const navbar = document.querySelector(".navbar");
  if (navbar) {
    const onScroll = function () {
      navbar.classList.toggle("is-scrolled", window.scrollY > 20);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  /* ---- Scroll-reveal for elements marked .reveal ---- */
  const revealEls = document.querySelectorAll(".reveal");
  if (revealEls.length && "IntersectionObserver" in window) {
    const io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });
    revealEls.forEach(function (el) { io.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add("is-visible"); });
  }

  /* ---- Project filtering (projects page) ---- */
  const filterBtns = document.querySelectorAll(".filter-btn");
  const projectCards = document.querySelectorAll("[data-category]");
  if (filterBtns.length && projectCards.length) {
    filterBtns.forEach(function (btn) {
      btn.addEventListener("click", function () {
        filterBtns.forEach(function (b) { b.classList.remove("is-active"); });
        btn.classList.add("is-active");
        const filter = btn.getAttribute("data-filter");
        projectCards.forEach(function (card) {
          const match = filter === "all" || card.getAttribute("data-category") === filter;
          card.style.display = match ? "flex" : "none";
        });
      });
    });
  }

  /* ---- Client logos: fall back to icon if image is missing ---- */
  document.querySelectorAll(".client__box").forEach(function (box) {
    const img = box.querySelector("img");
    const icon = box.querySelector(".material-symbols-outlined");
    if (!img || !icon) return;
    const showFallback = function () {
      img.classList.add("is-hidden");
      icon.classList.remove("is-hidden");
    };
    img.addEventListener("error", showFallback);
    if (img.complete && img.naturalWidth === 0) { showFallback(); }
  });

  /* ---- Footer year ---- */
  const yearEl = document.querySelector("[data-year]");
  if (yearEl) { yearEl.textContent = String(new Date().getFullYear()); }
})();
