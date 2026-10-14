# Baylior landing page — Phase 2 local preview

This build stays local. Do not deploy this folder or publish its sitemap entry before integration is verified.

Preview from the website root with a static server, then open `/products/baylior/`.

## Release gates

- `.htaccess` restricts Apache/LiteSpeed access to local requests; no production hosting settings have been changed.
- `noindex,nofollow` and a prominent LOCAL PREVIEW banner identify the draft.
- Every signup/pricing button is visibly labelled Preview link and targets the in-page placeholder explanation, including without JavaScript.
- `/js/baylior-destinations.js` has one shared destination setting with `integrationVerified: false` and an empty `signupOrigin`. Both must be deliberately configured after Phase 5 checks. HTTPS origins only; signup maps to `/signup`, pricing to `/`.
- Keep neutral Sign up wording, no fixed marketing prices or trial duration. Subscription screenshot amounts are demo data, not advertised prices. Production module/trial confirmation remains pending.
- No E6 endorsement, customer counts, testimonials or one-click WhatsApp setup claim.

## Contents

Hero, sticky product navigation, core feature blocks, job card/invoice examples, qualified modules, Windows/Android licences, onboarding steps, pricing teaser, FAQ, closing actions and installer contact fallback. The Trovo header and footer Products column come from `tools/build-site-header.py` (run it after changing the menu). The page itself is edited directly; the one-off Phase 2 build script was retired.

Assets are copied into `/assets/baylior/`; the page has no cross-repository asset dependency. The composed share card is PNG, exactly 1200×630, from the approved Baylior logo with original headline and platform copy. Open Graph and Twitter metadata use the intended canonical website paths; remote share scrapers will not see the image until release.

## Verification

Source checks cover local asset paths, anchors, structured data without offers/prices, preview destinations, metadata, screenshot hashes and share-card dimensions. Browser desktop/mobile, keyboard and visual checks remain pending because browser access to the local preview was declined. Responsive CSS covers phone, tablet and desktop but is not a substitute for rendered review.

Website changes that predated this task are preserved. Phase 3 site navigation, home-page band, Phase 4 signup changes and hosting are outside this build.

Follow-up: added Terms and Refund Policy to this page's footer. Mobile product bar uses one 64px row with horizontally scrollable section links and a fixed signup action; anchor offsets account for the shorter bar. Source and destination checks pass; rendered mobile confirmation remains pending.

