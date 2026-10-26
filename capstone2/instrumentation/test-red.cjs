'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const http = require('node:http');
const { createRedMetrics, BUCKETS, CONTENT_TYPE } = require('./red.cjs');

test('service labels are a fixed allowlist', () => {
  for (const service of ['web', 'catalogue', 'cart', 'payment']) assert.ok(createRedMetrics(service));
  for (const service of ['user-123', '', 'cart"\n', undefined]) {
    assert.throws(() => createRedMetrics(service), /Unsupported service/);
  }
});

test('real HTTP responses export cumulative RED metrics and exclude scrapes', async t => {
  const metrics = createRedMetrics('cart');
  const server = http.createServer((req, res) => metrics.middleware(req, res, () => {
    setTimeout(() => {
      res.statusCode = req.url.startsWith('/fail') ? 500 : 200;
      res.end('synthetic test');
    }, 30);
  }));
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  t.after(() => new Promise(resolve => server.close(resolve)));
  const base = `http://127.0.0.1:${server.address().port}`;
  assert.equal((await fetch(`${base}/ok/private-user?token=not-a-secret-fixture`)).status, 200);
  assert.equal((await fetch(`${base}/fail`)).status, 500);
  const scrape = await fetch(`${base}/metrics?probe=1`);
  assert.equal(scrape.headers.get('content-type'), CONTENT_TYPE);
  const text = await scrape.text();
  assert.match(text, /http_server_requests_total\{service="cart",status="200"\} 1\n/);
  assert.match(text, /http_server_requests_total\{service="cart",status="500"\} 1\n/);
  assert.match(text, /_count\{service="cart"\} 2\n/);
  assert.doesNotMatch(text, /private-user|token|probe=|path=/);
  const counts = BUCKETS.map(bound => Number(text.match(new RegExp(`le="${String(bound).replace('.', '\\.')}"\\} (\\d+)`))[1]));
  assert.ok(counts.every((n, i) => i === 0 || n >= counts[i - 1]));
  assert.equal(counts[0], 0); // Both actual responses intentionally take at least 30ms.
  assert.equal(counts.at(-1), 2);
  assert.match(text, /le="\+Inf"\} 2\n/);
  assert.ok(Number(text.match(/_sum\{service="cart"\} ([0-9.e+-]+)/)[1]) >= 0.05);
  assert.equal(await (await fetch(`${base}/metrics`)).text(), text);
});

test('empty registry has valid zero-valued histogram', () => {
  const text = createRedMetrics('catalogue').render();
  assert.match(text, /_count\{service="catalogue"\} 0/);
  assert.match(text, /le="\+Inf"\} 0/);
  assert.doesNotMatch(text, /NaN|undefined/);
});
