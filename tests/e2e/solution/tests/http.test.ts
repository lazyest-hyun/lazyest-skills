import test from 'node:test';
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {createServer} from 'node:net';
import {mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {setTimeout} from 'node:timers/promises';

test('loopback HTTP preserves health, create, replay, conflict, get and failure contracts',async()=>{
  const probe=createServer();await new Promise<void>(resolve=>probe.listen(0,'127.0.0.1',resolve));
  const port=(probe.address() as {port:number}).port;await new Promise<void>((resolve,reject)=>probe.close(error=>error?reject(error):resolve()));
  const dir=mkdtempSync(join(tmpdir(),'order-http-'));
  const child=spawn(process.execPath,['src/server.ts'],{env:{...process.env,PORT:String(port),DATA_DIR:dir},stdio:['ignore','ignore','pipe']});
  let stderr='';child.stderr.on('data',data=>stderr+=data);
  const exited=new Promise<void>((resolve,reject)=>{child.on('error',reject);child.on('exit',()=>resolve());});
  const url=`http://127.0.0.1:${port}`;
  const body={customerId:'c1',items:[{sku:'s1',quantity:1}],total:100,paymentToken:'tok_ok'};
  const post=async(payload:unknown,key?:string)=>{
    const response=await fetch(`${url}/orders`,{method:'POST',headers:{'Content-Type':'application/json',...(key===undefined?{}:{'Idempotency-Key':key})},body:JSON.stringify(payload)});
    return {code:response.status,body:await response.json()};
  };
  try {
    let ready=false;
    for(let i=0;i<100;i++) {
      if(child.exitCode!==null) throw new Error(`Server exited: ${stderr}`);
      try {const health=await fetch(`${url}/health`);assert.equal(health.status,200);assert.deepEqual(await health.json(),{ok:true});ready=true;break;} catch {await setTimeout(20);}
    }
    assert.ok(ready,`Server failed to start: ${stderr}`);
    const results=await Promise.all(Array.from({length:8},()=>post(body,'http')));
    const first=results[0];assert.equal(first.code,201);assert.equal(first.body.status,'paid');assert.deepEqual(Object.keys(first.body).sort(),['orderId','status','total']);
    assert.ok(results.every(x=>x.body.orderId===first.body.orderId));assert.deepEqual(await post(body,'http'),first);
    assert.equal((await post({...body,total:101},'http')).code,409);
    const get=await fetch(`${url}/orders/${first.body.orderId}`);assert.equal(get.status,200);assert.deepEqual(await get.json(),first.body);
    const missing=await fetch(`${url}/orders/missing`);assert.equal(missing.status,404);assert.deepEqual(await missing.json(),{error:'not found'});
    assert.equal((await post({...body,paymentToken:'tok_decline'},'decline')).body.status,'failed');
    assert.equal((await post({...body,paymentToken:'tok_timeout_after'},'after')).body.status,'paid');
    const pending=await post({...body,paymentToken:'tok_timeout_before'},'before');assert.equal(pending.body.status,'pending');
    const recovered=await post({...body,paymentToken:'tok_timeout_before'},'before');assert.equal(recovered.body.orderId,pending.body.orderId);assert.equal(recovered.body.status,'paid');
    assert.equal((await post({...body,total:-1},'invalid')).code,400);
    const malformed=await fetch(`${url}/orders`,{method:'POST',body:'{'});assert.equal(malformed.status,400);assert.deepEqual(Object.keys(await malformed.json()),['error']);
    const legacy1=await post(body);const legacy2=await post(body);assert.notEqual(legacy1.body.orderId,legacy2.body.orderId);
  } finally {child.kill('SIGTERM');await exited;rmSync(dir,{recursive:true,force:true});}
});
