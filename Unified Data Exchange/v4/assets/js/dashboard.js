(() => {
 const $=id=>document.getElementById(id);
 const state={data:null,page:{master:1,financing:1,intervention:1},size:10};
 const esc=v=>String(v??'—').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const fmt=v=>Number(v||0).toLocaleString('en-MY');
 const list=v=>Array.isArray(v)?v:[];
 // v1.1: support both COMPANY_NAME and BUSINESS_NAME in UDX outputs.
 function getCompanyName(record){
  const value=record?.COMPANY_NAME??record?.BUSINESS_NAME;
  return value==null||String(value).trim()===''?'—':String(value).trim();
 }
 function firstValue(records,keys){
  for(const record of records){
   if(!record)continue;
   for(const key of keys){
    const value=record[key];
    if(value!==undefined&&value!==null&&String(value).trim()!=='')return value;
   }
  }
  return null;
 }
 function formatRM(value){
  if(value===null||value===undefined||String(value).trim()==='')return '—';
  const n=Number(String(value).replace(/[^0-9.-]/g,''));
  return Number.isFinite(n)?'RM '+n.toLocaleString('en-MY',{minimumFractionDigits:2,maximumFractionDigits:2}):String(value);
 }
 function go(page){document.querySelectorAll('.page').forEach(x=>x.classList.toggle('active',x.id==='page-'+page));document.querySelectorAll('.nav').forEach(x=>x.classList.toggle('active',x.dataset.page===page));document.querySelector('.sidebar').classList.remove('open');history.replaceState(null,'','#'+page)}
 document.querySelectorAll('.nav').forEach(b=>b.onclick=()=>go(b.dataset.page));
 $('menuBtn').onclick=()=>document.querySelector('.sidebar').classList.toggle('open');
 if(location.hash&&document.querySelector('[data-page="'+location.hash.slice(1)+'"]'))go(location.hash.slice(1));

 function dashboardBreakdowns(s,f,i){
  const financingRows=list(f.FINANCING_POTENTIAL_LEADS);
  const byState={};
  financingRows.forEach(record=>{
   const raw=record.STATE??record.STATE_NAME??record.BUSINESS_STATE;
   const name=raw==null||String(raw).trim()===''?'Unknown':String(raw).trim();
   byState[name]=(byState[name]||0)+1;
  });
  const stateRows=Object.entries(byState).sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0]));
  const stateMax=Math.max(1,...stateRows.map(x=>x[1]));
  $('financingStateChart').innerHTML=stateRows.length?stateRows.map(([name,count])=>`<div class="bar-row"><span>${esc(name)}</span><div class="track"><div class="fill" style="width:${count/stateMax*100}%"></div></div><b class="bar-value">${fmt(count)}</b></div>`).join(''):'<div class="empty">No financing lead records available.</div>';

  const labels={TRAINING:'Training',DIGITALISATION:'Digitalisation',BUSINESS_DEVELOPMENT:'Business Development',LEADERSHIP_CAPACITY:'Leadership Capacity',HUMAN_RESOURCES:'Human Resources',FINANCIAL_MANAGEMENT:'Financial Management'};
  const summaryCounts=s.OUTPUT_COUNTS?.INTERVENTION_BY_TYPE||{};
  const records=list(i.INTERVENTION_POTENTIAL_LEADS);
  const keys=[...new Set([...Object.keys(labels),...Object.keys(summaryCounts),...records.map(x=>x.INTERVENTION_TYPE).filter(Boolean)])];
  const interventionRows=keys.map(key=>[labels[key]||key.replaceAll('_',' '),summaryCounts[key]??records.filter(x=>x.INTERVENTION_TYPE===key).length]).sort((a,b)=>Number(b[1])-Number(a[1])||a[0].localeCompare(b[0]));
  $('interventionChart').innerHTML=interventionRows.length?interventionRows.map(([name,count])=>`<div class="intervention-count-row"><span>${esc(name)}</span><strong>${fmt(count)}</strong></div>`).join(''):'<div class="empty">No intervention records available.</div>';
 }
 function touchpoints(s){
  const names={ELSA:'ELSA Assessment',CBRS:'CEDAR Training',EPC:'EPC Tenancy',JOMXCESS:'Event',MIS4:'Existing Customer'};
  const rows=Object.entries(s.SOURCE_SUMMARY||{});
  $('touchpoints').innerHTML=rows.map(([k,v])=>`<tr><td>${esc(names[k]||k)}</td><td class="right">${fmt(v.record_count??v.RECORD_COUNT)}</td></tr>`).join('')+`<tr><td><b>Total</b></td><td class="right"><b>${fmt(rows.reduce((a,[,v])=>a+Number(v.record_count??v.RECORD_COUNT??0),0))}</b></td></tr>`;
 }
 function dataInfo(s,n){
  const m=s.MATCHING_STATISTICS||{},q=s.DATA_QUALITY||{};
  const pairs=[['Auto Match',m.AUTO_MATCH],['Identity Review Required',m.IDENTITY_REVIEW_REQUIRED],['Single Source',m.SINGLE_SOURCE]];
  $('matchingStats').innerHTML=pairs.map(([k,v])=>`<div class="stat-box"><span>${esc(k)}</span><strong>${fmt(v)}</strong></div>`).join('');
  $('dataCount').textContent=fmt(n)+' Golden Records';
  const quality=[['Without Company Name',q.GOLDEN_RECORDS_WITHOUT_COMPANY_NAME],['Without SSM',q.GOLDEN_RECORDS_WITHOUT_SSM],['Without Phone',q.GOLDEN_RECORDS_WITHOUT_PHONE],['Without Email',q.GOLDEN_RECORDS_WITHOUT_EMAIL],['MODULE = NA',q.GOLDEN_RECORDS_WITH_MODULE_NA],['Identity Review Required',q.IDENTITY_REVIEW_REQUIRED]];
  $('qualityStats').innerHTML=quality.map(([k,v])=>`<div class="quality-box"><span>${esc(k)}</span><strong>${fmt(v)}</strong></div>`).join('');
  const t=s.PROCESSING_TIMINGS_SECONDS||{},d=[['Generated At',s.GENERATED_AT],['Process Start',s.PROCESS_START_DATETIME],['Process End',s.PROCESS_END_DATETIME],['Total Runtime',(s.TOTAL_RUNTIME_SECONDS??'—')+' seconds ('+(s.TOTAL_RUNTIME_HH_MM_SS??'—')+')'],['Source Records Read',s.SOURCE_RECORDS_READ],['New SME IDs Generated',s.IDENTITY_STATISTICS?.NEW_SME_IDS_GENERATED],['Existing SME IDs Reused',s.IDENTITY_STATISTICS?.EXISTING_SME_IDS_REUSED],['Existing Records Changed',s.IDENTITY_STATISTICS?.EXISTING_RECORDS_CHANGED],['Source Loading & Normalisation',t.SOURCE_LOADING_AND_NORMALISATION==null?'—':t.SOURCE_LOADING_AND_NORMALISATION+'s'],['Matching & Lead Scoring',t.MATCHING_AND_LEAD_SCORING==null?'—':t.MATCHING_AND_LEAD_SCORING+'s']];
  $('processingInfo').innerHTML=d.map(([k,v])=>`<div><span>${esc(k)}</span><b>${esc(v??'—')}</b></div>`).join('');
 }
 function pageRows(rows,page,body,info,renderRow){
  const pages=Math.max(1,Math.ceil(rows.length/state.size));page=Math.max(1,Math.min(page,pages));
  const slice=rows.slice((page-1)*state.size,page*state.size);
  $(body).innerHTML=slice.length?slice.map(renderRow).join(''):`<tr><td colspan="9" class="empty">No matching records</td></tr>`;
  $(info).textContent=`Page ${rows.length?page:0} of ${rows.length?pages:0} · ${fmt(rows.length)} records`;
  return {page,pages};
 }
 function master(){
  if(!state.data)return;
  let rows=list(state.data.files.golden.data.GOLDEN_RECORDS),q=$('masterSearch').value.toLowerCase(),size=$('masterSize').value;
  rows=rows.filter(x=>(!size||String(x.BUSINESS_SIZE||'').toLowerCase()===size.toLowerCase())&&[x.SME_ID,getCompanyName(x),x.STATE,x.SECTOR].some(v=>String(v||'').toLowerCase().includes(q)));
  const p=pageRows(rows,state.page.master,'masterTable','masterPageInfo',x=>`<tr><td><a href="#" class="record-link" data-record-kind="master" data-sme-id="${esc(x.SME_ID)}">${esc(x.SME_ID)}</a></td><td>${esc(getCompanyName(x))}</td><td>${esc(x.STATE)}</td><td>${esc(x.SECTOR)}</td><td>${esc(x.BUSINESS_SIZE)}</td><td>${esc(x.MATCH_STATUS)}</td><td>${esc(Array.isArray(x.SOURCE_SYSTEMS)?x.SOURCE_SYSTEMS.join(', '):x.SOURCE_SYSTEMS)}</td></tr>`);
  state.page.master=p.page;$('masterCount').textContent=fmt(rows.length)+' records';$('masterPrev').disabled=p.page<=1;$('masterNext').disabled=p.page>=p.pages;
 }
 function financing(){
  if(!state.data)return;
  let rows=list(state.data.files.financing.data.FINANCING_POTENTIAL_LEADS),q=$('financingSearch').value.toLowerCase(),tier=$('financingTier').value;
  rows=rows.filter(x=>(!tier||String(x.TIER||'').toUpperCase()===tier)&&[x.SME_ID,getCompanyName(x)].some(v=>String(v||'').toLowerCase().includes(q)));
  const p=pageRows(rows,state.page.financing,'financingTable','financingPageInfo',x=>`<tr><td><a href="#" class="record-link" data-record-kind="financing" data-sme-id="${esc(x.SME_ID)}">${esc(x.SME_ID)}</a></td><td>${esc(getCompanyName(x))}</td><td>${esc(x.STATE)}</td><td>${esc(x.SECTOR)}</td><td>${esc(x.TOTAL_SCORE)}</td><td>${esc(x.TIER)}</td><td><span class="tag ${x.REVIEW_REQUIRED?'review':'ok'}">${x.REVIEW_REQUIRED?'Need to review':'No'}</span></td></tr>`);
  state.page.financing=p.page;$('financingCount').textContent=fmt(rows.length)+' leads';$('financingPrev').disabled=p.page<=1;$('financingNext').disabled=p.page>=p.pages;
 }
 function intervention(){
  if(!state.data)return;
  let rows=list(state.data.files.intervention.data.INTERVENTION_POTENTIAL_LEADS),q=$('interventionSearch').value.toLowerCase(),tier=$('interventionTier').value,type=$('interventionType').value;
  rows=rows.filter(x=>(!tier||String(x.TIER||'').toUpperCase()===tier)&&(!type||x.INTERVENTION_TYPE===type)&&[x.SME_ID,getCompanyName(x)].some(v=>String(v||'').toLowerCase().includes(q)));
  const p=pageRows(rows,state.page.intervention,'interventionTable','interventionPageInfo',x=>`<tr><td><a href="#" class="record-link" data-record-kind="intervention" data-sme-id="${esc(x.SME_ID)}">${esc(x.SME_ID)}</a></td><td>${esc(getCompanyName(x))}</td><td>${esc(x.INTERVENTION_TYPE)}</td><td>${esc(x.SCORE)}</td><td>${esc(x.TIER)}</td><td><span class="tag ${x.REVIEW_REQUIRED?'review':'ok'}">${x.REVIEW_REQUIRED?'Need to review':'No'}</span></td></tr>`);
  state.page.intervention=p.page;$('interventionCount').textContent=fmt(rows.length)+' leads';$('interventionPrev').disabled=p.page<=1;$('interventionNext').disabled=p.page>=p.pages;
 }
 function admin(v){
  $('fileRows').innerHTML=v.rows.map(r=>`<tr><td>${esc(r.file)}</td><td><span class="tag ok">Available</span></td><td>${fmt(r.size)} bytes</td><td>${esc(r.generated)}</td><td>${esc(r.declared)} / ${esc(r.actual)}</td><td><span class="tag ${r.ok?'ok':'review'}">${r.ok?'Valid':'Invalid'}</span></td></tr>`).join('');
  const msgs=[...v.errors.map(x=>'ERROR: '+x),...v.warnings.map(x=>'WARNING: '+x)];
  $('validationMessages').textContent=msgs.length?msgs.join('\n'):'All four files passed structural and count validation.';
  $('validationMessages').className='messages '+(v.errors.length?'error':v.warnings.length?'warning':'success');
  $('adminStatus').textContent=v.errors.length?'Validation failed':v.warnings.length?'Valid with warnings':'Dataset valid';
  $('adminStatus').className='status '+(v.errors.length?'error':v.warnings.length?'warning':'success');
 }
 function render(d){
  state.data=d;const s=d.files.summary.data,g=d.files.golden.data,f=d.files.financing.data,i=d.files.intervention.data;
  $('kpiSmes').textContent=fmt(g.RECORD_COUNT??list(g.GOLDEN_RECORDS).length);
  $('kpiFinancing').textContent=fmt(f.LEAD_COUNT??list(f.FINANCING_POTENTIAL_LEADS).length);
  $('kpiIntervention').textContent=fmt(i.LEAD_COUNT??list(i.INTERVENTION_POTENTIAL_LEADS).length);
  $('datasetStatus').textContent='● Dataset loaded';$('datasetStatus').className='status success';
  dashboardBreakdowns(s,f,i);touchpoints(s);dataInfo(s,Number(g.RECORD_COUNT??list(g.GOLDEN_RECORDS).length));
  $('runStrip').textContent=`Latest UDX run: ${s.GENERATED_AT||'—'} (Malaysia time) · Runtime: ${s.TOTAL_RUNTIME_SECONDS??'—'} seconds · Source records: ${s.SOURCE_RECORDS_READ??'—'}`;
  const types=[...new Set(list(i.INTERVENTION_POTENTIAL_LEADS).map(x=>x.INTERVENTION_TYPE).filter(Boolean))].sort();
  $('interventionType').innerHTML='<option value="">All intervention types</option>'+types.map(t=>`<option value="${esc(t)}">${esc(t.replaceAll('_',' '))}</option>`).join('');
  master();financing();intervention();admin(d.validation);
 }
 async function reload(){
  const b=$('validateReload');b.disabled=true;b.textContent='Validating…';
  try{render(await window.UDXData.load())}
  catch(e){$('datasetStatus').textContent='● Dataset unavailable';$('datasetStatus').className='status error';$('adminStatus').textContent='Validation failed';$('adminStatus').className='status error';$('validationMessages').textContent=e.validation?e.validation.errors.join('\n'):e.message;$('validationMessages').className='messages error';$('fileRows').innerHTML=`<tr><td colspan="6" class="empty">${esc(e.message)}</td></tr>`}
  finally{b.disabled=false;b.textContent='Validate & Reload Data'}
 }
 [['masterSearch','input',()=>{state.page.master=1;master()}],['masterSize','change',()=>{state.page.master=1;master()}],['financingSearch','input',()=>{state.page.financing=1;financing()}],['financingTier','change',()=>{state.page.financing=1;financing()}],['interventionSearch','input',()=>{state.page.intervention=1;intervention()}],['interventionTier','change',()=>{state.page.intervention=1;intervention()}],['interventionType','change',()=>{state.page.intervention=1;intervention()}]].forEach(([id,event,fn])=>$(id).addEventListener(event,fn));
 [['master',master],['financing',financing],['intervention',intervention]].forEach(([key,fn])=>{$(key+'Prev').onclick=()=>{state.page[key]--;fn()};$(key+'Next').onclick=()=>{state.page[key]++;fn()}});
 function fieldLabel(k){return String(k).replace(/_/g,' ').toLowerCase().replace(/\b\w/g,c=>c.toUpperCase())}
 function fieldValue(v){if(v===null||v===undefined||v==='')return '—';if(Array.isArray(v))return v.map(x=>typeof x==='object'?JSON.stringify(x):String(x)).join(', ')||'—';if(typeof v==='object')return JSON.stringify(v,null,2);return String(v)}
 function reasonItems(value){
  if(value===null||value===undefined||value==='')return '<p class="detail-empty">No reasons provided.</p>';
  const values=Array.isArray(value)?value:[value];
  return '<ul class="detail-reasons">'+values.map(v=>`<li>${esc(typeof v==='object'?fieldValue(v):String(v))}</li>`).join('')+'</ul>';
 }
 function fields(record){
  const excluded=/PROVENANCE|SOURCE_FIELD|FIELD_SOURCE/i;
  return Object.entries(record||{}).filter(([k])=>!excluded.test(k)).map(([k,v])=>`<div class="detail-field"><span>${esc(fieldLabel(k))}</span><div>${esc(fieldValue(v))}</div></div>`).join('');
 }
 function financingReasonCards(records){
  return records.map((record,index)=>`<article class="detail-lead-card"><div class="detail-lead-heading">Financing Lead ${index+1}</div>${reasonItems(record.REASONS)}</article>`).join('');
 }
 function interventionReasonCards(records){
  return records.map((record,index)=>`<article class="detail-lead-card"><div class="detail-lead-heading">Intervention ${index+1}</div><div class="detail-intervention-type">${esc(String(record.INTERVENTION_TYPE||'—').replaceAll('_',' '))}</div><div class="detail-reasons-label">Reasons</div>${reasonItems(record.REASONS)}</article>`).join('');
 }
 function openDetails(kind,smeId){
  if(!state.data)return;
  const masterRecord=list(state.data.files.golden.data.GOLDEN_RECORDS).find(x=>String(x.SME_ID)===smeId);
  const financingRecords=list(state.data.files.financing.data.FINANCING_POTENTIAL_LEADS).filter(x=>String(x.SME_ID)===smeId);
  const interventionRecords=list(state.data.files.intervention.data.INTERVENTION_POTENTIAL_LEADS).filter(x=>String(x.SME_ID)===smeId);
  const allRecords=[masterRecord,...financingRecords,...interventionRecords].filter(Boolean);
  const companyName=getCompanyName(masterRecord||allRecords[0]||{});
  const city=firstValue(allRecords,['CITY','TOWN','DISTRICT','MUNICIPALITY']);
  const stateName=firstValue(allRecords,['STATE','STATE_NAME']);
  const sector=firstValue(allRecords,['SECTOR','INDUSTRY','ECONOMIC_SECTOR']);
  const revenue=firstValue(allRecords,['ANNUAL_REVENUE','REVENUE','ANNUAL_SALES','YEARLY_REVENUE','TOTAL_REVENUE']);
  const elsaStage=firstValue(allRecords,['ELSA_STAGE','ELSA_ASSESSMENT_STAGE','ASSESSMENT_STAGE','BUSINESS_STAGE']);
  const financingStatus=financingRecords.length?'Follow-up':'—';
  $('recordModalTitle').textContent=companyName==='—'?(smeId||'SME Details'):companyName;
  $('recordModalSubtitle').textContent='SME Profile';
  const summary=`<section class="detail-overview">
   <div class="detail-company">${esc(companyName)}</div>
   <div class="detail-location">${esc(city||'—')} <span>·</span> ${esc(stateName||'—')}</div>
   <div class="detail-sector">${esc(sector||'—')}</div>
   <div class="detail-sme-id">SME ID: <strong>${esc(smeId||'—')}</strong></div>
   <div class="detail-highlights">
    <div class="detail-highlight"><span>Revenue</span><strong>${esc(formatRM(revenue))}</strong></div>
    <div class="detail-highlight"><span>ELSA Stage</span><strong>${esc(elsaStage||'—')}</strong></div>
    <div class="detail-highlight"><span>Financing Lead</span><strong>${esc(financingStatus)}</strong></div>
   </div>
  </section>`;
  let html=summary;
  if(masterRecord)html+=`<section class="detail-section"><h3>Master Profile Information</h3><div class="detail-fields">${fields(masterRecord)}</div></section>`;
  else html+=`<section class="detail-section"><h3>Master Profile</h3><p class="hint">No matching Golden Record was found for this SME ID.</p></section>`;
  if(financingRecords.length)html+=`<section class="detail-section"><h3>Financing Leads (${financingRecords.length})</h3><div class="detail-lead-list">${financingReasonCards(financingRecords)}</div></section>`;
  if(interventionRecords.length)html+=`<section class="detail-section"><h3>Beyond Financing Leads (${interventionRecords.length})</h3><div class="detail-lead-list">${interventionReasonCards(interventionRecords)}</div></section>`;
  if(!financingRecords.length&&!interventionRecords.length)html+=`<section class="detail-section"><p class="hint">No financing or beyond-financing lead records are linked to this SME ID.</p></section>`;
  $('recordModalBody').innerHTML=html;$('recordModal').hidden=false;document.body.classList.add('modal-open');
 }
 function closeDetails(){$('recordModal').hidden=true;document.body.classList.remove('modal-open')}
 document.addEventListener('click',e=>{const target=e.target.closest('[data-record-kind]');if(target){e.preventDefault();openDetails(target.dataset.recordKind,target.dataset.smeId||'')}});
 $('closeRecordModal').addEventListener('click',closeDetails);
 $('recordModal').addEventListener('click',e=>{if(e.target===$('recordModal'))closeDetails()});
 document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!$('recordModal').hidden)closeDetails()});
 $('validateReload').onclick=reload;reload();
})();