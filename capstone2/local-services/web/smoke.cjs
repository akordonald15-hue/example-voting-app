const cp=require('node:child_process');
const assert=require('node:assert/strict');
const p=cp.spawn(process.execPath,['server.cjs']);
setTimeout(async()=>{try{
  let r=await fetch('http://127.0.0.1:8080/'); assert.equal(r.status,200);
  assert.ok((await r.text()).includes('Stan'));
  r=await fetch('http://127.0.0.1:8080/health');assert.equal(await r.text(),'OK');
  r=await fetch('http://127.0.0.1:8080/missing');assert.equal(r.status,404);
  r=await fetch('http://127.0.0.1:8080/metrics');let body=await r.text();
  assert.ok(body.includes('http_server_requests_total{service="web",status="200"}'));
  assert.ok(body.includes('status="404"'));
  assert.ok(body.includes('http_server_request_duration_seconds_bucket'));
  console.log('WEB_STATIC_HEALTH_RED_PASS');
}catch(e){console.error(e);process.exitCode=1;}finally{p.kill();}},300);
