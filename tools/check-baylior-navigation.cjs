// DOM-only behaviour checks. No browser launch, page load, resource fetch or network access.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const {JSDOM} = require(require.resolve('jsdom', {paths: [process.env.BAYLIOR_TEST_DEPENDENCIES || 'E:/TTS/Projects/Desktop_Apps/E6_Car_spa_new/apps/desktop/renderer']}));
const root = path.resolve(__dirname,'..');
const files = ['index.html','about.html','services.html','projects.html','contact.html',...['terms','refund-policy','privacy-policy','data-deletion','products/baylior'].map(p=>p+'/index.html')];
const script = fs.readFileSync(path.join(root,'js/baylior-navigation.js'),'utf8');
let refs=0;
for (const file of files) {
  const html=fs.readFileSync(path.join(root,file),'utf8');
  const dom=new JSDOM(html,{runScripts:'outside-only'});
  const {window:w}=dom, d=w.document;
  const ids=[...d.querySelectorAll('[id]')].map(e=>e.id);
  assert.equal(new Set(ids).size,ids.length,`${file}: duplicate id`);
  for(const a of d.querySelectorAll('.bp-header a,.bp-footer-products a,.bp-home-band a')) {
    const href=a.getAttribute('href');
    assert.ok(href.startsWith('/'),`${file}: nested path ${href}`);
    const [raw,anchor]=href.split('#');
    let target=path.join(root,raw);
    if(fs.statSync(target).isDirectory())target=path.join(target,'index.html');
    if(anchor) {
      const targetDom=new JSDOM(fs.readFileSync(target,'utf8'));
      assert.ok(targetDom.window.document.getElementById(anchor),`${file}: missing ${href}`);
      targetDom.window.close();
    }
    if(a.hasAttribute('data-baylior-destination')) {
      assert.equal(href,'/products/baylior/#preview-links');
      assert.match(a.textContent,/Preview link/);
    }
    refs++;
  }
  for(const img of d.querySelectorAll('.bp-header img,.bp-home-band img'))assert.ok(fs.existsSync(path.join(root,img.getAttribute('src'))));
  const mql={matches:false,addEventListener(_,cb){this.change=cb;}};
  w.matchMedia=()=>mql;
  w.eval(script);
  const product=d.querySelector('.bp-products-toggle'), panel=d.getElementById('baylior-products-panel'),menu=d.querySelector('.nav-toggle'),nav=d.getElementById('site-navigation');
  assert.ok(panel.hidden); assert.equal(nav.inert,false);
  product.click(); assert.equal(product.getAttribute('aria-expanded'),'true'); assert.equal(panel.hidden,false);
  panel.querySelector('a').focus();
  panel.dispatchEvent(new w.KeyboardEvent('keydown',{key:'Escape',bubbles:true}));
  assert.ok(panel.hidden); assert.equal(d.activeElement,product);
  product.click(); d.querySelector('main').click(); assert.ok(panel.hidden);
  product.click(); d.querySelector('.bp-header-actions a').focus(); assert.ok(panel.hidden);
  mql.matches=true; mql.change(); assert.ok(nav.inert); assert.equal(menu.getAttribute('aria-expanded'),'false');
  menu.click(); assert.equal(nav.inert,false); assert.equal(menu.getAttribute('aria-expanded'),'true');
  product.click(); panel.dispatchEvent(new w.KeyboardEvent('keydown',{key:'Escape',bubbles:true}));
  assert.ok(panel.hidden); assert.equal(menu.getAttribute('aria-expanded'),'true');
  product.dispatchEvent(new w.KeyboardEvent('keydown',{key:'Escape',bubbles:true}));
  assert.ok(nav.inert); assert.equal(d.activeElement,menu);
  menu.click(); product.click(); panel.querySelector('a').click();
  assert.ok(nav.inert); assert.ok(panel.hidden); assert.equal(d.activeElement,menu);
  menu.click(); d.querySelector('main').click(); assert.ok(nav.inert);
  mql.matches=false; mql.change(); assert.equal(nav.inert,false); assert.ok(panel.hidden);
  dom.window.close();
}
console.log(`PASS: ${files.length} pages, ${refs} discovery links/anchors, closed-state inertness, disclosure state, Escape focus return, outside click, focus-leave and responsive mode transitions. Native Tab/Enter/Space and rendered layout still require browser review.`);
