// Destination policy verification for SaaS products; no browser or network access.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const path = require('node:path');

// Test product-destinations.js
const destPath = path.join(__dirname, '../js/product-destinations.js');
const source = fs.readFileSync(destPath, 'utf8');

function run(config, productKey = 'carspa') {
  const links = ['signup', 'pricing'].map(kind => ({
    dataset: { destination: kind, product: productKey },
    href: '#preview-links',
    querySelectorAll: () => []
  }));

  const code = config
    ? source.replace(
        /const destinations = Object\.freeze\(\{[\s\S]*?\}\);/,
        `const destinations = Object.freeze(${JSON.stringify(config)});`
      )
    : source;

  vm.runInNewContext(code, {
    URL,
    document: {
      body: { classList: { add: () => {} } },
      querySelector: () => null,
      querySelectorAll: () => links
    }
  });

  return links.map(l => l.href);
}

// 1. Default state: unverified, remains placeholders
assert.deepEqual(run(), ['#preview-links', '#preview-links']);

// 2. Invalid or unverified configurations
for (const config of [
  { integrationVerified: false, signupOrigin: 'https://signup.example.test' },
  { integrationVerified: true, signupOrigin: 'http://signup.example.test' }, // HTTP remote rejected
  { integrationVerified: true, signupOrigin: 'javascript:alert(1)' },
  { integrationVerified: true, signupOrigin: 'https://signup.example.test/subfolder' },
  { integrationVerified: true, signupOrigin: 'https://user:password@signup.example.test' },
  { integrationVerified: true, signupOrigin: 'https://signup.example.test/?token=test' }
]) {
  assert.deepEqual(run(config), ['#preview-links', '#preview-links']);
}

// 3. Verified HTTPS origin: maps {origin}/signup/{platformKey} and {origin}/pricing/{platformKey}
assert.deepEqual(
  run({ integrationVerified: true, signupOrigin: 'https://signup.example.test' }, 'carspa'),
  ['https://signup.example.test/signup/carspa', 'https://signup.example.test/pricing/carspa']
);

assert.deepEqual(
  run({ integrationVerified: true, signupOrigin: 'https://signup.example.test' }, 'civil'),
  ['https://signup.example.test/signup/civil', 'https://signup.example.test/pricing/civil']
);

// 4. Verified localhost origin (dev support)
assert.deepEqual(
  run({ integrationVerified: true, signupOrigin: 'http://localhost:5191' }, 'carspa'),
  ['http://localhost:5191/signup/carspa', 'http://localhost:5191/pricing/carspa']
);

console.log('PASS: default and invalid destinations remain placeholders; verified origins map routes to {origin}/signup/{platformKey} and {origin}/pricing/{platformKey}.');
