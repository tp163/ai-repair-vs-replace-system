import { spawn } from 'node:child_process';
import { mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import assert from 'node:assert/strict';

// Browser smoke check using the installed Edge and its DevTools protocol.
const browser = spawn('C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe', [
  '--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check',
  '--remote-debugging-port=9335', `--user-data-dir=${resolve('.next/catalogue-browser')}`, 'about:blank',
], { windowsHide: true, stdio: 'ignore' });
const delay = ms => new Promise(done => setTimeout(done, ms));
let socket;
try {
  let targets;
  for (let i = 0; i < 40; i++) {
    try { targets = await (await fetch('http://127.0.0.1:9335/json/list')).json(); break; } catch { await delay(250); }
  }
  assert(targets?.length, 'Edge debugging session started');
  socket = new WebSocket(targets.find(target => target.type === 'page').webSocketDebuggerUrl);
  await new Promise(done => socket.addEventListener('open', done, { once: true }));
  let sequence = 0;
  const pending = new Map();
  const errors = [];
  socket.addEventListener('message', event => {
    const message = JSON.parse(event.data);
    if (message.id) { const task = pending.get(message.id); pending.delete(message.id); message.error ? task.reject(message.error) : task.resolve(message.result); }
    if (message.method === 'Runtime.exceptionThrown') errors.push(message.params.exceptionDetails.text);
  });
  const send = (method, params = {}) => new Promise((resolve, reject) => { const id = ++sequence; pending.set(id, { resolve, reject }); socket.send(JSON.stringify({ id, method, params })); });
  const evaluate = async expression => {
    const result = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
    if (result.exceptionDetails) throw Error(result.exceptionDetails.text);
    return result.result.value;
  };
  await send('Runtime.enable');
  await send('Page.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: 1440, height: 1000, deviceScaleFactor: 1, mobile: false });
  await send('Page.navigate', { url: 'http://localhost:3100/find-a-phone' });
  for (let i = 0; i < 60; i++) { if (await evaluate("document.querySelectorAll('.catalogue-card').length === 5")) break; await delay(250); }
  await delay(900);
  assert.equal(await evaluate("document.querySelectorAll('.catalogue-card').length"), 5);
  assert.equal(await evaluate("[...document.querySelectorAll('.gallery-frame img')].filter(img=>!img.complete || !img.naturalWidth).length"), 0, 'Product images load');
  assert.equal(await evaluate('document.documentElement.scrollWidth <= innerWidth'), true, 'Desktop has no horizontal overflow');
  await mkdir('.next/catalogue-checks', { recursive: true });
  const screenshot = async name => { const { data } = await send('Page.captureScreenshot', { format: 'png' }); await writeFile(`.next/catalogue-checks/${name}.png`, Buffer.from(data, 'base64')); };
  await screenshot('desktop-dark');
  await evaluate("document.documentElement.dataset.theme='light'");
  await delay(350);
  await screenshot('desktop-light');
  const before = await evaluate("document.querySelector('.gallery-track').style.transform");
  await delay(4100);
  assert.notEqual(await evaluate("document.querySelector('.gallery-track').style.transform"), before, 'Slideshow advances automatically');
  await evaluate("document.querySelector('[aria-label=\"iPhone 13: Pink\"]').click()");
  assert.equal(await evaluate("document.querySelector('.skin-stage').innerText.includes('Pink')"), true, 'Colour changes preview');
  await evaluate("document.querySelector('.catalogue-photo-link').click()");
  await delay(800);
  assert.equal(await evaluate("document.querySelector('.detail-copy h1').innerText"), 'iPhone 13');
  assert.equal(await evaluate("document.querySelectorAll('.spec-group').length"), 5, 'Full specs displayed');
  await screenshot('detail-desktop');
  await evaluate('window.scrollTo(0,document.body.scrollHeight)');
  await delay(800);
  assert.equal(await evaluate("getComputedStyle(document.querySelector('.spec-group:last-child')).opacity"), '1', 'Specification rows reveal when scrolled into view');
  await evaluate("document.querySelector('.catalogue-back').click()");
  await delay(700);
  await evaluate("[...document.querySelectorAll('.catalogue-brands button')].find(button=>button.innerText.includes('Samsung')).click()");
  await delay(700);
  assert.equal(await evaluate("document.querySelectorAll('.catalogue-card').length"), 1, 'Brand filtering works');
  await evaluate("document.querySelector('.catalogue-brands button').click()");
  await delay(700);
  await send('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 1, mobile: true });
  await delay(500);
  assert.equal(await evaluate('document.documentElement.scrollWidth <= innerWidth'), true, 'Mobile has no horizontal overflow');
  await screenshot('mobile');
  await evaluate("document.querySelector('.catalogue-photo-link').click()");
  await delay(700);
  assert.equal(await evaluate('document.documentElement.scrollWidth <= innerWidth'), true, 'Mobile detail has no horizontal overflow');
  await screenshot('detail-mobile');
  await send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-reduced-motion', value: 'reduce' }] });
  await evaluate("document.querySelector('.catalogue-back').click()");
  await delay(400);
  const reducedBefore = await evaluate("document.querySelector('.gallery-track').style.transform");
  await delay(4100);
  assert.equal(await evaluate("document.querySelector('.gallery-track').style.transform"), reducedBefore, 'Reduced motion disables automatic slides');
  assert.deepEqual(errors, [], 'No browser runtime exceptions');
  console.log('PASS: five cards, local photos, automatic slides, skin selection, full specs, brand filters, desktop/mobile layout, no browser errors.');
  console.log('Screenshots: .next/catalogue-checks/');
} finally { socket?.close(); browser.kill(); }
