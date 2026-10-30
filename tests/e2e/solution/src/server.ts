import {createServer} from 'node:http';
import {service} from './orders.ts';
const app=service(process.env.DATA_DIR??'./data');
const server=createServer(async(req,res)=>{
  try {
    let result;
    if(req.method==='GET' && req.url==='/health') result={code:200,body:{ok:true}};
    else if(req.method==='POST' && req.url==='/orders') {
      const chunks=[];for await(const chunk of req) chunks.push(chunk);
      const body=JSON.parse(Buffer.concat(chunks).toString());
      result=await app.create(body,typeof req.headers['idempotency-key']==='string'?req.headers['idempotency-key']:undefined);
    } else if(req.method==='GET' && req.url?.startsWith('/orders/')) result=app.get(req.url.slice(8));
    else result={code:404,body:{error:'not found'}};
    res.writeHead(result.code,{'Content-Type':'application/json'});res.end(JSON.stringify(result.body));
  } catch {res.writeHead(400,{'Content-Type':'application/json'});res.end(JSON.stringify({error:'invalid request'}));}
});
server.listen(Number(process.env.PORT??8080),'0.0.0.0');
process.on('SIGTERM',()=>server.close(()=>{app.close();process.exit(0);}));
