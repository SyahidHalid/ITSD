const U=(()=>{
const files={summary:'udx_run_summary.JSON',golden:'sme_golden_records.JSON',financing:'financing_potential_leads.JSON',training:'development_training_potential.JSON'};
const keys={summary:'udx.summary',golden:'udx.golden',financing:'udx.financing',training:'udx.training'};
const $=(s,r=document)=>r.querySelector(s), $$=(s,r=document)=>[...r.querySelectorAll(s)];
const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const v=x=>x===null||x===undefined||String(x).trim()===''?'—':String(x);
const n=x=>Number(x||0).toLocaleString('en-MY');
const money=x=>x==null||x===''?'—':(Number.isFinite(Number(x))?'RM '+Number(x).toLocaleString('en-MY',{maximumFractionDigits:2}):String(x));
// Large datasets belong in IndexedDB, not localStorage. Keep a small in-memory
// cache for synchronous detail/modal lookups, and use the JSON files as fallback.
const memory={};
const DB_NAME='sme-intelligence-hub';
const DB_VERSION=1;
const STORE_NAME='datasets';
let dbPromise;
function openDB(){
 if(!('indexedDB' in window))return Promise.reject(new Error('IndexedDB is not supported by this browser.'));
 if(!dbPromise)dbPromise=new Promise((resolve,reject)=>{
  const req=indexedDB.open(DB_NAME,DB_VERSION);
  req.onupgradeneeded=()=>{const db=req.result;if(!db.objectStoreNames.contains(STORE_NAME))db.createObjectStore(STORE_NAME,{keyPath:'key'});};
  req.onsuccess=()=>resolve(req.result);req.onerror=()=>reject(req.error||new Error('Could not open IndexedDB.'));
 });
 return dbPromise;
}
async function dbGet(k){const db=await openDB();return new Promise((resolve,reject)=>{const req=db.transaction(STORE_NAME,'readonly').objectStore(STORE_NAME).get(k);req.onsuccess=()=>resolve(req.result?req.result.data:null);req.onerror=()=>reject(req.error||new Error('Could not read dataset from IndexedDB.'));});}
async function dbPut(k,d){const db=await openDB();return new Promise((resolve,reject)=>{const tx=db.transaction(STORE_NAME,'readwrite');tx.objectStore(STORE_NAME).put({key:k,data:d,updatedAt:new Date().toISOString()});tx.oncomplete=()=>resolve();tx.onerror=()=>reject(tx.error||new Error('Could not save dataset to IndexedDB.'));tx.onabort=()=>reject(tx.error||new Error('Dataset storage transaction was aborted.'));});}
async function put(k,d){memory[k]=d;try{await dbPut(k,d);return {persisted:true};}catch(e){return {persisted:false,error:e};}}
function get(k){return Object.prototype.hasOwnProperty.call(memory,k)?memory[k]:null;}
async function clearAll(){Object.keys(memory).forEach(k=>delete memory[k]);try{const db=await openDB();await new Promise((resolve,reject)=>{const tx=db.transaction(STORE_NAME,'readwrite');tx.objectStore(STORE_NAME).clear();tx.oncomplete=resolve;tx.onerror=()=>reject(tx.error);tx.onabort=()=>reject(tx.error);});}catch(e){console.warn('Could not clear IndexedDB datasets:',e);}}
async function load(k,force=false){
 if(!force&&get(k)!==null)return get(k);
 if(!force){try{const saved=await dbGet(k);if(saved!==null&&saved!==undefined){memory[k]=saved;return saved;}}catch(e){console.warn('IndexedDB read unavailable; will try JSON file:',e);}}
 try{const r=await fetch(files[k],{cache:'no-store'});if(!r.ok)throw Error('HTTP '+r.status);const d=await r.json();memory[k]=d;const result=await put(k,d);if(!result.persisted)console.warn('Dataset loaded for this session but could not be persisted in IndexedDB:',result.error);return d;}
 catch(e){if(get(k)!==null)return get(k);console.warn('Could not load dataset '+files[k]+':',e);return null;}
}
async function all(){const a=await Promise.all(Object.keys(files).map(k=>load(k)));return Object.fromEntries(Object.keys(files).map((k,i)=>[k,a[i]]))}
function rows(d,k){if(!d)return[];let a=k==='golden'?['GOLDEN_RECORDS']:k==='financing'?['FINANCING_POTENTIAL_LEADS']:['DEVELOPMENT_TRAINING_POTENTIAL','TRAINING_POTENTIAL_LEADS','DEVELOPMENT_TRAINING_LEADS'];for(let x of a)if(Array.isArray(d[x]))return d[x];return[]}
function shell(){let nav=[['index.html','main','⌂','Main'],['sme_master_profile_v7.html','master','▦','Master Profile'],['financing_potential_lead_v2.html','financing','↗','Financing Opportunity'],['training_potential_v2.html','training','✦','Development & Training']];document.body.innerHTML=`<div class="app"><aside class="sidebar"><div class="brand"><b>IH</b>SME Intelligence Hub<small>SME DATA & LEAD PLATFORM</small></div><div class="nav-label">Workspace</div><nav class="navs">${nav.map(a=>`<a class="nav-link ${a[1]===document.body.dataset.page?'active':''}" href="${a[0]}">${a[2]} &nbsp; ${a[3]}</a>`).join('')}</nav><div class="dataset-nav"><div class="nav-label">Administration</div><a class="nav-link ${document.body.dataset.page==='dataset'?'active':''}" href="dataset_manager.html">⚙ &nbsp; Dataset Manager</a></div><div class="sidefoot">SME Intelligence Hub<br>Prototype · v1.0</div></aside><main class="main"><header class="topbar"><span>SME Intelligence Hub / <span id="crumb">Workspace</span></span><strong>SME Intelligence Hub</strong></header><div class="content" id="content">Loading…</div></main></div>`}
function page(t,h){$('#crumb').textContent=t;$('#content').innerHTML=h}
function chips(a){return `<div class="chips">${(a||[]).map(x=>`<span class="chip">${esc(x)}</span>`).join('')||'—'}</div>`}
function pill(t,c=''){return `<span class="status ${c}">${esc(t)}</span>`}
function head(k,t,p,button=''){return `<div class="head"><div><div class="eyebrow">SME Intelligence Hub</div><h1>${t}</h1><p>${p}</p></div>${button?`<button class="btn primary" id="${button}">↻ Reload JSON</button>`:''}</div>`}
function uploadCards(d){let a=[['summary','Run Summary','udx_run_summary.JSON','Engine run metadata and source coverage'],['golden','SME Golden Records','sme_golden_records.JSON','Master profiles, match confidence and provenance'],['financing','Financing Potential Leads','financing_potential_leads.JSON','Candidate financing leads and criteria'],['training','Development & Training','development_training_potential.JSON','Candidate training leads and criteria']];return `<div class="grid uploadgrid">${a.map(([k,t,f,desc])=>`<div class="card upload"><h3>${t}</h3><div class="filename">${f}</div><div class="muted">${desc}</div><div style="margin-top:10px">${d[k]?pill('Loaded'+(k==='summary'?'':` · ${n(rows(d[k],k).length)} records`),'ok'):pill('Not loaded','warn')}</div><input type="file" accept=".json,.JSON,application/json" data-upload="${k}"><div class="muted">Choose replacement JSON, if needed.</div><button class="btn" style="margin-top:9px" data-reload="${k}">Reload file from folder</button></div>`).join('')}</div>`}
function arrRows(d,k){
 if(Array.isArray(d))return d;
 if(!d||typeof d!=='object')return [];
 const candidates=k==='golden'?['GOLDEN_RECORDS','golden_records','records','data']:
  k==='financing'?['FINANCING_POTENTIAL_LEADS','financing_potential_leads','leads','records','data']:
  ['DEVELOPMENT_TRAINING_POTENTIAL','TRAINING_POTENTIAL_LEADS','DEVELOPMENT_TRAINING_LEADS','development_training_potential','training_potential_leads','leads','records','data'];
 for(const x of candidates)if(Array.isArray(d[x]))return d[x];
 return [];
}
function rows(d,k){return arrRows(d,k)}
function field(x,names){for(const name of names){if(x&&x[name]!==undefined&&x[name]!==null&&String(x[name]).trim()!=='')return x[name]}return null}
function metricValue(x,names){return field(x,names)}
function fmtCount(x){return x===null||x===undefined?'NA':n(x)}
function pct(part,total){return total?`${(100*part/total).toFixed(1)}%`:'NA'}
function aggregate(records, names, fallback='NA'){
 if(!records.length)return [];
 const vals=records.map(x=>field(x,names));
 if(vals.every(x=>x===null))return [];
 const m=new Map();for(const val of vals){if(val===null)continue;const label=String(val).trim();m.set(label,(m.get(label)||0)+1)}
 return [...m.entries()].sort((a,b)=>b[1]-a[1]);
}
function chartRows(items,max){if(!items.length)return '<p class="muted">NA — required data is not available in the loaded JSON files.</p>';return items.map(([label,val])=>`<div class="chart-row"><div class="chart-label"><span>${esc(label)}</span><b>${esc(n(val))}</b></div><div class="chart-track"><span style="width:${Math.max(0,Math.min(100,100*Number(val)/Math.max(1,max)))}%"></span></div></div>`).join('')}
const chartColors=['#e9a75c','#6f91bb','#75ad98','#c77d9c','#9b8ac4','#d4b85b','#5ca8b7','#d98e61','#8c9eaa','#a8bd72','#b48c72','#7187c1'];
function renderChart(items,type='bar'){
 if(!items.length)return '<p class="muted">NA — required data is not available in the loaded JSON files.</p>';
 const clean=items.map(([label,val])=>[String(label),Math.max(0,Number(val)||0)]),total=clean.reduce((a,x)=>a+x[1],0);
 if(type==='donut'||type==='pie'){
  if(total<=0)return '<p class="muted">NA — no usable numeric values are available.</p>';
  let cursor=0;const stops=clean.map((x,i)=>{const start=cursor;cursor+=100*x[1]/total;return `${chartColors[i%chartColors.length]} ${start.toFixed(3)}% ${cursor.toFixed(3)}%`}).join(',');
  return `<div class="chart-visual-layout"><div class="chart-${type}" style="background:conic-gradient(${stops})">${type==='donut'?`<div class="chart-donut-hole"><b>${esc(n(total))}</b><span>Total records</span></div>`:''}</div><div class="chart-legend">${clean.map(([label,val],i)=>`<div class="chart-legend-row"><span class="chart-swatch" style="background:${chartColors[i%chartColors.length]}"></span><span class="chart-legend-label" title="${esc(label)}">${esc(label)}</span><b>${esc(n(val))}</b><small>${(100*val/total).toFixed(1)}%</small></div>`).join('')}</div></div>`;
 }
 if(type==='column'){
  const max=Math.max(1,...clean.map(x=>x[1]));
  return `<div class="column-chart-scroll"><div class="column-chart" style="min-width:${Math.max(100,clean.length*72)}px">${clean.map(([label,val],i)=>`<div class="column-item" title="${esc(label)}: ${esc(n(val))}"><div class="column-value">${esc(n(val))}</div><div class="column-track"><span style="height:${Math.max(val>0?2:0,100*val/max)}%;background:${chartColors[i%chartColors.length]}"></span></div><div class="column-label">${esc(label)}</div></div>`).join('')}</div></div>`;
 }
 return `<div class="bar-chart">${chartRows(clean,Math.max(1,...clean.map(x=>x[1])))}</div>`;
}
async function dashboard(){
 shell();const d=await all(),g=rows(d.golden,'golden'),f=rows(d.financing,'financing'),t=rows(d.training,'training'),s=d.summary||{};
 const hasGolden=!!d.golden&&(Array.isArray(d.golden)||['GOLDEN_RECORDS','golden_records','records','data'].some(k=>Array.isArray(d.golden[k]))),hasFin=!!d.financing&&(Array.isArray(d.financing)||['FINANCING_POTENTIAL_LEADS','financing_potential_leads','leads','records','data'].some(k=>Array.isArray(d.financing[k]))),hasTrain=!!d.training&&(Array.isArray(d.training)||['DEVELOPMENT_TRAINING_POTENTIAL','TRAINING_POTENTIAL_LEADS','DEVELOPMENT_TRAINING_LEADS','development_training_potential','training_potential_leads','leads','records','data'].some(k=>Array.isArray(d.training[k])));
 const profileCount=hasGolden?g.length:null, financingCount=hasFin?f.length:null, trainingCount=hasTrain?t.length:null;
 const activeStatuses=['active','aktif','operating','registered','beroperasi'];
 const statusVals=g.map(x=>field(x,['business_status','BUSINESS_STATUS','status','STATUS','company_status','COMPANY_STATUS']));
 const hasStatus=statusVals.some(x=>x!==null);
 const activeCount=hasStatus?statusVals.filter(x=>activeStatuses.includes(String(x).trim().toLowerCase())).length:null;
 const dq=metricValue(s,['DATA_QUALITY_SCORE','data_quality_score','OVERALL_DATA_QUALITY_SCORE','overall_data_quality_score']);
 const dqText=dq===null?'NA':`${esc(String(dq).includes('%')?dq:`${dq}%`)}`;
 const confs=g.map(x=>field(x,['MATCH_CONFIDENCE','match_confidence']));
 const hasConf=confs.some(x=>x!==null);
 const highCount=hasConf?g.filter(x=>{const z=field(x,['MATCH_CONFIDENCE','match_confidence']);return z!==null&&Number(z)>=90}).length:null;
 const size=aggregate(g,['business_size','BUSINESS_SIZE','size','SIZE','business_scale','BUSINESS_SCALE']);
 const state=aggregate(g,['state','STATE','business_state','BUSINESS_STATE','negeri','NEGERI']);
 const stateTop8=state.slice(0,8); // Dashboard chart shows only the eight states with the most SME records.
 const financingBySector=aggregate(f,['SECTOR','sector','BUSINESS_SECTOR','business_sector','INDUSTRY','industry']).filter(([label])=>!['0','0.0','0.00','NA','N/A','NULL'].includes(String(label).trim().toUpperCase()));
 const trainingByState=aggregate(t,['STATE','state','BUSINESS_STATE','business_state','NEGERI','negeri']);
 const sourcesFromSummary=s.SOURCE_SUMMARY||s.SOURCE_SYSTEM_SUMMARY||s.SOURCE_COUNTS||null;
 let source= [];
 if(sourcesFromSummary&&typeof sourcesFromSummary==='object')source=Object.entries(sourcesFromSummary).map(([k,x])=>[k,Number(typeof x==='number'?x:(x?.record_count??x?.RECORD_COUNT??x?.count??x?.COUNT))]).filter(x=>Number.isFinite(x[1]));
 if(!source.length) {const m=new Map();for(const x of g){let ss=field(x,['SOURCE_SYSTEMS','source_systems','SOURCE_SYSTEM','source_system']);if(Array.isArray(ss))ss.forEach(z=>m.set(String(z),(m.get(String(z))||0)+1));else if(ss!==null)m.set(String(ss),(m.get(String(ss))||0)+1)}source=[...m.entries()].sort((a,b)=>b[1]-a[1])}
 const matchGroups=hasConf?[['Match ≥90%',g.filter(x=>{let v=field(x,['MATCH_CONFIDENCE','match_confidence']);return v!==null&&Number(v)>=90}).length],['Match 75–89%',g.filter(x=>{let v=field(x,['MATCH_CONFIDENCE','match_confidence']),z=Number(v);return v!==null&&z>=75&&z<90}).length],['Match <75%',g.filter(x=>{let v=field(x,['MATCH_CONFIDENCE','match_confidence']);return v!==null&&Number(v)<75}).length]]:[];
 let totalSource=metricValue(s,['SOURCE_RECORDS_READ','TOTAL_SOURCE_RECORDS','source_records_read','total_source_records']);
 if(totalSource===null){const ss=s.SOURCE_SUMMARY||s.SOURCE_SYSTEM_SUMMARY||s.SOURCE_COUNTS; if(ss&&typeof ss==='object'){const vals=Object.values(ss).map(x=>Number(typeof x==='number'?x:(x?.record_count??x?.RECORD_COUNT??x?.count??x?.COUNT))).filter(Number.isFinite);if(vals.length)totalSource=vals.reduce((a,b)=>a+b,0)}}
 const counts=s.OUTPUT_COUNTS||s.output_counts||{};
 const countOrSummary=(records,loaded,countKeys)=>{if(loaded)return records.length;const val=field(counts,countKeys);return val===null?null:val};
 const goldenCount=countOrSummary(g,hasGolden,['GOLDEN_RECORDS','golden_records','TOTAL_GOLDEN_RECORDS']);
 const finCount=countOrSummary(f,hasFin,['FINANCING_POTENTIAL_LEADS','financing_potential_leads']);
 const trainCount=countOrSummary(t,hasTrain,['DEVELOPMENT_TRAINING_POTENTIAL','DEVELOPMENT_TRAINING_LEADS','development_training_potential']);
 const metric=(label,value,note='')=>`<div class="card kpi"><div class="klabel">${label}</div><div class="kvalue">${value}</div><div class="knote">${note}</div></div>`;
 const chart=(title,desc,items,type='bar')=>`<section class="card section chart-card"><div class="chart-heading"><div><h2>${title}</h2><p class="muted">${desc}</p></div></div>${renderChart(items,type)}</section>`;

 const sourceTotal=source.reduce((a,x)=>a+Number(x[1]||0),0);
 if(totalSource===null&&source.length)totalSource=sourceTotal;
 page('Main',`${head('','SME Intelligence Hub','Summary and charts are populated only from the loaded JSON datasets. Missing data is displayed as NA.','refreshAll')}
 <div class="notice">All figures are read from the loaded JSON files or calculated directly from their records. Metrics requiring unavailable fields are shown as NA. No illustrative figures are used.</div>
 <div class="grid kpis summary-kpis">
 ${metric('Total SME Master Profiles',fmtCount(profileCount),'Count of records in SME Golden Records JSON')}
 ${metric('Active SMEs',fmtCount(activeCount),hasStatus?pct(activeCount,profileCount)+' of profiles':'NA — no business status field found')}
 ${metric('Data Quality Score',dqText,'Only shown when supplied by Run Summary JSON')}
 ${metric('Financing Prospects',fmtCount(financingCount),hasGolden&&hasFin?pct(financingCount,profileCount)+' of profiles':'Count from Financing Leads JSON')}
 ${metric('Training Prospects',fmtCount(trainingCount),hasGolden&&hasTrain?pct(trainingCount,profileCount)+' of profiles':'Count from Training Leads JSON')}
 ${metric('High Confidence Matches',fmtCount(highCount),hasConf?'Match confidence ≥90%':'NA — match confidence field not found')}
 </div>
 <div class="grid dashboard-charts">
 ${chart('SME by Business Size','Distribution based on business-size fields in Golden Records JSON',size,'donut')}
 ${chart('SME by State','Top 8 states by SME count, based on Golden Records JSON',stateTop8,'bar')}
 <section class="card section chart-card"><div class="chart-heading"><div><h2>Financing Leads by Sector</h2><p class="muted">Counts grouped by sector from Financing Leads JSON</p></div><span class="chart-total">${financingCount===null?'NA':n(financingCount)+' leads'}</span></div>${renderChart(financingBySector,'column')}</section>
 <section class="card section chart-card"><div class="chart-heading"><div><h2>Training Leads by State</h2><p class="muted">Counts grouped by state from Training Leads JSON</p></div><span class="chart-total">${trainingCount===null?'NA':n(trainingCount)+' leads'}</span></div>${renderChart(trainingByState,'bar')}</section>
 <section class="card section chart-card"><div class="chart-heading"><div><h2>Match Confidence</h2><p class="muted">Buckets calculated from record-level match confidence</p></div></div>${matchGroups.length?renderChart(matchGroups,'pie'):'<p class="muted">NA — match confidence is not available in Golden Records JSON.</p>'}<div class="quality-score"><div><span>Overall Data Quality Score</span><b>${dqText}</b></div></div></section>
 <section class="card section chart-card"><div class="chart-heading"><div><h2>Source System Contribution</h2><p class="muted">Counts from Run Summary JSON, or Golden Record source-system fields</p></div><span class="chart-total">${source.length?n(sourceTotal)+' records':'NA'}</span></div>${renderChart(source,'column')}</section>
 </div>
 <section class="card section chatbot-section" aria-labelledby="chatTitle">
  <div class="chatbot-header"><div class="chatbot-avatar">✦</div><div><h2 id="chatTitle">AI Chatbot</h2><p class="muted">Ask questions about SME profiles, financing leads, training leads, sectors, states and available data.</p></div><span class="chatbot-status"><i></i> JSON-connected prototype</span></div>
  <div class="chatbot-notice">Responses use the JSON datasets loaded in this browser. If the requested information is unavailable, the chatbot will say NA. This prototype is not connected to a live AI model.</div>
  <div class="chat-messages" id="chatMessages" aria-live="polite"><div class="chat-message bot"><span class="chat-avatar">✦</span><div class="chat-bubble"><b>Hello! I’m your SME Intelligence assistant.</b><br>Ask me a question about the currently loaded SME data. I will only use information available in the JSON files.</div></div></div>
  <div class="chat-suggestions"><button class="chat-suggestion" data-question="How many SME master profiles are available?">Total SME profiles</button><button class="chat-suggestion" data-question="Show financing leads by sector.">Financing by sector</button><button class="chat-suggestion" data-question="Show training leads by state.">Training by state</button><button class="chat-suggestion" data-question="What is the data quality score?">Data quality</button></div>
  <form class="chat-input-row" id="chatForm"><input id="chatInput" type="text" placeholder="Ask a question about the SME data…" autocomplete="off" aria-label="Ask the SME Intelligence assistant"><button class="btn primary" type="submit">Send&nbsp; ↗</button></form>
 </section>`);
 $('#refreshAll').onclick=async()=>{await clearAll();await dashboard()};
 bindDashboardChat({g,f,t,hasGolden,hasFin,hasTrain,profileCount,financingCount,trainingCount,activeCount,hasStatus,dqText,hasConf,highCount,size,state,financingBySector,trainingByState,source,matchGroups});
}
function bindDashboardChat(ctx){
 const messages=$('#chatMessages'),input=$('#chatInput');
 const add=(text,who)=>{const row=document.createElement('div');row.className='chat-message '+who;const avatar=document.createElement('span');avatar.className='chat-avatar';avatar.textContent=who==='user'?'You':'✦';const bubble=document.createElement('div');bubble.className='chat-bubble';bubble.textContent=text;row.append(avatar,bubble);messages.appendChild(row);messages.scrollTop=messages.scrollHeight};
 const list=(title,items)=>items&&items.length?title+'\n'+items.map(([label,count])=>`• ${label}: ${n(count)}`).join('\n'):'NA — this information is not available in the loaded JSON files.';
 const answer=(question)=>{const q=question.toLowerCase();
  if((q.includes('total')||q.includes('how many')||q.includes('count'))&&(q.includes('sme')||q.includes('master profile')||q.includes('profile')))return `Total SME Master Profiles: ${fmtCount(ctx.profileCount)}.`;
  if(q.includes('active'))return `Active SMEs: ${fmtCount(ctx.activeCount)}${ctx.hasStatus?' based on available business-status fields.':'; NA because no recognised business-status field is available.'}`;
  if(q.includes('financ')&&(/sector|industry|sectors/.test(q)))return list('Financing leads by sector:',ctx.financingBySector);
  if(q.includes('training')&&(/state|negeri|location/.test(q)))return list('Training leads by state:',ctx.trainingByState);
  if(q.includes('financ'))return `Financing Prospects: ${fmtCount(ctx.financingCount)} records in the loaded Financing Leads JSON.`;
  if(q.includes('training')||q.includes('development lead'))return `Training Prospects: ${fmtCount(ctx.trainingCount)} records in the loaded Development & Training JSON.`;
  if(q.includes('business size')||q.includes('business scale')||q.includes('micro')||q.includes('medium'))return list('SME by business size:',ctx.size);
  if(q.includes('state')||q.includes('negeri'))return list('SME master profiles by state:',ctx.state);
  if(q.includes('source system')||q.includes('source contribution')||q.includes('source data'))return list('Source system contribution:',ctx.source);
  if(q.includes('data quality')||q.includes('quality score'))return `Data Quality Score: ${ctx.dqText}. The score is shown only if supplied in the Run Summary JSON.`;
  if(q.includes('match')||q.includes('confidence'))return ctx.hasConf?list('Match confidence distribution:',ctx.matchGroups):'NA — match confidence is not available in the loaded SME Golden Records JSON.';
  if(q.includes('help')||q.includes('what can'))return 'You can ask about total SME profiles, active SMEs, financing prospects, financing leads by sector, training prospects, training leads by state, business size, state distribution, source contribution, data quality or match confidence.';
  return 'I could not identify a supported metric in that question. Try asking about SME profiles, financing by sector, training by state, business size, state distribution, data quality or match confidence. Answers are limited to the loaded JSON data.';
 };
 const send=(q)=>{q=(q||'').trim();if(!q)return;add(q,'user');input.value='';setTimeout(()=>add(answer(q),'bot'),120)};
 $('#chatForm').addEventListener('submit',e=>{e.preventDefault();send(input.value)});
 $$('[data-question]').forEach(b=>b.addEventListener('click',()=>send(b.dataset.question)));
}
function normalizeDataset(k,d){
 if(k==='summary'){
  if(!d||typeof d!=='object'||Array.isArray(d))throw Error('Run Summary must be a JSON object.');
  return d;
 }
 const candidates=k==='golden'?['GOLDEN_RECORDS','golden_records','records','data']:
  k==='financing'?['FINANCING_POTENTIAL_LEADS','financing_potential_leads','leads','records','data']:
  ['DEVELOPMENT_TRAINING_POTENTIAL','TRAINING_POTENTIAL_LEADS','DEVELOPMENT_TRAINING_LEADS','development_training_potential','training_potential_leads','leads','records','data'];
 if(Array.isArray(d))return {[candidates[0]]:d};
 if(!d||typeof d!=='object')throw Error('Expected a JSON object or array.');
 for(const key of candidates){if(Array.isArray(d[key]))return d}
 // Support a common nested export wrapper, without discarding metadata.
 if(d.result&&typeof d.result==='object')for(const key of candidates)if(Array.isArray(d.result[key]))return {...d,...d.result};
 throw Error('Expected a record array. Recognised keys: '+candidates.join(', '));
}
async function datasetManager(){
 shell();let d=await all();
 page('Dataset Manager',`${head('','JSON Dataset Manager','Upload, parse and validate the four JSON engine outputs. Uploads are shared across all pages in this browser.','refreshAll')}<div class="notice">Select a JSON file for each dataset. The file is parsed in the browser, checked for a recognised structure, then saved for use by the dashboard and other pages. Uploading does not change the files on disk.</div><div id="upload-feedback" aria-live="polite"></div><div id="uploads">${uploadCards(d)}</div><p class="footer">To use JSON files from disk automatically, place them beside the HTML files and run this prototype through a local HTTP server. Use “Reload file from folder” to fetch the fixed filename again.</p>`);
 $('#refreshAll').onclick=async()=>{await clearAll();location.reload()};
 $$('[data-upload]').forEach(i=>i.addEventListener('change',async()=>{
  const file=i.files&&i.files[0];if(!file)return;const k=i.dataset.upload;const feedback=$('#upload-feedback');
  feedback.innerHTML=`<div class="notice">Reading ${esc(file.name)}…</div>`;
  try{
   const text=await file.text();let parsed;try{parsed=JSON.parse(text)}catch(err){throw Error('Invalid JSON syntax: '+err.message)}
   const normalized=normalizeDataset(k,parsed);const storage=await put(k,normalized);
   const count=k==='summary'?null:rows(normalized,k).length;
   feedback.innerHTML=`<div class="notice good">Successfully loaded <b>${esc(file.name)}</b>${count===null?'':` — ${n(count)} records detected`}. Dashboard data has been updated in this browser.</div>`;
   // Re-render the manager so the loaded status and record count update without losing feedback.
   const refreshed=await all();$('#uploads').innerHTML=uploadCards(refreshed);
   bindUploads();bindReloads();
  }catch(e){feedback.innerHTML=`<div class="notice">Could not load <b>${esc(file.name)}</b>: ${esc(e.message)}. The previous dataset, if any, has been retained.</div>`;i.value=''}
 }));
 bindReloads();
 function bindUploads(){ $$('[data-upload]').forEach(i=>i.addEventListener('change',async()=>{const file=i.files&&i.files[0];if(!file)return;const k=i.dataset.upload;const feedback=$('#upload-feedback');feedback.innerHTML=`<div class="notice">Reading ${esc(file.name)}…</div>`;try{let parsed;try{parsed=JSON.parse(await file.text())}catch(err){throw Error('Invalid JSON syntax: '+err.message)}const normalized=normalizeDataset(k,parsed);const storage=await put(k,normalized);const count=k==='summary'?null:rows(normalized,k).length;feedback.innerHTML=`<div class="notice good">Successfully loaded <b>${esc(file.name)}</b>${count===null?'':` — ${n(count)} records detected`}. Dashboard data has been updated in this browser.</div>`;$('#uploads').innerHTML=uploadCards(await all());bindUploads();bindReloads()}catch(e){feedback.innerHTML=`<div class="notice">Could not load <b>${esc(file.name)}</b>: ${esc(e.message)}. The previous dataset, if any, has been retained.</div>`;i.value=''}})); }
 function bindReloads(){ $$('[data-reload]').forEach(b=>b.onclick=async()=>{const k=b.dataset.reload,feedback=$('#upload-feedback');try{const r=await fetch(files[k],{cache:'no-store'});if(!r.ok)throw Error('HTTP '+r.status);const parsed=await r.json(),normalized=normalizeDataset(k,parsed),storage=await put(k,normalized);feedback.innerHTML=`<div class="notice good">Reloaded ${esc(files[k])} successfully.</div>`;$('#uploads').innerHTML=uploadCards(await all());bindUploads();bindReloads()}catch(e){feedback.innerHTML=`<div class="notice">Cannot reload ${esc(files[k])}: ${esc(e.message)}. Ensure the file exists beside the HTML files and the server is running.</div>`}}); }
}
function financingPage(d){
 const a=rows(d,'financing');
 const state=x=>field(x,['STATE','state']);
 const priority=x=>field(x,['LEAD_PRIORITY','lead_priority']);
 const rank=x=>field(x,['LEAD_RANK','lead_rank']);
 const smeId=x=>field(x,['SME_ID','sme_id']);
 const matchMethod=x=>field(x,['SME_ID_MATCH_METHOD','sme_id_match_method']);
 const score=x=>field(x,['FINAL_LEAD_SCORE','final_lead_score']);
 const leadKey=x=>String(rank(x)??smeId(x)??'');
 page('Financing Opportunity',`${head('','Financing Opportunity','Ranked financing leads using the SME_ID-based lead-scoring JSON format.','refreshPage')}<div class="notice">Lead scores, priority and recommended actions are displayed as supplied by the JSON. SME_ID links to the existing SME Golden Record when available. These are leads for review, not approved financing applications.</div><div class="grid kpis"><div class="card kpi"><div class="klabel">Total Financing Leads</div><div class="kvalue">${n(a.length)}</div><div class="knote">Records loaded from ${files.financing}</div></div><div class="card kpi"><div class="klabel">Very Hot / Hot</div><div class="kvalue">${n(a.filter(x=>['VERY HOT','HOT'].includes(String(priority(x)||'').toUpperCase())).length)}</div><div class="knote">Based on LEAD_PRIORITY</div></div><div class="card kpi"><div class="klabel">Training Participants</div><div class="kvalue">${a.some(x=>field(x,['TRAINING_PARTICIPANT','training_participant'])!==null)?n(a.filter(x=>Number(field(x,['TRAINING_PARTICIPANT','training_participant']))===1).length):'NA'}</div><div class="knote">Based on TRAINING_PARTICIPANT</div></div><div class="card kpi"><div class="klabel">Average Lead Score</div><div class="kvalue">${(()=>{const vals=a.map(x=>score(x)).filter(x=>x!==null&&Number.isFinite(Number(x)));return vals.length?(vals.reduce((s,x)=>s+Number(x),0)/vals.length).toFixed(2):'NA'})()}</div><div class="knote">Average of available FINAL_LEAD_SCORE values</div></div></div><div class="card section"><h2>Financing Lead Directory</h2><p class="muted">${n(a.length)} records · SME_ID is the Golden Record identifier; lead rank is the ranking position.</p><div class="tools"><input class="search" id="q" placeholder="Search SME ID, company, source, sector, email…"><select id="state"><option value="">All states</option>${[...new Set(a.map(state).filter(x=>x!==null).map(String))].sort().map(x=>`<option value="${esc(x)}">${esc(x)}</option>`).join('')}</select><select id="priority"><option value="">All priorities</option>${[...new Set(a.map(priority).filter(x=>x!==null).map(String))].sort((x,y)=>x.localeCompare(y)).map(x=>`<option value="${esc(x)}">${esc(x)}</option>`).join('')}</select><select id="sort"><option value="rank">Sort by lead rank</option><option value="score">Highest lead score</option></select></div><div class="tablewrap"><table><thead><tr><th>Rank</th><th>SME Golden ID</th><th>ID Match Method</th><th>Company</th><th>Source / Programme</th><th>State</th><th>Sector</th><th>SME Category</th><th>Final Score</th><th>Priority</th><th>Recommended Action</th><th>Details</th></tr></thead><tbody id="tbody"></tbody></table></div><div class="pagination"><span id="count"></span><span><button class="btn" id="prev">Previous</button> <button class="btn" id="next">Next</button></span></div></div><p class="footer">Missing or null JSON fields are shown as —. Scores are not recalculated by this interface. SME_ID values are read from the JSON; the interface does not generate identifiers.</p>`);
 let p=1,filtered=[];
 function draw(){
  const q=$('#q').value.toLowerCase(),st=$('#state').value,pr=$('#priority').value,sort=$('#sort').value;
  filtered=a.filter(x=>JSON.stringify(x).toLowerCase().includes(q)&&(!st||String(state(x)??'')===st)&&(!pr||String(priority(x)??'')===pr));
  filtered.sort((x,y)=>sort==='score'?(Number(score(y)??-Infinity)-Number(score(x)??-Infinity)):(Number(rank(x)??Infinity)-Number(rank(y)??Infinity)));
  const pages=Math.max(1,Math.ceil(filtered.length/10));p=Math.min(p,pages);const part=filtered.slice((p-1)*10,p*10);
  $('#tbody').innerHTML=part.map(x=>{const pri=String(priority(x)||'').toUpperCase(),cls=pri==='VERY HOT'?'ok':pri==='HOT'?'info':pri==='WARM'?'warn':'';const id=smeId(x);return `<tr><td>${esc(v(rank(x)))}</td><td>${id?`<span class="click" data-sme-profile="${esc(id)}">${esc(id)}</span>`:'—'}</td><td>${esc(v(matchMethod(x)))}</td><td><span class="company">${esc(v(field(x,['COMPANY_NAME','company_name'])))}</span><span class="sub">${esc(v(field(x,['REGISTRATION_NUMBER','registration_number'])))}</span></td><td>${esc(v(field(x,['LEAD_SOURCE','lead_source'])))}<span class="sub">${esc(v(field(x,['PROGRAMME','programme'])))}</span></td><td>${esc(v(state(x)))}</td><td>${esc(v(field(x,['SECTOR','sector'])))}</td><td>${esc(v(field(x,['SME_CATEGORY','sme_category'])))}</td><td><b>${score(x)===null?'—':esc(Number(score(x)).toFixed(2))}</b></td><td>${pill(v(priority(x)),cls)}</td><td>${esc(v(field(x,['RECOMMENDED_ACTION','recommended_action'])))}</td><td><button class="btn" data-fin-lead="${esc(leadKey(x))}">View details</button></td></tr>`}).join('');
  $('#count').textContent=`Showing ${filtered.length?(p-1)*10+1:0}–${Math.min(p*10,filtered.length)} of ${filtered.length}`;$('#prev').disabled=p===1;$('#next').disabled=p>=pages;
  $$('[data-fin-lead]').forEach(el=>el.onclick=()=>financingLeadModal(el.dataset.finLead));
  $$('[data-sme-profile]').forEach(el=>el.onclick=()=>location.href='sme_master_profile_detail_v2.html?id='+encodeURIComponent(el.dataset.smeProfile));
 }
 ['q','state','priority','sort'].forEach(id=>$('#'+id).addEventListener('input',()=>{p=1;draw()}));$('#prev').onclick=()=>{p--;draw()};$('#next').onclick=()=>{p++;draw()};$('#refreshPage').onclick=async()=>{try{const r=await fetch(files.financing,{cache:'no-store'});if(!r.ok)throw Error('HTTP '+r.status);await put('financing',normalizeDataset('financing',await r.json()));location.reload()}catch(e){alert('Could not reload '+files.financing+'. Check that the file is beside the HTML files and the local server is running.')}};draw();
}
function financingLeadModal(key){
 const records=rows(get('financing'),'financing');
 const x=records.find(r=>String(field(r,['LEAD_RANK','lead_rank'])??field(r,['SME_ID','sme_id'])??'')===String(key));
 if(!x)return;
 const val=(names)=>field(x,names);
 const fmt=(z)=>z===null?'—':typeof z==='number'?String(z):String(z);
 const fields=[
  ['Lead Rank',val(['LEAD_RANK'])],['SME Golden ID',val(['SME_ID'])],['SME ID Match Method',val(['SME_ID_MATCH_METHOD'])],
  ['Lead Source',val(['LEAD_SOURCE'])],['Programme',val(['PROGRAMME'])],['Training Participant',val(['TRAINING_PARTICIPANT'])===null?null:(Number(val(['TRAINING_PARTICIPANT']))===1?'Yes':'No')],
  ['Company Name',val(['COMPANY_NAME'])],['Registration Number',val(['REGISTRATION_NUMBER'])],['Email',val(['EMAIL'])],['Phone',val(['PHONE'])],['State',val(['STATE'])],['Sector',val(['SECTOR'])],['SME Category',val(['SME_CATEGORY'])],['Business Need',val(['BUSINESS_NEED'])],
  ['Annual Turnover',val(['ANNUAL_TURNOVER'])===null?null:money(val(['ANNUAL_TURNOVER']))],['Full-time Employees',val(['FULL_TIME_EMPLOYEES'])],['Attendance',val(['ATTENDANCE'])],['Collection Rate',val(['COLLECTION_RATE'])],['Ageing',val(['AGEING'])],
  ['Readiness Score',val(['READINESS_SCORE'])===null?null:Number(val(['READINESS_SCORE'])).toFixed(2)],['Conversion Propensity',val(['CONVERSION_PROPENSITY'])===null?null:Number(val(['CONVERSION_PROPENSITY'])).toFixed(2)],['Final Lead Score',val(['FINAL_LEAD_SCORE'])===null?null:Number(val(['FINAL_LEAD_SCORE'])).toFixed(2)],['Lead Priority',val(['LEAD_PRIORITY'])],['Recommended Action',val(['RECOMMENDED_ACTION'])]
 ];
 const id=val(['SME_ID']);
 document.body.insertAdjacentHTML('beforeend',`<div class="modalback" id="modal"><div class="modal"><div style="display:flex;justify-content:space-between;gap:10px"><div><div class="eyebrow">Financing lead scoring</div><h2 style="margin:0">${esc(v(val(['COMPANY_NAME'])))}</h2><p class="muted">SME ID: ${esc(v(id))} · Rank ${esc(v(val(['LEAD_RANK'])))}</p></div><button class="btn" id="close">Close ✕</button></div>${id?`<p><a href="sme_master_profile_detail_v2.html?id=${encodeURIComponent(String(id))}">Open SME Master Profile ↗</a></p>`:''}<div class="grid detailgrid">${fields.map(([l,z])=>`<div class="field"><div class="flabel">${esc(l)}</div><div class="fvalue">${esc(fmt(z))}</div></div>`).join('')}</div><p class="footer">All values are read from the financing leads JSON. Null or absent fields are displayed as —.</p></div></div>`);$('#close').onclick=()=>$('#modal').remove();$('#modal').onclick=e=>{if(e.target.id==='modal')e.currentTarget.remove()};
}
function tablePage(d,k){if(k==='financing')return financingPage(d);let golden=k==='golden',a=rows(d,k),title=golden?'Master Profile':'Development & Training',state=x=>golden?x.state:x.STATE,company=x=>golden?x.business_name:x.BUSINESS_NAME;
let disclaimer=k==='financing'?d.DISCLAIMER:k==='training'?d.DISCLAIMER:'';
page(title,`${head('',title,golden?'Search consolidated SME records and inspect profile provenance.':golden?'':'Candidate leads identified by the engine.','refreshPage')}${disclaimer?`<div class="notice"><b>Important:</b> ${esc(disclaimer)}</div>`:''}<div class="card section"><h2>${golden?'Golden Record Directory':'Lead Directory'}</h2><p class="muted">${n(a.length)} records from ${files[k]}</p><div class="tools"><input class="search" id="q" placeholder="Search business, SME ID, SSM, email, state…"><select id="state"><option value="">All states</option>${[...new Set(a.map(state).filter(Boolean))].sort().map(x=>`<option>${esc(x)}</option>`).join('')}</select>${!golden?'<select id="review"><option value="">All review statuses</option><option value="true">Review required</option><option value="false">Review flag off</option></select>':''}</div><div class="tablewrap"><table><thead><tr>${(golden?['SME ID','Business Name','SSM / Registration','State','Sector','Match Status','Confidence','Source Systems']:['SME ID','Business Name','State','Sector',k==='financing'?'Financing Status':'Training Status','Review','Lead Reason']).map(x=>`<th>${x}</th>`).join('')}</tr></thead><tbody id="tbody"></tbody></table></div><div class="pagination"><span id="count"></span><span><button class="btn" id="prev">Previous</button> <button class="btn" id="next">Next</button></span></div></div><p class="footer">Missing values are shown as —. Lead records are candidates, not approved financing applications or confirmed programme referrals.</p>`);
let p=1,filtered=[];function draw(){let q=$('#q').value.toLowerCase(),st=$('#state').value,rv=$('#review')?.value||'';filtered=a.filter(x=>JSON.stringify(x).toLowerCase().includes(q)&&(!st||state(x)===st)&&(!rv||String(!!x.REVIEW_REQUIRED)===rv));let pages=Math.max(1,Math.ceil(filtered.length/10));p=Math.min(p,pages);let part=filtered.slice((p-1)*10,p*10);$('#tbody').innerHTML=part.map(x=>golden?`<tr><td><span class="click" data-profile="${esc(x.SME_ID)}">${esc(v(x.SME_ID))}</span></td><td><span class="company">${esc(v(x.business_name))}</span><span class="sub">${esc(v(x.contact_person))}</span></td><td>${esc(v(x.ssm))}</td><td>${esc(v(x.state))}</td><td>${esc(v(x.sector))}</td><td>${pill(v(x.MATCH_STATUS),x.MATCH_STATUS==='AUTO_MATCH'?'ok':'warn')}</td><td>${x.MATCH_CONFIDENCE==null?'—':esc(x.MATCH_CONFIDENCE)+'%'}</td><td>${chips(x.SOURCE_SYSTEMS)}</td></tr>`:`<tr><td><span class="click" data-lead="${esc(x.SME_ID)}">${esc(v(x.SME_ID))}</span></td><td><span class="company">${esc(v(x.BUSINESS_NAME))}</span><span class="sub">${esc(v(x.EMAIL))}</span></td><td>${esc(v(x.STATE))}</td><td>${esc(v(x.SECTOR))}</td><td>${esc(v(k==='financing'?x.FINANCING_STATUS:x.TRAINING_STATUS))}</td><td>${x.REVIEW_REQUIRED?pill('Review required','warn'):pill('Review flag off','ok')}</td><td><button class="btn" data-lead="${esc(x.SME_ID)}">View criteria</button><span class="sub">${esc(v(x.LEAD_REASON))}</span></td></tr>`).join('');$('#count').textContent=`Showing ${filtered.length?(p-1)*10+1:0}–${Math.min(p*10,filtered.length)} of ${filtered.length}`;$('#prev').disabled=p===1;$('#next').disabled=p>=pages;$$('[data-profile]').forEach(el=>el.onclick=()=>location.href='sme_master_profile_detail_v2.html?id='+encodeURIComponent(el.dataset.profile));$$('[data-lead]').forEach(el=>el.onclick=()=>leadModal(k,el.dataset.lead))}
['q','state','review'].forEach(id=>$('#'+id)?.addEventListener('input',()=>{p=1;draw()}));$('#prev').onclick=()=>{p--;draw()};$('#next').onclick=()=>{p++;draw()};$('#refreshPage').onclick=async()=>{try{let r=await fetch(files[k],{cache:'no-store'});if(!r.ok)throw Error();await put(k,normalizeDataset(k,await r.json()));location.reload()}catch{alert('Could not reload '+files[k]+'. Check the same-folder file and local server.')}};draw()}
function leadModal(k,id){let x=rows(get(k),k).find(r=>String(r.SME_ID)===String(id));if(!x)return;let c=x.LEAD_CRITERIA||[];document.body.insertAdjacentHTML('beforeend',`<div class="modalback" id="modal"><div class="modal"><div style="display:flex;justify-content:space-between;gap:10px"><div><div class="eyebrow">Lead qualification</div><h2 style="margin:0">${esc(v(x.BUSINESS_NAME))}</h2><p class="muted">${esc(v(x.SME_ID))} · ${k==='financing'?'Financing opportunity':'Development & training'}</p></div><button class="btn" id="close">Close ✕</button></div><div class="notice">${esc(v(x.LEAD_REASON))}</div><div class="grid detailgrid">${[['SSM',x.SSM],['Phone',x.PHONE],['Email',x.EMAIL],['State',x.STATE],['Sector',x.SECTOR],['Lead type',x.LEAD_TYPE],['Financing status',x.FINANCING_STATUS],['Financing need',x.FINANCING_NEED],['Annual revenue',money(x.ANNUAL_REVENUE)],['Training status',x.TRAINING_STATUS],['Digitalisation',x.DIGITALISATION],['Programme',x.PROGRAMME]].map(([l,z])=>`<div class="field"><div class="flabel">${esc(l)}</div><div class="fvalue">${esc(v(z))}</div></div>`).join('')}</div><h3>Qualification criteria (${c.length})</h3>${c.map(z=>`<div class="criteria"><b>${esc(v(z.CRITERION))}</b><p class="muted">Source: ${esc(v(z.SOURCE_SYSTEM))} · Field: ${esc(v(z.SOURCE_FIELD))} · Value: ${esc(v(z.SOURCE_VALUE))}</p><div class="muted">Rule: ${esc(v(z.RULE))}</div></div>`).join('')||'<p class="muted">No criteria supplied.</p>'}<p class="footer">Source systems: ${esc((x.SOURCE_SYSTEMS||[]).join(', '))} · Review required: ${esc(v(x.REVIEW_REQUIRED))}</p></div></div>`);$('#close').onclick=()=>$('#modal').remove();$('#modal').onclick=e=>{if(e.target.id==='modal')e.currentTarget.remove()}}
async function detail(){shell();let d=await load('golden');if(!d){page('Profile detail',`<div class="notice">Could not load sme_golden_records.JSON. Go to the Main Dashboard to upload it.</div>`);return}let id=new URLSearchParams(location.search).get('id'),x=rows(d,'golden').find(r=>String(r.SME_ID)===String(id));if(!x){page('Profile detail',`<h1>Profile not found</h1><a href="sme_master_profile_v7.html">Back to Master Profile</a>`);return}let fs=[['SME ID',x.SME_ID],['Business name',x.business_name],['SSM / registration',x.ssm],['Contact person',x.contact_person],['Phone',x.phone],['Email',x.email],['Address',x.address],['Postcode',x.postcode],['City',x.city],['State',x.state],['Sector',x.sector],['Business status',x.business_status],['Annual revenue',money(x.annual_revenue)],['Financing status',x.financing_status],['Financing need',x.financing_need],['Training status',x.training_status],['Digitalisation',x.digitalisation],['Entrepreneur ID',x.entrepreneur_id],['Programme',x.programme]];let prov=x.PROVENANCE||{};page('Master Profile Detail',`${head('',esc(v(x.business_name)),`${esc(v(x.SME_ID))} · Unified Golden Record`)}<p><a class="btn" href="sme_master_profile_v7.html">← Back to Master Profile</a></p><div class="grid kpis" style="margin-top:18px"><div class="card kpi"><div class="klabel">Match Confidence</div><div class="kvalue">${x.MATCH_CONFIDENCE==null?'—':esc(x.MATCH_CONFIDENCE)+'%'}</div></div><div class="card kpi"><div class="klabel">Match Status</div><div class="kvalue" style="font-size:18px">${esc(v(x.MATCH_STATUS))}</div></div><div class="card kpi"><div class="klabel">Source Systems</div><div class="kvalue">${n((x.SOURCE_SYSTEMS||[]).length)}</div><div class="knote">${esc((x.SOURCE_SYSTEMS||[]).join(', '))}</div></div><div class="card kpi"><div class="klabel">Source Records</div><div class="kvalue">${n(x.SOURCE_RECORD_COUNT)}</div></div></div><div class="card section"><h2>Master Profile Attributes</h2><div class="grid detailgrid">${fs.map(([l,z])=>`<div class="field"><div class="flabel">${esc(l)}</div><div class="fvalue">${esc(v(z))}</div></div>`).join('')}</div></div><div class="card section"><h2>Source Records</h2><div class="tablewrap"><table><thead><tr><th>Source System</th><th>Source Record ID</th><th>Source Row</th></tr></thead><tbody>${(x.SOURCE_RECORDS||[]).map(z=>`<tr><td>${esc(v(z.source_system))}</td><td>${esc(v(z.source_record_id))}</td><td>${esc(v(z.source_row_number))}</td></tr>`).join('')||'<tr><td colspan="3">No source record detail supplied.</td></tr>'}</tbody></table></div></div><div class="card section"><h2>Field Provenance</h2><p class="muted">Canonical attribute and the original source field selected by the engine.</p><div class="tablewrap"><table><thead><tr><th>Canonical Field</th><th>Source System</th><th>Source Field</th></tr></thead><tbody>${Object.entries(prov).map(([k,z])=>`<tr><td>${esc(k)}</td><td>${esc(v(z?.source_system))}</td><td>${esc(v(z?.source_field))}</td></tr>`).join('')||'<tr><td colspan="3">No provenance supplied.</td></tr>'}</tbody></table></div></div>`)}
async function init(){let p=document.body.dataset.page;if(p==='main')return dashboard();if(p==='dataset')return datasetManager();shell();if(p==='detail')return detail();let k=p==='master'?'golden':p==='financing'?'financing':'training',d=await load(k);if(!d){page('Dataset required',`<div class="head"><div><div class="eyebrow">JSON file required</div><h1>Dataset not loaded</h1><p>Expected file: ${files[k]}</p></div><a class="btn primary" href="index.html">Go to Main Dashboard</a></div><div class="notice">Keep the file in the same folder and open the prototype through a local HTTP server. You can also upload it from the Main Dashboard.</div>`);return}tablePage(d,k)}
return{init}
})();document.addEventListener('DOMContentLoaded',U.init);
