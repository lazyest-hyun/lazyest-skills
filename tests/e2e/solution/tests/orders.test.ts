import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {service,STARTER_MARKER} from '../src/orders.ts';
test('legacy success response stays usable',async()=>{
  const dir=mkdtempSync(join(tmpdir(),'order-starter-'));const app=service(dir);
  try { const result=await app.create({customerId:'c1',items:[{sku:'s1',quantity:1}],total:100,paymentToken:'tok_ok'});
    assert.equal(STARTER_MARKER,'synthetic-order-v1');assert.equal(result.code,201);assert.deepEqual(Object.keys(result.body).sort(),['orderId','status','total']);assert.equal(result.body.status,'paid');
  } finally {app.close();rmSync(dir,{recursive:true,force:true});}
});

import {DatabaseSync} from 'node:sqlite';
import {spawn} from 'node:child_process';
const order={customerId:'c1',items:[{sku:'s1',quantity:1}],total:100,paymentToken:'tok_ok'};
async function fixture(run:(app:ReturnType<typeof service>,dir:string)=>Promise<void>) {
  const dir=mkdtempSync(join(tmpdir(),'order-reliability-'));const app=service(dir);
  try {await run(app,dir);} finally {app.close();rmSync(dir,{recursive:true,force:true});}
}
function stored(dir:string,file:string,sql:string) {
  const db=new DatabaseSync(join(dir,file));try {return db.prepare(sql).all();} finally {db.close();}
}
test('same key replays one order and one payment, ignoring object order and unknown fields',()=>fixture(async(app,dir)=>{
  const first=await app.create({...order,extra:'ignored'},'same');
  const replay=await app.create({paymentToken:'tok_ok',total:100,items:[{quantity:1,sku:'s1',extra:123}],customerId:'c1'},'same');
  assert.deepEqual(replay,first);
  assert.equal(stored(dir,'orders.sqlite','SELECT * FROM orders').length,1);
  assert.equal(stored(dir,'gateway.sqlite','SELECT count FROM attempts')[0].count,1);
}));
test('changed accepted values conflict without charging or changing the original order',()=>fixture(async(app,dir)=>{
  const first=await app.create(order,'conflict');
  for(const body of [{...order,total:101},{...order,customerId:'c2'},{...order,paymentToken:'tok_decline'},{...order,items:[{sku:'s2',quantity:1}]}]) {
    const result=await app.create(body,'conflict');assert.equal(result.code,409);assert.deepEqual(Object.keys(result.body),['error']);
  }
  assert.deepEqual(app.get(first.body.orderId!),{...first,code:200});
  assert.equal(stored(dir,'gateway.sqlite','SELECT * FROM attempts').length,1);
}));
test('requests without keys remain independent and zero totals are valid',()=>fixture(async(app)=>{
  const first=await app.create({...order,total:0});const second=await app.create({...order,total:0});
  assert.equal(first.body.total,0);assert.equal(first.body.status,'paid');assert.notEqual(first.body.orderId,second.body.orderId);
}));
test('decline is terminal and retry never charges again',()=>fixture(async(app,dir)=>{
  const first=await app.create({...order,paymentToken:'tok_decline'},'decline');
  assert.equal(first.body.status,'failed');assert.deepEqual(await app.create({...order,paymentToken:'tok_decline'},'decline'),first);
  assert.equal(stored(dir,'gateway.sqlite','SELECT count FROM attempts')[0].count,1);
}));
test('timeout after accepted payment reconciles as paid without another attempt',()=>fixture(async(app,dir)=>{
  const body={...order,paymentToken:'tok_timeout_after'};const first=await app.create(body,'after');
  assert.equal(first.body.status,'paid');assert.deepEqual(await app.create(body,'after'),first);
  assert.equal(stored(dir,'gateway.sqlite','SELECT count FROM attempts')[0].count,1);
}));
test('timeout before acceptance stays pending then retries the original gateway key',()=>fixture(async(app,dir)=>{
  const body={...order,paymentToken:'tok_timeout_before'};const first=await app.create(body,'before');
  assert.equal(first.body.status,'pending');assert.equal(app.get(first.body.orderId!).body.status,'pending');
  const retry=await app.create(body,'before');assert.equal(retry.body.orderId,first.body.orderId);assert.equal(retry.body.status,'paid');
  assert.equal(stored(dir,'gateway.sqlite','SELECT * FROM charges').length,1);
  assert.equal(stored(dir,'gateway.sqlite','SELECT count FROM attempts')[0].count,2);
}));
test('simultaneous retries across service instances reserve one order and one accepted charge',()=>fixture(async(app,dir)=>{
  const other=service(dir);
  try {
    const results=await Promise.all(Array.from({length:12},(_,i)=>(i%2?app:other).create(order,'parallel')));
    assert.equal(new Set(results.map(x=>x.body.orderId)).size,1);assert.ok(results.every(x=>x.body.status==='paid'));
    assert.equal(stored(dir,'orders.sqlite','SELECT * FROM orders').length,1);
    assert.equal(stored(dir,'gateway.sqlite','SELECT * FROM charges').length,1);
  } finally {other.close();}
}));
test('pending and terminal orders survive restart',async()=>{
  const dir=mkdtempSync(join(tmpdir(),'order-restart-'));let app=service(dir);
  try {
    const body={...order,paymentToken:'tok_timeout_before'};const pending=await app.create(body,'restart');app.close();app=service(dir);
    const paid=await app.create(body,'restart');assert.equal(paid.body.orderId,pending.body.orderId);assert.equal(paid.body.status,'paid');
    app.close();app=service(dir);assert.deepEqual(await app.create(body,'restart'),paid);
    assert.equal(stored(dir,'orders.sqlite','SELECT * FROM orders').length,1);
  } finally {app.close();rmSync(dir,{recursive:true,force:true});}
});
test('validation rejects invalid requests without reserving a key or charging',()=>fixture(async(app,dir)=>{
  for(const body of [null,{}, {...order,customerId:' '},{...order,items:[]},{...order,items:[{sku:'s1',quantity:0}]},{...order,items:[{sku:'s1',quantity:1.5}]},{...order,total:-1},{...order,total:0.1},{...order,paymentToken:'unsupported'}]) {
    assert.equal((await app.create(body,'invalid')).code,400);
  }
  assert.equal(stored(dir,'orders.sqlite','SELECT * FROM orders').length,0);
  assert.equal(stored(dir,'gateway.sqlite','SELECT * FROM attempts').length,0);
  assert.equal((await app.create(order,'invalid')).body.status,'paid');
  assert.deepEqual(app.get('missing'),{code:404,body:{error:'not found'}});
}));
test('pending order reconciles payment accepted before process interruption',()=>fixture(async(app,dir)=>{
  const body={...order,paymentToken:'tok_timeout_before'};const pending=await app.create(body,'interrupted');
  const db=new DatabaseSync(join(dir,'gateway.sqlite'));
  db.prepare('INSERT INTO charges(key,amount,outcome) VALUES(?,?,?)').run(pending.body.orderId!,100,'paid');db.close();
  const result=await app.create(body,'interrupted');assert.equal(result.body.status,'paid');assert.equal(result.body.orderId,pending.body.orderId);
  assert.equal(stored(dir,'gateway.sqlite','SELECT count FROM attempts')[0].count,1);
}));
test('separate processes sharing persistence cannot reserve duplicate keyed orders',()=>fixture(async(_app,dir)=>{
  const source=`import {service} from './src/orders.ts';const app=service(process.argv[1]);try {console.log(JSON.stringify(await app.create(${JSON.stringify(order)},'processes')));} finally {app.close();}`;
  const run=()=>new Promise<any>((resolve,reject)=>{
    const child=spawn(process.execPath,['--input-type=module','-e',source,dir],{cwd:process.cwd(),stdio:['ignore','pipe','pipe']});let out='';let err='';
    child.stdout.on('data',x=>out+=x);child.stderr.on('data',x=>err+=x);child.on('error',reject);
    child.on('exit',code=>{if(code===0) {try {resolve(JSON.parse(out));} catch(error) {reject(error);}} else reject(new Error(err));});
  });
  const results=await Promise.all(Array.from({length:6},run));
  assert.equal(new Set(results.map(x=>x.body.orderId)).size,1);assert.ok(results.every(x=>x.body.status==='paid'));
  assert.equal(stored(dir,'orders.sqlite','SELECT * FROM orders').length,1);assert.equal(stored(dir,'gateway.sqlite','SELECT * FROM charges').length,1);
}));
