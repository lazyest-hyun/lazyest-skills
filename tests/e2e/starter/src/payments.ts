import {DatabaseSync} from 'node:sqlite';
import {mkdirSync} from 'node:fs';
import {join} from 'node:path';
import {setTimeout} from 'node:timers/promises';

export const TOKENS = new Set(['tok_ok','tok_decline','tok_timeout_after','tok_timeout_before']);
export function gateway(directory: string) {
  mkdirSync(directory,{recursive:true});
  const db = new DatabaseSync(join(directory,'gateway.sqlite'));
  db.exec('PRAGMA busy_timeout=3000; CREATE TABLE IF NOT EXISTS attempts (key TEXT PRIMARY KEY, count INTEGER NOT NULL); CREATE TABLE IF NOT EXISTS charges (key TEXT PRIMARY KEY, amount INTEGER NOT NULL, outcome TEXT NOT NULL)');
  return {
    lookup(key: string): string {
      const row=db.prepare('SELECT outcome FROM charges WHERE key=?').get(key);
      return row ? String(row.outcome) : 'not_found';
    },
    async charge(key: string, amount: number, token: string): Promise<string> {
      db.prepare('INSERT INTO attempts(key,count) VALUES(?,1) ON CONFLICT(key) DO UPDATE SET count=count+1').run(key);
      await setTimeout(15);
      const existing=db.prepare('SELECT amount,outcome FROM charges WHERE key=?').get(key);
      if(existing) { if(existing.amount!==amount) throw new Error('gateway key conflict'); return String(existing.outcome); }
      const attempts=Number(db.prepare('SELECT count FROM attempts WHERE key=?').get(key)!.count);
      if(token==='tok_timeout_before' && attempts===1) throw new Error('uncertain timeout');
      const outcome=token==='tok_decline' ? 'declined' : 'paid';
      db.prepare('INSERT OR IGNORE INTO charges(key,amount,outcome) VALUES(?,?,?)').run(key,amount,outcome);
      if(token==='tok_timeout_after' && attempts===1) throw new Error('uncertain timeout');
      return outcome;
    },
    close() { db.close(); }
  };
}
