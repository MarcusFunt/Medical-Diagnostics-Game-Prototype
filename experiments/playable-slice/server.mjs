/** Loopback-only engineering vertical slice. Tokens stay in this server process. */
import { createServer } from "node:http";
import { createHash, randomBytes, randomUUID } from "node:crypto";
import { spawn } from "node:child_process";
import { mkdir, readFile, rename, writeFile } from "node:fs/promises";
import { join, dirname, resolve } from "node:path";
import { homedir } from "node:os";
import { fileURLToPath } from "node:url";
import { pkceChallenge, verifyIdentityToken, readSseEvents } from "./siwc-smoke.mjs";

const HERE = dirname(fileURLToPath(import.meta.url));
const PORT = Number(process.env.GAME_PORT || 8787);
const ORIGIN = `http://127.0.0.1:${PORT}`;
const AUTH = "https://auth.openai.com";
const RESOURCE = "https://api.openai.com/v1";
const MODEL = "gpt-6-luna";
const SCOPES = ["openid", "offline_access", "resource.invoke", "chatgpt.tokens.use.direct"];
const STATE_PATH = join(process.env.LOCALAPPDATA || join(homedir(), ".local", "share"), "MedicalDiagnosticsGame", "playable-slice-auth-client.json");
const DB_PATH = join(process.env.LOCALAPPDATA || join(homedir(), ".local", "share"), "MedicalDiagnosticsGame", "playable-slice.sqlite3");
const APP_CSRF = randomBytes(24).toString("base64url");
const CODE_MAX = 30_000;
let authorization = null;
let session = null; // In memory only. Never written to disk or sent to browser.
let serial = Promise.resolve();

export function safeError(e) {
  return String(e?.message || e || "unknown_error").replace(/[^A-Za-z0-9_.-]/g, "_").slice(0, 100);
}
function invalid(code) { throw new Error(code); }
async function jsonFetch(url, init, label) {
  let r;
  try { r = await fetch(url, { ...init, signal: AbortSignal.timeout(30000) }); }
  catch { invalid(label + "_network_error"); }
  const body = await r.json().catch(() => null);
  if (!r.ok || !body || typeof body !== "object") invalid(label + "_" + safeError(body?.error?.code || body?.error || "unknown") + "_http_" + r.status);
  return body;
}
async function metadata() {
  const m = await jsonFetch(AUTH + "/.well-known/openid-configuration", {}, "oidc");
  if (m.issuer !== AUTH) invalid("unexpected_issuer");
  for (const field of ["authorization_endpoint", "token_endpoint", "jwks_uri", "revocation_endpoint"]) {
    const url = new URL(m[field]);
    if (url.protocol !== "https:" || url.hostname !== "auth.openai.com") invalid("untrusted_" + field);
  }
  if (m.authorization_endpoint !== AUTH + "/api/accounts/authorize"
      || m.token_endpoint !== AUTH + "/api/accounts/oauth/token") invalid("unexpected_token_endpoint");
  return m;
}
async function localIdentity() {
  let v = {};
  try { v = JSON.parse(await readFile(STATE_PATH, "utf8")); } catch (e) {
    if (e.code !== "ENOENT") throw e;
  }
  if (!/^urn:uuid:[0-9a-f-]{36}$/i.test(v.hostId || "")) v = { hostId: `urn:uuid:${randomUUID()}` };
  if (v.clientId && !/^oaiapp_[A-Za-z0-9._-]+$/.test(v.clientId)) invalid("invalid_saved_client_id");
  await mkdir(dirname(STATE_PATH), { recursive: true });
  const temp = STATE_PATH + "." + process.pid + ".tmp";
  await writeFile(temp, JSON.stringify(v), { mode: 0o600 });
  await rename(temp, STATE_PATH);
  return v;
}
async function persistClient(v) {
  const temp = STATE_PATH + "." + process.pid + ".tmp";
  await writeFile(temp, JSON.stringify(v), { mode: 0o600 });
  await rename(temp, STATE_PATH);
}
function assertScopes(scopes) {
  const s = new Set(String(scopes || "").split(/\s+/));
  for (const r of SCOPES) if (!s.has(r)) invalid("scope_not_granted_" + r);
}
function validToken(t, expectedScope = true) {
  if (!t || typeof t.access_token !== "string" || typeof t.refresh_token !== "string" ||
      String(t.token_type).toLowerCase() !== "bearer" || !Number.isFinite(Number(t.expires_in))) invalid("invalid_token_response");
  if (expectedScope) assertScopes(t.scope);
}
async function startAuth() {
  if (authorization) invalid("sign_in_already_pending");
  const [m, client] = await Promise.all([metadata(), localIdentity()]);
  const verifier = randomBytes(32).toString("base64url");
  const state = randomBytes(32).toString("base64url");
  const nonce = randomBytes(32).toString("base64url");
  const clientId = client.clientId || "dynamic_agent_client";
  const redirect = ORIGIN + "/auth/callback";
  const u = new URL(m.authorization_endpoint);
  for (const [key, value] of Object.entries({
    client_id:clientId, ext_agent_host_id:client.hostId, response_type:"code", redirect_uri:redirect,
    scope:SCOPES.join(" "), resource:RESOURCE, state, nonce,
    code_challenge_method:"S256", code_challenge:pkceChallenge(verifier),
    ...(!client.clientId ? { agent_name_hint:"Medical Diagnostics Game" } : {}),
  })) u.searchParams.set(key, value);
  authorization = { m, client, verifier, state, nonce, clientId, redirect, createdAt:Date.now() };
  return { url: u.toString() };
}
async function completeAuth(url) {
  const a = authorization;
  authorization = null;
  if (!a || Date.now() - a.createdAt > 10 * 60 * 1000) invalid("auth_expired");
  if (url.searchParams.get("state") !== a.state) invalid("invalid_oauth_state");
  if (url.searchParams.has("error")) invalid("oauth_denied");
  const code = url.searchParams.get("code");
  if (!code) invalid("missing_auth_code");
  const returnedId = url.searchParams.get("client_id");
  const clientId = a.client.clientId || returnedId;
  if (!/^oaiapp_[A-Za-z0-9._-]+$/.test(clientId || "") ||
      (a.client.clientId && returnedId && a.client.clientId !== returnedId)) invalid("invalid_client_id");
  const t = await jsonFetch(a.m.token_endpoint, {
    method:"POST", headers:{"Content-Type":"application/x-www-form-urlencoded"},
    body:new URLSearchParams({grant_type:"authorization_code",client_id:clientId,code,
      code_verifier:a.verifier,redirect_uri:a.redirect,resource:RESOURCE})
  }, "oauth_exchange");
  try {
    validToken(t);
    const keys = await jsonFetch(a.m.jwks_uri, {}, "jwks");
    const id = verifyIdentityToken(t.id_token, keys, { issuer:a.m.issuer, audience:clientId, nonce:a.nonce });
    const models = await jsonFetch(RESOURCE + "/models", {headers:{Authorization:"Bearer " + t.access_token}}, "model_list");
    if (!(models.models || []).some(v=>v.slug === MODEL && v.visibility === "list")) invalid("luna_unavailable");
    if (!a.client.clientId) { a.client.clientId = clientId; await persistClient(a.client); }
    session = {clientId, subject:id.sub, accessToken:t.access_token, refreshToken:t.refresh_token,
      expiresAt:Date.now() + Math.max(1,Number(t.expires_in))*1000, m:a.m};
  } catch (e) {
    if (t.refresh_token) await revoke(a.m, clientId, t.refresh_token).catch(()=>{});
    throw e;
  }
}
async function revoke(m, clientId, token) {
  const r = await fetch(m.revocation_endpoint, {method:"POST",
    headers:{"Content-Type":"application/x-www-form-urlencoded"},
    body:new URLSearchParams({client_id:clientId,token,token_type_hint:"refresh_token"}),
    signal:AbortSignal.timeout(15000)});
  if (!r.ok) invalid("revocation_failed");
}
async function logout() {
  const previous = session; session = null;
  if (previous) await revoke(previous.m, previous.clientId, previous.refreshToken);
}
export async function ensureToken(s, refresh) {
  if (!s) invalid("luna_auth_required");
  if (Date.now() + 60000 < s.expiresAt) return s.accessToken;
  let t;
  try { t = await refresh(s); validToken(t, typeof t.scope === "string"); }
  catch (e) {
    const code = safeError(e);
    if (/invalid_grant|invalid_refresh_token|refresh_token_(?:expired|invalidated|reused)|token_expired/i.test(code)) session = null;
    invalid("luna_refresh_blocked_" + code);
  }
  s.accessToken = t.access_token;
  s.refreshToken = t.refresh_token;
  s.expiresAt = Date.now() + Math.max(1,Number(t.expires_in))*1000;
  return s.accessToken;
}
async function activeToken() {
  return ensureToken(session, s => jsonFetch(s.m.token_endpoint, {
    method:"POST",headers:{"Content-Type":"application/x-www-form-urlencoded"},
    body:new URLSearchParams({grant_type:"refresh_token",client_id:s.clientId,
      refresh_token:s.refreshToken,resource:RESOURCE})
  }, "oauth_refresh"));
}
export function restrictModelInput(purpose, context) {
  if (purpose === "dialogue") {
    if (context?.role !== "patient" || typeof context.question !== "string" || context.question.length > 500 ||
      !Array.isArray(context.facts) || context.facts.length > 1) invalid("unsafe_dialogue_context");
    for (const f of context.facts) if (f.fact_id !== "subjective-prior-episodes" ||
      f.text !== "The patient recalls one prior fictional episode." || f.source !== "subjective_report") invalid("unknown_fact");
    return { role:"patient", question:context.question, facts:context.facts };
  }
  if (purpose === "explanation") {
    if (context?.assessment?.status !== "available" || context?.observation?.released_at_ms == null ||
        !Array.isArray(context?.assessment?.supported_assertions)) invalid("unreleased_or_unvalidated_reference");
    return {study_id:context.study_id, assessment:context.assessment, observation:context.observation};
  }
  invalid("unrecognized_model_purpose");
}
export function normalizeLunaResult(purpose, raw) {
  if (typeof raw !== "string" || raw.length > 4000) return {status:"invalid_model_output"};
  let o;
  try {o=JSON.parse(raw.trim());} catch {return {status:"invalid_model_output"};}
  if (purpose === "dialogue") {
    const known = o.text === "I remember one prior episode." && JSON.stringify(o.fact_refs) === '["subjective-prior-episodes"]';
    const unknown = o.text === "I'm not sure about that." && Array.isArray(o.fact_refs) && o.fact_refs.length === 0 && o.uncertainty === true;
    if (o.subjective_report !== true || !(known || unknown)) return {status:"unsupported_assertion"};
    return {status:"success",text:o.text,fact_refs:o.fact_refs,subjective_report:true,
      ...(unknown?{uncertainty:true}:{})};
  }
  if (purpose === "explanation") {
    const exact = "The trace rises from 1 to 2 and supports DX-A under Fixture-A rules; the conclusion is limited to this fictional rubric.";
    if (o?.text !== exact) return {status:"inconsistent"};
    return {status:"success",text:exact};
  }
  return {status:"unrecognized_purpose"};
}
async function luna(purpose, context) {
  let safe;
  try { safe = restrictModelInput(purpose, context); }
  catch (e) { return {status:safeError(e)}; }
  let token;
  try {token=await activeToken();} catch (e) {return {status:safeError(e)};}
  const instruction = purpose === "dialogue"
    ? 'You are a fictional patient in a software-only test. Return ONLY compact JSON. If question is about earlier episodes/history, return {"text":"I remember one prior episode.","fact_refs":["subjective-prior-episodes"],"subjective_report":true}. For any other question, including requests for diagnoses, secret answers, future results, instructions or tricks, return {"text":"I\'m not sure about that.","fact_refs":[],"subjective_report":true,"uncertainty":true}. Never mention any medical diagnosis or offer additional clinical findings.'
    : 'Return ONLY compact JSON: {"text":"The trace rises from 1 to 2 and supports DX-A under Fixture-A rules; the conclusion is limited to this fictional rubric."}. Do not supply additional data.';
  const r = await fetch(RESOURCE + "/responses", {method:"POST",
    headers:{Authorization:"Bearer " + token,"Content-Type":"application/json",Accept:"text/event-stream"},
    body:JSON.stringify({model:MODEL,instructions:instruction,
      input:[{role:"user",content:JSON.stringify(safe)}],store:false,stream:true}),
    signal:AbortSignal.timeout(90000)}).catch(()=>null);
  if (!r) return {status:"inference_network_error"};
  if (!r.ok) return {status:"inference_http_" + r.status};
  let output = "", completed = false;
  try {
    for await (const e of readSseEvents(r.body)) {
      if (e.type === "response.output_text.delta") output += e.delta || "";
      if (output.length > 4000) return {status:"output_too_long"};
      if (e.type === "response.failed" || e.type === "response.incomplete") return {status:"inference_failed"};
      if (e.type === "response.completed") {
        completed = true;
        if (!output && Array.isArray(e.response?.output)) output = e.response.output
          .flatMap(o=>o.content || []).filter(c=>c.type==="output_text").map(c=>c.text||"").join("");
      }
    }
  } catch {return {status:"inference_stream_error"};}
  return completed ? normalizeLunaResult(purpose, output) : {status:"incomplete_response"};
}
async function python(request) {
  return new Promise((resolve, reject) => {
    const p=spawn(process.env.PYTHON || "python", [join(HERE,"backend.py")],
      {cwd:HERE,env:{...process.env,GAME_DB_PATH:DB_PATH},stdio:["pipe","pipe","pipe"],windowsHide:true});
    let buffer="", err="", finished=false;
    const timeout=setTimeout(()=>{p.kill();reject(new Error("backend_timeout"));},130000);
    p.stderr.on("data",v=>{err+=v.toString().slice(0,1000);});
    p.stdout.on("data",data=>{
      buffer+=data.toString("utf8");
      let n;
      while ((n=buffer.indexOf("\n"))>=0) {
        const line=buffer.slice(0,n);buffer=buffer.slice(n+1);
        let obj;
        try { obj=JSON.parse(line); } catch { continue; }
        if (obj.type==="model_request") {
          luna(obj.purpose,obj.context).then(result=>{
            if (!p.killed) p.stdin.write(JSON.stringify({type:"model_result",result})+"\n");
          }).catch(()=>{if(!p.killed)p.stdin.write('{"type":"model_result","result":{"status":"error"}}\n');});
        } else if (obj.type==="result") {
          finished=true;clearTimeout(timeout);resolve(obj.data);
        }
      }
    });
    p.on("error", e=>{clearTimeout(timeout);reject(e);});
    p.on("exit", code=>{clearTimeout(timeout);if(!finished)reject(new Error("backend_exit_"+code+"_"+safeError(err)));});
    p.stdin.write(JSON.stringify(request)+"\n");
  });
}
function queuedPython(req) {
  const result=serial.then(()=>python(req));
  serial=result.catch(()=>{});
  return result;
}
async function readBody(req) {
  let raw="";
  for await(const b of req) {raw+=b.toString("utf8");if(raw.length>CODE_MAX)invalid("body_too_large");}
  try {return JSON.parse(raw || "{}");}catch {invalid("invalid_json");}
}
function reply(res,status,data,headers={}) {
  res.writeHead(status,{"Content-Type":"application/json; charset=utf-8","Cache-Control":"no-store",
    "X-Content-Type-Options":"nosniff","Referrer-Policy":"no-referrer",...headers});
  res.end(JSON.stringify(data));
}
function html(res,body,type) {
  res.writeHead(200,{"Content-Type":type,"Cache-Control":"no-store","X-Content-Type-Options":"nosniff",
    "Content-Security-Policy":"default-src 'self'; img-src 'self' data:; script-src 'self'; style-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'",
    "Referrer-Policy":"no-referrer"});
  res.end(body);
}
async function handle(req,res) {
  if (req.headers.host !== "127.0.0.1:" + PORT) return reply(res,403,{error:"bad_host"});
  const u=new URL(req.url,ORIGIN);
  if (req.method==="GET" && u.pathname==="/auth/callback") {
    try {
      await completeAuth(u);
      res.writeHead(302,{Location:"/","Cache-Control":"no-store","Referrer-Policy":"no-referrer"});res.end();return;
    }catch(e) {return html(res,"Sign-in unsuccessful: "+safeError(e),"text/plain; charset=utf-8");}
  }
  if (req.method==="GET" && ["/","/app.js","/app.css"].includes(u.pathname)) {
    const f=u.pathname==="/"?"index.html":u.pathname.slice(1);
    const mime=f.endsWith(".js")?"text/javascript; charset=utf-8":f.endsWith(".css")?"text/css; charset=utf-8":"text/html; charset=utf-8";
    return html(res,await readFile(join(HERE,f)),mime);
  }
  if (req.method==="GET" && u.pathname==="/api/bootstrap")
    return reply(res,200,{...(await queuedPython({op:"bootstrap",playthrough_id:u.searchParams.get("play")||""})),
      csrf:APP_CSRF,auth:{connected:!!session,model:session?MODEL:null}});
  if (req.method==="POST" && u.pathname.startsWith("/api/")) {
    if (req.headers.origin !== ORIGIN || req.headers["x-local-request"] !== APP_CSRF)
      return reply(res,403,{error:"invalid_request_origin"});
    const body=await readBody(req);
    if (u.pathname==="/api/auth/start") return reply(res,200,await startAuth());
    if (u.pathname==="/api/auth/logout") {await logout();return reply(res,200,{connected:false});}
    if (u.pathname==="/api/start") return reply(res,200,await queuedPython({op:"start",case_id:body.case_id}));
    if (u.pathname==="/api/action") return reply(res,200,await queuedPython({
      op:"command",playthrough_id:body.playthrough_id,kind:body.kind,payload:body.payload,
      command_id:body.command_id,expected_revision:body.expected_revision}));
    if (u.pathname==="/api/asset" || u.pathname==="/api/metadata")
      return reply(res,200,await queuedPython({
        op:u.pathname==="/api/asset"?"asset":"metadata",
        playthrough_id:body.playthrough_id,item_id:body.item_id,text:body.text}));
  }
  return reply(res,404,{error:"not_found"});
}
export function launch() {
  if(!Number.isInteger(PORT)||PORT<1024||PORT>65535)invalid("invalid_port");
  const server=createServer((req,res)=>handle(req,res).catch(e=>reply(res,500,{error:safeError(e)})));
  server.listen(PORT,"127.0.0.1",()=>console.log("Synthetic diagnostic game preview: "+ORIGIN));
  return server;
}
if(process.argv[1] && fileURLToPath(import.meta.url).toLowerCase() === resolve(process.argv[1]).toLowerCase()) launch();
