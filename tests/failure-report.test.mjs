import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const workflow=readFileSync(new URL('../.github/workflows/report-failure.yml',import.meta.url),'utf8');
const script=workflow.split('          script: |\n')[1].split('\n').map(line=>line.replace(/^            /,'')).join('\n');
const execute=new (Object.getPrototypeOf(async function(){}).constructor)('context','github',script);

async function exercise({controlled=false,titleOnly=false,existing=[]}={}) {
  const writes=[];
  const run={id:12,workflow_id:34,head_branch:'main',head_sha:'a'.repeat(40),name:'Hornigold quality',display_title:controlled||titleOnly?'[TEST ALARMU] Hornigold quality':'Hornigold quality',html_url:'https://github.com/example/repo/actions/runs/12'};
  const jobs=[{name:'quality',conclusion:'failure',steps:[{name:controlled?'Controlled alarm self-test':'Build',conclusion:'failure'}]}];
  const rest={actions:{listJobsForWorkflowRun:()=>{}},issues:{listForRepo:()=>{},create:async value=>writes.push({type:'create',...value}),update:async value=>writes.push({type:'update',...value})}};
  await execute({repo:{owner:'example',repo:'repo'},payload:{workflow_run:run}},{rest,paginate:async method=>method===rest.actions.listJobsForWorkflowRun?jobs:existing});
  return writes;
}

test('controlled alarm creates clearly labelled test without replacing real incident',async()=>{
  const writes=await exercise({controlled:true,existing:[{number:1,body:'<!-- hornigold-quality:34:main -->'}]});
  assert.equal(writes.length,1);assert.equal(writes[0].type,'create');
  assert.match(writes[0].title,/^\[TEST ALARMU\]/);assert.match(writes[0].body,/:controlled-test -->/);
  assert.match(writes[0].body,/brak rzeczywistej awarii/);
});
test('repeated controlled alarm updates only the previous test',async()=>{
  const writes=await exercise({controlled:true,existing:[{number:2,body:'<!-- hornigold-quality:34:main:controlled-test -->'}]});
  assert.equal(writes[0].type,'update');assert.equal(writes[0].issue_number,2);
});
test('real failure remains a real incident',async()=>{
  const writes=await exercise();assert.match(writes[0].title,/^\[Kontrola\]/);
  assert.doesNotMatch(writes[0].body,/controlled-test|brak rzeczywistej awarii/);
});
test('test title alone cannot relabel a genuine failing step',async()=>{
  const writes=await exercise({titleOnly:true});assert.match(writes[0].title,/^\[Kontrola\]/);
  assert.doesNotMatch(writes[0].body,/:controlled-test/);
});
