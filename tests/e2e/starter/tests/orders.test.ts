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
