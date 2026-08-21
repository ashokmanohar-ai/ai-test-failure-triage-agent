import { createServer } from 'node:http';

const profile = process.env.FAILURE_PROFILE ?? 'none';
let flakyVisits = 0;

const page = () => {
  const label = profile === 'locator_change' ? 'Continue to payment' : 'Checkout';
  const total = profile === 'product_defect' ? '£90' : '£100';
  const dataState = profile === 'invalid_test_data' ? 'Account expired' : 'Account active';
  const delay = profile === 'flaky_timing' && ++flakyVisits % 2 === 1 ? 1800 : 0;
  return `<!doctype html><html><body><h1>Controlled Checkout</h1><p id="total">${total}</p><p id="account">${dataState}</p><button id="checkout" style="visibility:${delay ? 'hidden' : 'visible'}">${label}</button><p id="result"></p><script>
  const button = document.querySelector('#checkout');
  ${delay ? `setTimeout(() => { button.style.visibility = 'visible'; }, ${delay});` : ''}
  button.addEventListener('click', async () => {
    const response = await fetch('/api/orders', { method: 'POST' });
    if (!response.ok) console.error('Order request failed', response.status);
    document.querySelector('#result').textContent = response.ok ? 'Order confirmed' : 'Order failed';
  });
  </script></body></html>`;
};

const server = createServer((request, response) => {
  if (request.url === '/ready') { response.writeHead(200); response.end('ready'); return; }
  if (request.url === '/health') { response.writeHead(profile === 'environment_down' ? 503 : 200, { 'content-type': 'application/json' }); response.end(JSON.stringify({ status: profile === 'environment_down' ? 'DOWN' : 'UP' })); return; }
  if (request.url === '/api/session') { response.writeHead(profile === 'auth_expired' ? 401 : 200); response.end(); return; }
  if (request.url === '/api/orders' && request.method === 'POST') {
    const status = profile === 'api_500' ? 500 : profile === 'auth_expired' ? 401 : 201;
    const respond = () => { response.writeHead(status, { 'content-type': 'application/json', 'x-correlation-id': 'demo-req-001' }); response.end(JSON.stringify({ status })); };
    if (profile === 'slow_endpoint') setTimeout(respond, 2000); else respond();
    return;
  }
  response.writeHead(200, { 'content-type': 'text/html' }); response.end(page());
});

server.listen(4173, '127.0.0.1');
for (const signal of ['SIGTERM', 'SIGINT']) process.on(signal, () => server.close(() => process.exit(0)));

