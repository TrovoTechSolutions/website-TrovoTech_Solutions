# Phase 3 — company website discovery

Implementation prepared 14 October 2026 on `signup-phase3`; local preview only. Committed to `main`; not deployed.

## Included

- Shared Products disclosure on five company pages, four policy pages and the Baylior page.
- Baylior panel with logo, tagline, description, feature anchors, Explore Baylior, signup and pricing actions.
- Get the app and signup actions in desktop headers and inside the mobile drawer.
- Product links in every footer, retaining existing links; Terms and Refund Policy included.
- Home-page Baylior band after the hero, with the approved real screenshot.
- E6 remains a Portfolio project with no Baylior endorsement.
- One disabled signup/pricing destination configuration at `/js/baylior-destinations.js`. Every unconfigured action is visibly marked Preview link and leads to the product-page explanation.

## Accessibility behaviour

Products is a native disclosure button with aria-expanded/aria-controls. Its panel uses hidden, so closed links are not focusable. Native Enter/Space and Tab behaviour is retained. Escape closes the panel and restores focus to Products; a second Escape closes the mobile drawer and returns focus to the navigation toggle. Outside click and leaving the disclosure with focus close the panel. Mobile closed navigation is inert; selecting a link closes it. Responsive mode changes reset state and keep focus out of inert content.

## Verification

Passing DOM-only checks cover all ten pages and 223 discovery links/anchors, unique IDs, local assets, disclosure states, Escape focus return, outside click, focus-leave and breakpoint state transitions. Destination policy checks cover disabled/invalid configuration and route mapping. Existing Phase 2 source/asset checks and JavaScript syntax checks pass.

Browser review completed 14 October 2026 (built-in browser, local server on port 5195): Products menu by mouse and keyboard (Enter, Tab, Shift+Tab, Escape returns focus, outside click, focus leaving closes it); phone menu (opens, scrolls, Escape closes panel then menu, closed links not focusable); all ten pages at 375 and desktop widths with no horizontal scroll, broken images or console errors; header fits on one line at 1024 and 1366. Phase 3 is complete as a local preview. The live website will be redesigned and uploaded later; "Get a Quote" was removed from the header and should be reconsidered in that redesign.

Existing unrelated website changes, page bodies, root redirect rules and policy text were preserved. No live signup domain, production trial claim or payment integration was introduced.
