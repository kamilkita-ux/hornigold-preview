// Local QA adapter only: exercises the same Worker against SQLite and static assets.
import {createServer} from 'node:http';
import {DatabaseSync} from 'node:sqlite';
import {readFile,stat} from 'node:fs/promises';
import {readFileSync} from 'node:fs';
import path from 'node:path';
import worker from '../server/worker.mjs';
const root=path.resolve('_site'),port=Number(process.env.PORT||4334);const sql=new DatabaseSync(':memory:');
sql.exec(readFileSync('drizzle/0000_quiet_overlord.sql','utf8'));
const DB={prepare(q){return {bind(...args){return {async first(){return sql.prepare(q).get(...args)??null}}}}}};
const types={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json','.pdf':'application/pdf','.xml':'application/xml','.txt':'text/plain','.png':'image/png','.jpg':'image/jpeg','.webp':'image/webp','.svg':'image/svg+xml','.woff2':'font/woff2'};
const ASSETS={async fetch(req){const u=new URL(req.url);let p;try{p=path.resolve(root,'.'+decodeURIComponent(u.pathname))}catch{return new Response('Bad path',{status:400})};if(p!==root&&!p.startsWith(root+path.sep))return new Response('Forbidden',{status:403});
 try{if((await stat(p)).isDirectory())p=path.join(p,'index.html')}catch{if(!path.extname(p))p+='.html'}
 try{return new Response(req.method==='HEAD'?null:await readFile(p),{headers:{'Content-Type':types[path.extname(p)]||'application/octet-stream'}})}catch{return new Response('Not found',{status:404})}
}};
createServer(async(req,res)=>{try{const request=new Request('http://'+req.headers.host+req.url,{method:req.method,headers:req.headers});const r=await worker.fetch(request,{DB,ASSETS});res.writeHead(r.status,Object.fromEntries(r.headers));res.end(Buffer.from(await r.arrayBuffer()));}catch{res.writeHead(500);res.end('QA adapter error')}}).listen(port,'127.0.0.1',()=>console.log('Local http://127.0.0.1:'+port));
