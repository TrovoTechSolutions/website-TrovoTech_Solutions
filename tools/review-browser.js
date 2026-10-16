// Automated browser review using Chrome DevTools Protocol via native WebSocket
const { spawn } = require('node:child_process');
const http = require('node:http');

const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const PORT = 9333;

function get(url) {
  return new Promise((resolve, reject) => {
    http.get(url, res => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(data));
    }).on('error', reject);
  });
}

function delay(ms) {
  return new Promise(r => setTimeout(r, ms));
}

async function main() {
  console.log('Launching headless Chrome for browser review...');
  const proc = spawn(CHROME, [
    '--headless=new',
    `--remote-debugging-port=${PORT}`,
    '--hide-scrollbars',
    'about:blank'
  ]);

  try {
    await delay(1500);
    const tabsJson = await get(`http://localhost:${PORT}/json`);
    const tabs = JSON.parse(tabsJson);
    const pageTab = tabs.find(t => t.type === 'page') || tabs[0];
    const wsUrl = pageTab.webSocketDebuggerUrl;

    const ws = new WebSocket(wsUrl);
    await new Promise((res, rej) => {
      ws.onopen = res;
      ws.onerror = rej;
    });

    let reqId = 1;
    function send(method, params = {}) {
      return new Promise((resolve, reject) => {
        const id = reqId++;
        const onMsg = (event) => {
          const msg = JSON.parse(event.data);
          if (msg.id === id) {
            ws.removeEventListener('message', onMsg);
            if (msg.error) reject(msg.error);
            else resolve(msg.result);
          }
        };
        ws.addEventListener('message', onMsg);
        ws.send(JSON.stringify({ id, method, params }));
      });
    }

    async function waitFor(expr, timeoutMs = 5000) {
      const start = Date.now();
      while (Date.now() - start < timeoutMs) {
        const res = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
        if (res?.result?.value) return res.result.value;
        await delay(100);
      }
      throw new Error(`Timeout waiting for: ${expr}`);
    }

    const consoleErrors = [];
    ws.addEventListener('message', (event) => {
      const msg = JSON.parse(event.data);
      if (msg.method === 'Console.messageAdded' && msg.params.message.level === 'error') {
        consoleErrors.push(msg.params.message.text);
      }
      if (msg.method === 'Runtime.exceptionThrown') {
        consoleErrors.push(msg.params.exceptionDetails.text);
      }
    });

    await send('Console.enable');
    await send('Runtime.enable');
    await send('Page.enable');

    console.log('\n--- 1. Testing No Horizontal Scroll & Layout at 375, 768, 1366 px ---');
    const urls = [
      'http://localhost:5501/products/baylior/',
      'http://localhost:5501/products/'
    ];

    for (const pageUrl of urls) {
      for (const width of [375, 768, 1366]) {
        await send('Emulation.setDeviceMetricsOverride', {
          width,
          height: 900,
          deviceScaleFactor: 1,
          mobile: width < 1000
        });
        await send('Page.navigate', { url: pageUrl });
        await delay(1000);

        const evalRes = await send('Runtime.evaluate', {
          expression: '({ scrollWidth: document.documentElement.scrollWidth, clientWidth: document.documentElement.clientWidth })',
          returnByValue: true
        });

        const { scrollWidth, clientWidth } = evalRes.result.value;
        const noScroll = scrollWidth <= clientWidth;
        console.log(`[PASS: ${noScroll}] ${pageUrl} @ ${width}px -> scrollWidth: ${scrollWidth}, clientWidth: ${clientWidth}`);
        if (!noScroll) {
          throw new Error(`Horizontal scroll detected on ${pageUrl} at ${width}px!`);
        }
      }
    }

    console.log('\n--- 2. Keyboard Navigation: Product Sub-Header & FAQ Accordion ---');
    await send('Emulation.setDeviceMetricsOverride', { width: 1366, height: 900, deviceScaleFactor: 1, mobile: false });
    await send('Page.navigate', { url: 'http://localhost:5501/products/baylior/' });
    await waitFor('document.readyState === "complete" && Boolean(document.querySelector(".b-product-nav .b-nav-links a"))');

    const keyboardTest = await send('Runtime.evaluate', {
      expression: `(() => {
        // Test sub-header links keyboard focus
        const firstLink = document.querySelector('.b-product-nav .b-nav-links a');
        if (!firstLink) return { error: 'No link found in .b-product-nav .b-nav-links' };
        firstLink.focus();
        const navFocused = document.activeElement === firstLink;

        // Test details / summary expansion
        const details = document.querySelector('details');
        if (!details) return { error: 'No details element found' };
        const summary = details.querySelector('summary');
        summary.focus();
        const summaryFocused = document.activeElement === summary;
        summary.click();
        const opened = details.open;

        return { navFocused, summaryFocused, opened };
      })()`,
      returnByValue: true
    });

    const testVal = keyboardTest?.result?.value;
    console.log('Sub-header first link focused:', testVal.navFocused);
    console.log('FAQ summary focused by keyboard:', testVal.summaryFocused);
    console.log('FAQ details toggled open on click/enter:', testVal.opened);
    if (!testVal.navFocused || !testVal.summaryFocused || !testVal.opened) {
      throw new Error('Keyboard navigation test failed!');
    }

    console.log('\n--- 3. Console Errors Check ---');
    console.log(`Total console errors recorded across all runs: ${consoleErrors.length}`);
    if (consoleErrors.length > 0) {
      console.error('Errors:', consoleErrors);
      throw new Error('Console errors encountered during browser review!');
    }

    console.log('\nALL BROWSER REVIEW CHECKS PASSED SUCCESSFULLY.');
    ws.close();
  } finally {
    proc.kill();
  }
}

main().catch(err => {
  console.error('Browser review failed:', err);
  process.exit(1);
});
