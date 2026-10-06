// Prepare an existing Sites checkout from the single repository source.
import {cp,mkdir,readFile,writeFile,rm} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const release=JSON.parse(await readFile(path.join(root,'_site/release.json'),'utf8'));
if(release.base!=='/'||!release.counterEnabled)throw Error('Run build.py --base / --counter first');
const manifest=JSON.parse(await readFile(path.join(root,'.openai/hosting.json'),'utf8'));
if(manifest.project_id!=='appgprj_6ac24ff4d7d08191aef99366bb3d966f')throw Error('Unexpected Site project');
await rm(path.join(root,'dist'),{recursive:true,force:true});
await mkdir(path.join(root,'dist/server'),{recursive:true});await mkdir(path.join(root,'dist/.openai'),{recursive:true});
await cp(path.join(root,'_site'),path.join(root,'dist/client'),{recursive:true});
for(const f of ['worker.mjs','counter.mjs','routes.mjs'])await cp(path.join(root,'server',f),path.join(root,'dist/server',f==='worker.mjs'?'index.js':f));
await cp(path.join(root,'.openai/hosting.json'),path.join(root,'dist/.openai/hosting.json'));
await writeFile(path.join(root,'dist/server/wrangler.json'),JSON.stringify({name:'hornigold-review',main:'index.js',compatibility_date:'2026-05-15',assets:{directory:'../client',binding:'ASSETS',run_worker_first:true,not_found_handling:'404-page'},d1_databases:[{binding:'DB',database_name:'hornigold-counter',database_id:'00000000-0000-0000-0000-000000000000',migrations_dir:'../../drizzle'}]},null,2));
console.log('Prepared unified v23 Sites artifact; existing DB binding retained.');
