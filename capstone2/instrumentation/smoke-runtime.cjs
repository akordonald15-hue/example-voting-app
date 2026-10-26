'use strict';
// Run inside the image after startup; verifies HTTP instrumentation, not database readiness.
(async () => {
  for (let attempt = 0; attempt < 20; attempt += 1) {
    try {
      const response = await fetch('http://127.0.0.1:8080/health');
      if (response.status !== 200) throw Error('Health endpoint unavailable');
      const health = await response.json();
      const readiness = await fetch('http://127.0.0.1:8080/ready');
      if (readiness.status !== 503) throw Error('Expected unavailable dependency readiness HTTP503');
      const metrics = await (await fetch('http://127.0.0.1:8080/metrics')).text();
      if (!metrics.includes('http_server_requests_total') || !metrics.includes('http_server_request_duration_seconds_bucket')) throw Error('Missing RED metrics');
      if ((process.env.EXPECT_CART || '').toLowerCase() === 'true' && !metrics.includes('items_added')) throw Error('Missing upstream cart counter');
      console.log(JSON.stringify({ result: 'PASS', health, readinessStatus: readiness.status, metrics }));
      return;
    } catch (error) {
      if (attempt === 19) throw error;
      await new Promise(resolve => setTimeout(resolve, 500));
    }
  }
})().catch(error => { console.error(error.message); process.exitCode = 1; });
