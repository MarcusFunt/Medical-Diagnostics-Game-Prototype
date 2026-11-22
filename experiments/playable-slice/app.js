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
function plot(samples){
  const c=$("plot"),ctx=c.getContext("2d");ctx.clearRect(0,0,c.width,c.height);
  ctx.fillStyle="#fbfefe";ctx.fillRect(0,0,c.width,c.height);
  ctx.strokeStyle="#dfe9eb";ctx.lineWidth=1;
  for(let x=0;x<c.width;x+=28){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,c.height);ctx.stroke();}
  for(let y=0;y<c.height;y+=28){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(c.width,y);ctx.stroke();}
  if(!Array.isArray(samples)||!samples.length)return;
  const min=Math.min(...samples)-.6,max=Math.max(...samples)+.6;
  ctx.strokeStyle="#05867c";ctx.lineWidth=3;ctx.beginPath();
  samples.forEach((v,i)=>{const x=30+(c.width-60)*(samples.length===1?0.5:i/(samples.length-1));
    const y=12+(c.height-24)*(1-(v-min)/(max-min));i?ctx.lineTo(x,y):ctx.moveTo(x,y);});
  ctx.stroke();
}
async function inspect(item){
  const r=await post("/api/asset",{playthrough_id:playId,item_id:item});
  if(r.status!=="available"){note("Artifact withheld: "+r.status,true);return;}
  const a=r.artifact||{};
  $("artifact").hidden=false;$("interpret").hidden=item!=="T";
  $("artifact").dataset.item=item;
  plot(a.samples||(a.value!==undefined?[a.value]:[]));
  const alternative=await post("/api/asset",{playthrough_id:playId,item_id:item,text:true});
  $("artifact-data").textContent=(alternative.artifact?.text||"Synthetic data")+
    "\nExact source samples: "+JSON.stringify(a.samples||a.value)+
    "\nUnits: "+(a.units||"not provided");
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
  $("interpretation").textContent=aid?JSON.stringify(aid.assessment,null,2)+
    (aid.explanation?"\nLuna: "+aid.explanation:"\nExplanation status: "+aid.explanation_status):"No authorized interpretation available.";
}));
$("diagnosis-form").addEventListener("submit",e=>{e.preventDefault();const a=$("leading").value,b=$("alternative").value;
  busy(()=>action("submit_diagnosis",{leading_diagnosis:a,differential:b&&b!==a?[a,b]:[a],reasoning:$("reasoning").value}));
});
refresh().then(()=>note("Ready: select a fictional patient.")).catch(e=>note("Cannot load local backend: "+e.message,true));
