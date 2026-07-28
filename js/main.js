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

  /* ---- Contact Form Web3Forms AJAX ---- */
  const contactForm = document.getElementById("contactForm");
  const formResult = document.getElementById("contactFormResult");
  const submitBtnText = document.getElementById("submitBtnText");

  if (contactForm && formResult && submitBtnText) {
    contactForm.addEventListener("submit", function(e) {
      e.preventDefault();
      
      const formData = new FormData(contactForm);
      const object = Object.fromEntries(formData);
      const json = JSON.stringify(object);
      
      // UI Feedback
      submitBtnText.textContent = "Sending...";
      formResult.style.display = "none";
      formResult.classList.remove("is-error", "is-success");
      formResult.style.backgroundColor = "transparent";

      fetch("https://api.web3forms.com/submit", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Accept": "application/json"
        },
        body: json
      })
      .then(async (response) => {
        let json = await response.json();
        if (response.status == 200) {
          formResult.innerHTML = "Form submitted successfully! We'll be in touch soon.";
          formResult.style.color = "#10b981"; // Success green
          formResult.style.backgroundColor = "rgba(16, 185, 129, 0.1)";
          contactForm.reset();
        } else {
          console.log(response);
          formResult.innerHTML = json.message || "Something went wrong!";
          formResult.style.color = "#ef4444"; // Error red
          formResult.style.backgroundColor = "rgba(239, 68, 68, 0.1)";
        }
      })
      .catch(error => {
        console.log(error);
        formResult.innerHTML = "Something went wrong! Please try again.";
        formResult.style.color = "#ef4444";
        formResult.style.backgroundColor = "rgba(239, 68, 68, 0.1)";
      })
      .then(function() {
        formResult.style.display = "block";
        submitBtnText.textContent = "Send Message";
        setTimeout(() => {
          formResult.style.display = "none";
        }, 5000);
      });
    });
  }
})();
