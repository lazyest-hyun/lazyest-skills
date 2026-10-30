import {DatabaseSync} from 'node:sqlite';
import {mkdirSync} from 'node:fs';
import {join} from 'node:path';
import {randomUUID} from 'node:crypto';
import {gateway,TOKENS} from './payments.ts';

export const STARTER_MARKER='synthetic-order-v1';
export function service(directory: string) {
  mkdirSync(directory,{recursive:true});
  const db=new DatabaseSync(join(directory,'orders.sqlite'));
  db.exec('PRAGMA busy_timeout=3000; CREATE TABLE IF NOT EXISTS orders (id TEXT PRIMARY KEY, request_key TEXT, payload TEXT NOT NULL, total INTEGER NOT NULL, status TEXT NOT NULL)');
  db.exec('CREATE INDEX IF NOT EXISTS orders_request_key ON orders(request_key)');
  const payment=gateway(directory);
  // Only accepted fields define identity; unknown properties and object order do not.
  function payload(body: any) {
    return JSON.stringify({customerId:body.customerId,items:body.items.map((item:any)=>({sku:item.sku,quantity:item.quantity})),total:body.total,paymentToken:body.paymentToken});
  }
  function response(row: any) {return {orderId:row.id,status:row.status,total:row.total};}
  return {
    async create(body: any, key?: string) {
      if(!body || typeof body.customerId!=='string' || !body.customerId.trim() || !Array.isArray(body.items) || !body.items.length || body.items.some((x:any)=>!x || typeof x.sku!=='string' || !x.sku || !Number.isInteger(x.quantity) || x.quantity<=0) || !Number.isInteger(body.total) || body.total<0 || !TOKENS.has(body.paymentToken)) {
        return {code:400,body:{error:'invalid order'}};
      }
      const accepted=payload(body);
      let row: any;
      // Reserve the order before awaiting the independent payment side effect.
      // BEGIN IMMEDIATE also serializes reservations from other service processes.
      db.exec('BEGIN IMMEDIATE');
      try {
        if(key!==undefined) row=db.prepare('SELECT * FROM orders WHERE request_key=? ORDER BY rowid LIMIT 1').get(key);
        if(row && payload(JSON.parse(row.payload))!==accepted) {
          db.exec('COMMIT');
          return {code:409,body:{error:'idempotency key conflict'}};
        }
        if(!row) {
          const id=randomUUID();
          db.prepare('INSERT INTO orders(id,request_key,payload,total,status) VALUES(?,?,?,?,?)').run(id,key??null,accepted,body.total,'pending');
          row=db.prepare('SELECT * FROM orders WHERE id=?').get(id);
        }
        db.exec('COMMIT');
      } catch(error) {
        db.exec('ROLLBACK');
        throw error;
      }
      if(row.status==='pending') {
        let outcome=payment.lookup(row.id);
        if(outcome==='not_found') {
          try {outcome=await payment.charge(row.id,row.total,body.paymentToken);}
          catch {outcome=payment.lookup(row.id);}
        }
        // A timeout alone cannot prove failure. Never overwrite a final outcome
        // with a concurrent request's stale pending observation.
        if(outcome==='paid' || outcome==='declined') {
          db.prepare("UPDATE orders SET status=? WHERE id=? AND status='pending'").run(outcome==='paid'?'paid':'failed',row.id);
        }
      }
      return {code:201,body:response(db.prepare('SELECT * FROM orders WHERE id=?').get(row.id))};
    },
    get(id:string) {const row=db.prepare('SELECT * FROM orders WHERE id=?').get(id);return row ? {code:200,body:response(row)} : {code:404,body:{error:'not found'}};},
    close() {payment.close();db.close();}
  };
}
