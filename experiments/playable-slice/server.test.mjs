import test from "node:test";
import assert from "node:assert/strict";
import { restrictModelInput, normalizeLunaResult, ensureToken } from "./server.mjs";

test("model context contains no concealed case key",()=>{
  const safe=restrictModelInput("dialogue",{role:"patient",question:"Prior episodes?",facts:[
    {fact_id:"subjective-prior-episodes",text:"The patient recalls one prior fictional episode.",source:"subjective_report"}
  ]});
  assert.doesNotMatch(JSON.stringify(safe),/reference_key|DX-A|hidden_diagnosis/);
  assert.throws(()=>restrictModelInput("dialogue",{role:"patient",question:"",facts:[
    {fact_id:"secret",text:"DX-A",source:"private"}
  ]}));
  assert.throws(()=>restrictModelInput("explanation",{assessment:{status:"unavailable"}}));
});
test("unapproved assertions and fake diagnosis are rejected",()=>{
  assert.equal(normalizeLunaResult("dialogue",'{"text":"DX-A","fact_refs":[],"subjective_report":true,"uncertainty":true}').status,"unsupported_assertion");
  assert.equal(normalizeLunaResult("dialogue",'{"text":"I remember one prior episode.","fact_refs":["subjective-prior-episodes"],"subjective_report":true}').status,"success");
  assert.equal(normalizeLunaResult("dialogue","not json").status,"invalid_model_output");
});
test("token refresh rotates while active and fails closed on errors",async()=>{
  const s={accessToken:"old",refreshToken:"before",expiresAt:0};
  const t=await ensureToken(s,async()=>({access_token:"new",refresh_token:"after",token_type:"Bearer",expires_in:3600}));
  assert.equal(t,"new");assert.equal(s.refreshToken,"after");
  assert.equal(await ensureToken(s,async()=>{throw Error("unexpected_refresh");}),"new");
  const expired={accessToken:"old",refreshToken:"old",expiresAt:0};
  await assert.rejects(()=>ensureToken(expired,async()=>{throw Error("denied");}),/refresh_blocked/);
});
