// Pure server-side payload builder, NOT a public endpoint or active CAPI sender.
// Call only after server-side validation of an authenticated consent receipt.
export function buildMetaEvent({name,eventId,time,url,consent,userAgent,fbp,fbc}){
 if(consent!==true)throw new Error('Verified advertising consent required');
 if(!['PageView','ViewContent','Contact'].includes(name))throw new Error('Unsupported event; Purchase requires a verified booking integration');
 if(!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(eventId||''))throw new Error('Shared browser/server event ID required');
 const now=Math.floor(Date.now()/1000);if(!Number.isInteger(time)||time>now+60||time<now-604800)throw new Error('Invalid event time');
 const parsed=new URL(url);if(parsed.origin!=='https://hornigold.pl'||parsed.search||parsed.hash||parsed.username||parsed.password)throw new Error('Only clean canonical production URLs allowed');
 if(typeof userAgent!=='string'||!userAgent.trim()||userAgent.length>1024)throw new Error('Valid user agent required');
 const user_data={client_user_agent:userAgent};
 for(const [key,value] of Object.entries({fbp,fbc}))if(value!==undefined){if(typeof value!=='string'||!/^fb\.\d+\.\d+\.[A-Za-z0-9_-]{1,500}$/.test(value))throw new Error('Invalid Meta identifier');user_data[key]=value;}
 return {event_name:name,event_time:time,event_source_url:parsed.href,action_source:'website',event_id:eventId,user_data};
}
