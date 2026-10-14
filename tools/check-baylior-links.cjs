// Isolated destination-policy verification; no browser or network access.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../products/baylior/destinations.js'), 'utf8');
function run(config) {
  const links = ['signup','pricing'].map(kind => ({ dataset: {destination:kind}, href:'#preview-links', classList: {add() {}} }));
  const code = config ? source.replace("{ integrationVerified: false, signupOrigin: '' }", JSON.stringify(config)) : source;
  vm.runInNewContext(code, {URL, document: { querySelector:()=>null, querySelectorAll:()=>links }});
  return links.map(link=>link.href);
}
assert.deepEqual(run(), ['#preview-links','#preview-links']);
for (const config of [
  {integrationVerified:false, signupOrigin:'https://signup.example.test'},
  {integrationVerified:true, signupOrigin:'http://signup.example.test'},
  {integrationVerified:true, signupOrigin:'javascript:alert(1)'},
  {integrationVerified:true, signupOrigin:'https://signup.example.test/subfolder'},
  {integrationVerified:true, signupOrigin:'https://user:password@signup.example.test'},
  {integrationVerified:true, signupOrigin:'https://signup.example.test/?token=test'}
]) assert.deepEqual(run(config), ['#preview-links','#preview-links']);
assert.deepEqual(run({integrationVerified:true,signupOrigin:'https://signup.example.test'}), ['https://signup.example.test/signup','https://signup.example.test/']);
console.log('PASS: default and invalid/unverified destinations remain placeholders; verified HTTPS origin maps routes correctly.');
