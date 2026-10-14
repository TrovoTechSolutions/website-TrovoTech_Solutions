/* ==========================================================================
   Trovo Tech Solutions — /products/ industry filter
   Without JavaScript every product stays visible.
   ========================================================================== */
(function () {
  "use strict";

  var buttons = document.querySelectorAll(".products-filter button[data-industry]");
  var cards = document.querySelectorAll(".product-card[data-industry]");
  if (!buttons.length) return;

  buttons.forEach(function (button) {
    button.addEventListener("click", function () {
      var industry = button.dataset.industry;
      buttons.forEach(function (other) {
        other.setAttribute("aria-pressed", String(other === button));
      });
      cards.forEach(function (card) {
        card.hidden = industry !== "all" && card.dataset.industry !== industry;
      });
    });
  });
})();
