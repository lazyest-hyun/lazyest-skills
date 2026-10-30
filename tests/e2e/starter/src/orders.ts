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
  const payment=gateway(directory);
  function response(row: any) {return {orderId:row.id,status:row.status,total:row.total};}
  return {
    async create(body: any, key?: string) {
      if(!body || typeof body.customerId!=='string' || !body.customerId.trim() || !Array.isArray(body.items) || !body.items.length || body.items.some((x:any)=>!x || typeof x.sku!=='string' || !x.sku || !Number.isInteger(x.quantity) || x.quantity<=0) || !Number.isInteger(body.total) || body.total<0 || !TOKENS.has(body.paymentToken)) {
        return {code:400,body:{error:'invalid order'}};
      }
      const id=randomUUID();
      db.prepare('INSERT INTO orders(id,request_key,payload,total,status) VALUES(?,?,?,?,?)').run(id,key??null,JSON.stringify(body),body.total,'pending');
      try {
        const status=await payment.charge(id,body.total,body.paymentToken);
        db.prepare('UPDATE orders SET status=? WHERE id=?').run(status==='paid'?'paid':'failed',id);
      } catch {
        db.prepare('UPDATE orders SET status=? WHERE id=?').run('failed',id);
      }
      return {code:201,body:response(db.prepare('SELECT * FROM orders WHERE id=?').get(id))};
    },
    get(id:string) {const row=db.prepare('SELECT * FROM orders WHERE id=?').get(id);return row ? {code:200,body:response(row)} : {code:404,body:{error:'not found'}};},
    close() {payment.close();db.close();}
  };
}
