'use strict';

const SERVICES = new Set(['web', 'catalogue', 'cart', 'payment']);
const BUCKETS = Object.freeze([0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10]);
const CONTENT_TYPE = 'text/plain; version=0.0.4; charset=utf-8';

/** One registry per process; attach before routes/error handlers. No path/user labels. */
function createRedMetrics(service) {
  if (!SERVICES.has(service)) throw new TypeError('Unsupported service');
  const statuses = new Map();
  const buckets = BUCKETS.map(() => 0);
  let count = 0;
  let sum = 0;

  function render() {
    const lines = [
      '# HELP http_server_requests_total Completed HTTP responses by service and status.',
      '# TYPE http_server_requests_total counter',
      ...[...statuses].sort(([a], [b]) => a - b).map(([status, value]) =>
        `http_server_requests_total{service="${service}",status="${status}"} ${value}`),
      '# HELP http_server_request_duration_seconds Completed HTTP response duration in seconds.',
      '# TYPE http_server_request_duration_seconds histogram',
      ...BUCKETS.map((bound, i) =>
        `http_server_request_duration_seconds_bucket{service="${service}",le="${bound}"} ${buckets[i]}`),
      `http_server_request_duration_seconds_bucket{service="${service}",le="+Inf"} ${count}`,
      `http_server_request_duration_seconds_sum{service="${service}"} ${sum}`,
      `http_server_request_duration_seconds_count{service="${service}"} ${count}`,
    ];
    return lines.join('\n') + '\n';
  }

  function middleware(req, res, next) {
    // Only the pathname is inspected; it is never recorded or exported.
    if ((req.url || '').split('?')[0] === '/metrics') {
      res.statusCode = 200;
      res.setHeader('Content-Type', CONTENT_TYPE);
      res.end(render());
      return;
    }
    const start = process.hrtime.bigint();
    res.once('finish', () => {
      const seconds = Number(process.hrtime.bigint() - start) / 1e9;
      // Node's status code is bounded; never turn arbitrary request fields into labels.
      const status = res.statusCode;
      statuses.set(status, (statuses.get(status) || 0) + 1);
      count += 1;
      sum += seconds;
      BUCKETS.forEach((bound, i) => { if (seconds <= bound) buckets[i] += 1; });
    });
    next();
  }
  return Object.freeze({ middleware, render });
}

module.exports = { createRedMetrics, BUCKETS, CONTENT_TYPE };
