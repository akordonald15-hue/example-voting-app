'use strict';
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const {createRedMetrics} = require('./red.cjs');
const metrics = createRedMetrics('web');
const services = new Set(['catalogue','user','cart','shipping','payment','ratings']);
const types = {'.html':'text/html','.js':'application/javascript','.css':'text/css','.json':'application/json','.png':'image/png','.jpg':'image/jpeg','.svg':'image/svg+xml','.woff':'font/woff','.woff2':'font/woff2','.ico':'image/x-icon'};
http.createServer((req,res) => metrics.middleware(req,res,() => {
  res.on('finish', () => console.log(JSON.stringify({service:'web',level:'info',method:req.method,status:res.statusCode})));
  const route = req.url.match(/^\/api\/([^/]+)\/(.*)$/);
  if (route && services.has(route[1])) {
    const service = route[1];
    const host = process.env[service.toUpperCase()+'_HOST'] || service;
    const upstream = http.request({hostname:host,port:service==='ratings'?80:8080,path:'/'+route[2],method:req.method,headers:{...req.headers,host}}, response => {
      res.writeHead(response.statusCode,response.headers); response.pipe(res);
    });
    upstream.setTimeout(15000,()=>upstream.destroy(new Error('upstream timeout')));
    upstream.on('error',()=>{if(!res.headersSent)res.writeHead(502);res.end('upstream unavailable');});
    req.pipe(upstream); return;
  }
  if(req.url.split('?')[0]==='/health'){res.end('OK');return;}
  let name;
  try { name=decodeURIComponent(req.url.split('?')[0]); } catch {res.writeHead(400);res.end();return;}
  if(name==='/') name='/index.html';
  let file=path.resolve(__dirname,'static','.'+name);
  if(!file.startsWith(path.join(__dirname,'static')+path.sep)){res.writeHead(403);res.end();return;}
  if(!fs.existsSync(file)&&name.startsWith('/images/'))file=path.join(__dirname,'static/images/placeholder.png');
  fs.readFile(file,(error,data)=>{if(error){res.writeHead(404);res.end();return;}
    res.setHeader('Content-Type',types[path.extname(file)]||'application/octet-stream');
    // Remove optional Instana browser injection; the application content is retained.
    res.end(path.extname(file)==='.html'?data.toString().replace(/<!--# include file="eum.html" -->/g,''):data);
  });
})).listen(8080,'0.0.0.0');
