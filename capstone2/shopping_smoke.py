"""Bounded synthetic checkout in explicitly named local kind; no real payment."""
import datetime,json,subprocess
from pathlib import Path
from collect_kind import K, NODE, read
SCRIPT = r"""
(async()=>{
const receipts=[];
async function call(path,method='GET',body){const t=Date.now();const r=await fetch('http://web:8080'+path,{method,headers:body?{'content-type':'application/json'}:{},body:body?JSON.stringify(body):undefined,signal:AbortSignal.timeout(20000)});const text=await r.text();receipts.push({path,method,status:r.status,ms:Date.now()-t});if(!r.ok)throw Error(method+' '+path+' returned '+r.status);try{return JSON.parse(text)}catch{return text}}
try {
const credential={name:'flow-'+require('crypto').randomBytes(6).toString('hex'),password:require('crypto').randomBytes(24).toString('hex'),email:'flow@example.invalid'};
await call('/api/user/register','POST',credential);
await call('/api/user/login','POST',credential);
const id=(await call('/api/user/uniqueid')).uuid;
const products=await call('/api/catalogue/products');const product=products.find(p=>p.instock>0);if(!product)throw Error('No in-stock product');
await call('/api/cart/add/'+id+'/'+product.sku+'/1');
await call('/api/cart/cart/'+id);
const codes=await call('/api/shipping/codes');let cities=[];let code;
for(const candidate of codes.slice(0,3)){code=candidate;cities=await call('/api/shipping/cities/'+code.code);if(cities.length)break}
if(!cities.length)throw Error('No shipping city');
const shipping=await call('/api/shipping/calc/'+cities[0].uuid);shipping.location=code.name+' '+cities[0].name;
const cart=await call('/api/shipping/confirm/'+id,'POST',shipping);
const order=await call('/api/payment/pay/'+id,'POST',cart);
console.log(JSON.stringify({success:true,receipts,order}));
}catch(e){console.log(JSON.stringify({success:false,receipts,error:e.message}));process.exitCode=1}
})()
"""
if __name__=='__main__':
    assert [n['metadata']['name'] for n in json.loads(read(['get','nodes','-o','json']))['items']]==[NODE]
    p=subprocess.run(K+['exec','-n','robot-shop','deploy/web','--','node','-e',SCRIPT],capture_output=True,text=True,timeout=240)
    result=json.loads(p.stdout.strip());result['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();result['scope']='local kind; simulated payment gateway; synthetic credentials not exported'
    output=Path(__file__).resolve().parent/'evidence/runtime/shopping-flow.json';output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2));raise SystemExit(p.returncode)
