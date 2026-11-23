const $=id=>document.getElementById(id);
let csrf="",playId="",projection=null,auth=false,locked=false;
const escapeHtml=v=>String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const seconds=v=>(v/1000).toFixed(1)+" s";
function note(text,error=false){$("notice").textContent=text;$("notice").className="notice"+(error?" error":"");}
async function get(url){const r=await fetch(url,{cache:"no-store"});if(!r.ok)throw Error("network_"+r.status);return r.json();}
async function post(path,data={}){
  const r=await fetch(path,{method:"POST",headers:{"Content-Type":"application/json","X-Local-Request":csrf},body:JSON.stringify(data),cache:"no-store"});
  if(!r.ok)throw Error("server_"+r.status);
  return r.json();
}
async function busy(fn){if(locked)return;locked=true;updateEnabled();try{await fn();}catch(e){note("Operation blocked: "+e.message,true);}finally{locked=false;updateEnabled();}}
function setSelected(p){projection=p;playId=p?.target_id||"";$("artifact").hidden=true;show();}
async function refresh(select=playId){
  const state=await get("/api/bootstrap"+(select?"?play="+encodeURIComponent(select):""));
  csrf=state.csrf;auth=state.auth.connected;
  $("auth-status").textContent=auth?"Connected to "+state.auth.model+" (session memory only)":"Not signed in. New patient turns are unavailable.";
  $("connect").hidden=auth;$("disconnect").hidden=!auth;
  const catalog=state.catalog?.data?.playable_case_ids||[];
  $("catalog").innerHTML=catalog.map(id=>`<div class="library-item"><div><strong>${escapeHtml(id)}</strong><small>Fictional test case</small></div><button class="secondary" data-case="${escapeHtml(id)}">New play</button></div>`).join("");
  $("sessions").innerHTML=state.sessions.map(s=>`<div class="library-item ${s.playthrough_id===select?"active":""}"><div><strong>${escapeHtml(s.case_id)}</strong><small>${seconds(s.elapsed_ms)} · ${escapeHtml(s.status)}</small></div><button class="secondary" data-play="${escapeHtml(s.playthrough_id)}">Open</button></div>`).join("") || '<p class="muted">No saved encounters yet.</p>';
  setSelected(state.projection);
}
function current(){return projection?.data||{};}
function updateEnabled(){
  const active=!!projection&&projection.status==="active";
  for(const id of ["ask-form","diagnosis-form"]){const e=$(id);for(const c of e.querySelectorAll("input,button,select,textarea"))c.disabled=locked||!active||(id==="ask-form"&&!auth);}
  const orders=current().orders||{};
  $("order-a").disabled=locked||!active||!!orders.A;
  $("order-t").disabled=locked||!active||!!orders.T;
  for(const id of ["wait-1","wait-5","wait-9"])$(id).disabled=locked||!active;
  $("interpret").disabled=locked||!active;
}
function show(){
  const d=current(),orders=d.orders||{},results=d.released_results||{};
  $("encounter-meta").textContent=projection?d.case_id+" · "+projection.status+" · revision "+projection.revision:"Choose a saved encounter or create a new playthrough.";
  $("clock").textContent="t = "+seconds(projection?.elapsed_ms||0);
  const history=d.dialogue_history||[];
  $("transcript").innerHTML=history.map(item=>
    `<div class="bubble learner"><strong>You</strong>${escapeHtml(item.question)}</div><div class="bubble patient"><strong>Patient · fictional</strong>${escapeHtml(item.answer)}</div>`).join("") ||
    '<p class="muted">No conversation recorded. Patient-generated responses are available only when Luna is connected.</p>';
  $("orders").innerHTML=Object.keys(orders).map(k=>{
    const order=orders[k],released=!!results[k];
    return `<div class="order"><span><strong>${escapeHtml(k)}</strong> · ${escapeHtml(order.status)}</span>${released?`<button class="secondary" data-item="${escapeHtml(k)}">Inspect</button>`:"<small>Not released</small>"}</div>`;
  }).join("")||'<p class="muted">No investigations ordered.</p>';
  $("diagnosis-form").hidden=!projection||projection.status!=="active";
  $("debrief").hidden=!projection||projection.status!=="encounter_complete";
  if(projection?.status==="encounter_complete"){
    const deb=d.debrief||{},submission=d.submission||{};
    $("debrief").innerHTML=`<h3>Encounter complete</h3><p>Submitted: <strong>${escapeHtml(submission.leading_diagnosis||"–")}</strong>. Clinical time is frozen at ${seconds(projection.elapsed_ms)}.</p><p>Fictional score and audit:</p><pre>${escapeHtml(JSON.stringify(deb,null,2))}</pre>`+
      (d.review?.status==="prompted"?
      '<form id="review-form"><label>Case quality rating (software fixture) <select name="rating"><option value="5">5</option><option value="4">4</option><option value="3">3</option><option value="2">2</option><option value="1">1</option></select></label><label>Comment<textarea name="comment" maxlength="400" rows="2"></textarea></label><button type="submit">Save review</button><button type="button" id="skip-review" class="ghost">Skip review</button></form>':
      '<p>Post-case review: '+escapeHtml(d.review?.status||"complete")+'</p>');
    const form=$("review-form");
    if(form)form.addEventListener("submit",e=>{e.preventDefault();busy(async()=>{
      const f=new FormData(form);await action("review_case",{rating:Number(f.get("rating")),comment:String(f.get("comment"))});
    });});
    const skip=$("skip-review");if(skip)skip.addEventListener("click",()=>busy(()=>action("skip_review",{})));
  }
  updateEnabled();
}
async function action(kind,payload){
  if(!projection){note("Select a patient first.",true);return;}
  const r=await post("/api/action",{playthrough_id:playId,kind,payload,
    expected_revision:projection.revision,command_id:crypto.randomUUID()});
  if(!r.receipt||r.receipt.status!=="committed"){
    note("No change: "+(r.receipt?.status||r.status)+"."+(r.receipt?.data?.cause?" ("+r.receipt.data.cause+")":""),true);
  }else note("Saved: "+kind.replace(/_/g," ")+".");
  if(r.projection)setSelected(r.projection);
}
const svgNS="http://www.w3.org/2000/svg";
function svgNode(name,attrs={},text=null){
  const node=document.createElementNS(svgNS,name);
  for(const [key,value] of Object.entries(attrs))node.setAttribute(key,String(value));
  if(text!==null)node.textContent=String(text);
  return node;
}
const leadOrder=["I","II","III","aVR","aVL","aVF","V1","V2","V3","V4","V5","V6"];
function validDisplayWaveform(w){
  return !!w&&w.kind==="display_only_synthetic_fixture"&&w.sample_rate_hz===100&&
    w.duration_seconds===10&&w.paper_speed_mm_s===25&&w.gain_mm_per_fixture_mv===10&&
    Array.isArray(w.lead_order)&&w.lead_order.join(",")==leadOrder.join(",")&&
    w.leads&&leadOrder.every(name=>Array.isArray(w.leads[name])&&w.leads[name].length===1000&&
      w.leads[name].every(value=>Number.isFinite(value)&&Math.abs(value)<=2));
}
function plot(samples,waveform){
  const host=$("plot");host.replaceChildren();
  if(validDisplayWaveform(waveform)){
    const width=1090,height=470,x0=70,mmScale=4,pxPerSecond=100,pxPerFixtureMv=40;
    const svg=svgNode("svg",{viewBox:`0 0 ${width} ${height}`,role:"img",
      "aria-label":"Software-generated 12-channel display fixture. Not an ECG or medical evidence."});
    svg.append(svgNode("rect",{x:0,y:0,width,height,fill:"#fffafa"}));
    for(let x=0;x<=width;x+=mmScale){
      const major=x%(5*mmScale)===0;
      svg.append(svgNode("line",{x1:x,y1:0,x2:x,y2:height,stroke:major?"#e6b6bc":"#f5dfe2","stroke-width":major?1:.55}));
    }
    for(let y=0;y<=height;y+=mmScale){
      const major=y%(5*mmScale)===0;
      svg.append(svgNode("line",{x1:0,y1:y,x2:width,y2:y,stroke:major?"#e6b6bc":"#f5dfe2","stroke-width":major?1:.55}));
    }
    svg.append(svgNode("text",{x:16,y:23,class:"signal-title"},"DISPLAY FIXTURE · NOT A MEDICAL ECG"));
    const rows=[["I","aVR","V1","V4"],["II","aVL","V2","V5"],["III","aVF","V3","V6"]];
    const baselines=[86,174,262],segmentSamples=250,segmentWidth=250;
    function pathFor(values,start,count,startX,baseline){
      const points=[];
      for(let j=0;j<count;j++){
        const v=Math.max(-1.2,Math.min(1.2,values[start+j]));
        const x=startX+(j/waveform.sample_rate_hz)*pxPerSecond;
        const y=baseline-v*pxPerFixtureMv;
        points.push(`${x.toFixed(1)},${y.toFixed(1)}`);
      }
      return points.join(" ");
    }
    function calibrationPulse(baseline){
      const x=18,up=baseline-pxPerFixtureMv;
      return `M ${x} ${baseline} L ${x+6} ${baseline} L ${x+6} ${up} L ${x+26} ${up} L ${x+26} ${baseline} L ${x+34} ${baseline}`;
    }
    rows.forEach((row,rowIndex)=>{
      const baseline=baselines[rowIndex];
      svg.append(svgNode("path",{d:calibrationPulse(baseline),fill:"none",stroke:"#234a55","stroke-width":1.5}));
      row.forEach((name,col)=>{
        const start=col*segmentSamples,startX=x0+col*segmentWidth;
        svg.append(svgNode("text",{x:startX+3,y:baseline-31,class:"signal-lead"},name));
        svg.append(svgNode("polyline",{points:pathFor(waveform.leads[name],start,segmentSamples,startX,baseline),
          fill:"none",stroke:"#087d72","stroke-width":1.35,"stroke-linejoin":"round","stroke-linecap":"round"}));
      });
    });
    const rhythmBase=358;
    svg.append(svgNode("text",{x:x0+3,y:rhythmBase-31,class:"signal-lead"},"II · 10 s display strip"));
    svg.append(svgNode("path",{d:calibrationPulse(rhythmBase),fill:"none",stroke:"#234a55","stroke-width":1.5}));
    svg.append(svgNode("polyline",{points:pathFor(waveform.leads.II,0,1000,x0,rhythmBase),
      fill:"none",stroke:"#087d72","stroke-width":1.35,"stroke-linejoin":"round","stroke-linecap":"round"}));
    svg.append(svgNode("text",{x:16,y:448,class:"signal-footer"},
      "Display scale: 25 mm/s · 10 mm/fixture-mV · arbitrary generated shapes and lead relationships · no diagnostic meaning"));
    host.setAttribute("aria-label","Synthetic software display fixture; not an ECG or medical evidence.");
    host.append(svg);
    return;
  }
  const values=Array.isArray(samples)?samples.filter(Number.isFinite):[];
  const width=800,height=190,svg=svgNode("svg",{viewBox:`0 0 ${width} ${height}`,role:"img",
    "aria-label":"Legacy fictional sample plot; not medical evidence."});
  svg.append(svgNode("rect",{x:0,y:0,width,height,fill:"#fbfefe"}));
  for(let x=0;x<=width;x+=24)svg.append(svgNode("line",{x1:x,y1:0,x2:x,y2:height,stroke:"#e7eff0","stroke-width":1}));
  for(let y=0;y<=height;y+=24)svg.append(svgNode("line",{x1:0,y1:y,x2:width,y2:y,stroke:"#e7eff0","stroke-width":1}));
  svg.append(svgNode("text",{x:16,y:22,class:"signal-title"},"LEGACY FICTIONAL SAMPLE PLOT · NOT MEDICAL EVIDENCE"));
  if(values.length){
    const min=Math.min(...values)-.6,max=Math.max(...values)+.6,span=max-min||1;
    const points=values.map((value,index)=>`${30+(width-60)*(values.length===1?0.5:index/(values.length-1))},${18+(height-36)*(1-(value-min)/span)}`).join(" ");
    svg.append(svgNode("polyline",{points,fill:"none",stroke:"#087d72","stroke-width":3,"stroke-linejoin":"round"}));
  }
  host.append(svg);
}
async function inspect(item){
  const r=await post("/api/asset",{playthrough_id:playId,item_id:item});
  if(r.status!=="available"){note("Artifact withheld: "+r.status,true);return;}
  const a=r.artifact||{};
  $("artifact").hidden=false;$("interpret").hidden=item!=="T";
  $("artifact").dataset.item=item;
  plot(a.samples||(a.value!==undefined?[a.value]:[]),a.display_waveform);
  const alternative=await post("/api/asset",{playthrough_id:playId,item_id:item,text:true});
  $("artifact-data").textContent=alternative.artifact?.text||"Synthetic data";
  if(!a.display_waveform){
    $("artifact-data").textContent+="\nExact source samples: "+JSON.stringify(a.samples||a.value)+
      "\nUnits: "+(a.units||"not provided");
  }
  $("interpretation").textContent="";
  if(projection.status==="active")await action("open_artifact",{item_id:item});
  $("artifact").hidden=false;
}
$("connect").addEventListener("click",()=>busy(async()=>{
  const r=await post("/api/auth/start");if(!r.url)throw Error("authorization_unavailable");
  note("Opening the official consent page…");location.assign(r.url);
}));
$("disconnect").addEventListener("click",()=>busy(async()=>{await post("/api/auth/logout");await refresh();note("Luna disconnected.");}));
$("catalog").addEventListener("click",e=>{const b=e.target.closest("[data-case]");if(!b)return;busy(async()=>{
  const r=await post("/api/start",{case_id:b.dataset.case});
  if(r.status!=="committed")throw Error(r.status);await refresh(r.playthrough_id);note("Created a separate saved playthrough.");
});});
$("sessions").addEventListener("click",e=>{const b=e.target.closest("[data-play]");if(b)busy(async()=>{
  await refresh(b.dataset.play);note("Loaded saved encounter from local SQLite.");
});});
$("ask-form").addEventListener("submit",e=>{e.preventDefault();const q=$("question").value.trim();if(!q)return;busy(async()=>{
  await action("ask_patient",{question:q});$("question").value="";
});});
$("order-a").addEventListener("click",()=>busy(()=>action("order_tests",{items:[{item_id:"A",kind:"point"}]})));
$("order-t").addEventListener("click",()=>busy(()=>action("order_tests",{items:[{item_id:"T",kind:"trace"}]})));
for(const [id,ms] of [["wait-1",1000],["wait-5",5000],["wait-9","until9"]]){
  $(id).addEventListener("click",()=>busy(()=>action("wait",{duration_ms:ms==="until9"?Math.max(0,9000-(projection?.elapsed_ms||0)):ms})));
}
$("orders").addEventListener("click",e=>{const b=e.target.closest("[data-item]");if(b)busy(()=>inspect(b.dataset.item));});
$("interpret").addEventListener("click",()=>busy(async()=>{
  const item=$("artifact").dataset.item;
  if(item!=="T")return;
  await action("request_interpretation",{item_id:item,explanation:auth});
  const aid=(current().interpretation_aids||[]).at(-1);
  $("artifact").hidden=false;
  const assessment=aid?.assessment||{};
  $("interpretation").textContent=assessment.summary||"No safe reference interpretation is available for this synthetic fixture.";
  if(assessment.limitations)$("interpretation").textContent+="\n"+assessment.limitations;
  $("interpretation").textContent+="\nExplanation status: "+(aid?.explanation_status||"unavailable");
}));
$("diagnosis-form").addEventListener("submit",e=>{e.preventDefault();const a=$("leading").value,b=$("alternative").value;
  busy(()=>action("submit_diagnosis",{leading_diagnosis:a,differential:b&&b!==a?[a,b]:[a],reasoning:$("reasoning").value}));
});
refresh().then(()=>note("Ready: select a fictional patient.")).catch(e=>note("Cannot load local backend: "+e.message,true));
