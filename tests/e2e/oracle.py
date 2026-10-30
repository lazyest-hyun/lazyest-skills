"""Independent HTTP oracle for a synthetic exercise; loopback only."""
import concurrent.futures
import json
import os
from pathlib import Path
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.error
import urllib.request

PROJECT = Path(sys.argv.pop(1)).resolve() if len(sys.argv)>1 and not sys.argv[1].startswith('-') else Path(__file__).parent/'solution'
BODY={'customerId':'c1','items':[{'sku':'s1','quantity':1}],'total':100,'paymentToken':'tok_ok'}

class HTTPOracle(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.directory=Path(self.temp.name)
        self.process=None
        self.start()
    def start(self):
        with socket.socket() as sock:
            sock.bind(('127.0.0.1',0));self.port=sock.getsockname()[1]
        env=dict(os.environ,PORT=str(self.port),DATA_DIR=str(self.directory))
        self.log=open(self.directory/'server.log','ab')
        self.process=subprocess.Popen(['node','src/server.ts'],cwd=PROJECT,env=env,stdout=self.log,stderr=self.log)
        for _ in range(100):
            if self.process.poll() is not None:
                raise AssertionError('server exited: '+(self.directory/'server.log').read_text())
            try:
                if self.request('GET','/health')[0]==200:return
            except (OSError,urllib.error.URLError):pass
            time.sleep(.03)
        raise AssertionError('server did not become ready')
    def stop(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:self.process.kill();self.process.wait(timeout=5)
        self.log.close()
    def tearDown(self):
        self.stop();self.temp.cleanup()
    def request(self,method,path,body=None,key=None):
        headers={'Content-Type':'application/json'}
        if key is not None:headers['Idempotency-Key']=key
        req=urllib.request.Request(f'http://127.0.0.1:{self.port}'+path,data=json.dumps(body).encode() if body is not None else None,headers=headers,method=method)
        try:
            with urllib.request.urlopen(req,timeout=10) as result:return result.status,json.load(result)
        except urllib.error.HTTPError as error:return error.code,json.load(error)
    def create(self,body=None,key='one'):
        return self.request('POST','/orders',body if body is not None else BODY,key)
    def gateway_counts(self):
        with sqlite3.connect(self.directory/'gateway.sqlite') as db:
            return db.execute('select count(*) from charges where outcome="paid"').fetchone()[0],db.execute('select coalesce(sum(count),0) from attempts').fetchone()[0]
    def assert_shape(self,result):
        code,body=result;self.assertEqual(code,201);self.assertEqual(set(body),{'orderId','status','total'});self.assertIsInstance(body['orderId'],str);self.assertTrue(body['orderId']);self.assertIs(type(body['total']),int)
    def test_legacy_and_response_contract(self):
        first=self.create(key=None);second=self.create(key=None)
        self.assert_shape(first);self.assert_shape(second);self.assertNotEqual(first[1]['orderId'],second[1]['orderId'])
        self.assertEqual(self.request('GET','/orders/'+first[1]['orderId']),(200,first[1]))
        self.assertEqual(self.request('GET','/orders/not-real'),(404,{'error':'not found'}))
        self.assertEqual(self.request('GET','/health'),(200,{'ok':True}))
    def test_replay_identity_ignores_field_order_and_extra_properties(self):
        first=self.create(); replay=self.create(dict(reversed(list(BODY.items())))|{'ignored':'x'})
        self.assert_shape(first);self.assertEqual(replay,first);self.assertEqual(self.gateway_counts(),(1,1))
    def test_same_key_different_payload_conflicts(self):
        self.create();code,body=self.create(BODY|{'total':101})
        self.assertEqual(code,409);self.assertEqual(set(body),{'error'});self.assertEqual(self.gateway_counts(),(1,1))
    def test_concurrent_replays_make_one_order_and_one_charge(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
            results=list(pool.map(lambda _:self.create(key='concurrent'),range(12)))
        for result in results:self.assert_shape(result)
        self.assertEqual(len({r[1]['orderId'] for r in results}),1)
        self.assertEqual(self.gateway_counts()[0],1)
    def test_decline_is_terminal_and_not_recharged(self):
        body=BODY|{'paymentToken':'tok_decline'}
        first=self.create(body);self.assert_shape(first);self.assertEqual(first[1]['status'],'failed')
        self.assertEqual(self.create(body),first);self.assertEqual(self.gateway_counts(),(0,1))
    def test_timeout_after_charge_reconciles_without_recharge_after_restart(self):
        body=BODY|{'paymentToken':'tok_timeout_after'}
        first=self.create(body);self.assert_shape(first);self.assertIn(first[1]['status'],('pending','paid'))
        self.assertEqual(self.gateway_counts(),(1,1));self.stop();self.start()
        replay=self.create(body);self.assertEqual(replay[1]['orderId'],first[1]['orderId']);self.assertEqual(replay[1]['status'],'paid');self.assertEqual(self.gateway_counts(),(1,1))
    def test_timeout_before_charge_retries_same_order_safely(self):
        body=BODY|{'paymentToken':'tok_timeout_before'}
        first=self.create(body);self.assertEqual(first[1]['status'],'pending');self.assertEqual(self.gateway_counts(),(0,1))
        replay=self.create(body);self.assertEqual(replay[1]['orderId'],first[1]['orderId']);self.assertEqual(replay[1]['status'],'paid');self.assertEqual(self.gateway_counts(),(1,2))
    def test_completed_key_survives_restart(self):
        first=self.create();self.stop();self.start();self.assertEqual(self.create(),first);self.assertEqual(self.gateway_counts(),(1,1))
    def test_invalid_inputs_and_zero_total(self):
        for patch in ({'total':None},{'total':'0'},{'total':True},{'total':-1},{'items':[]},{'items':[{'sku':'s1','quantity':0}]},{'customerId':''}):
            with self.subTest(patch=patch):
                code,body=self.create(BODY|patch,key='invalid');self.assertEqual(code,400);self.assertEqual(set(body),{'error'})
        result=self.create(BODY|{'total':0},key='valid-zero');self.assert_shape(result);self.assertEqual(result[1]['total'],0);self.assertEqual(result[1]['status'],'paid')

if __name__=='__main__':unittest.main(verbosity=2)
