import assert from "node:assert/strict";
import { generateKeyPairSync, sign } from "node:crypto";
import test from "node:test";
import * as siwc from "./siwc-smoke.mjs";

const encode = (value) => Buffer.from(JSON.stringify(value)).toString("base64url");

function signedIdToken(claims, privateKey, kid = "test-key") {
  const header = encode({ alg: "RS256", kid, typ: "JWT" });
  const payload = encode(claims);
  const signingInput = `${header}.${payload}`;
  const signature = sign("RSA-SHA256", Buffer.from(signingInput), privateKey).toString("base64url");
  return `${signingInput}.${signature}`;
}

test("creates the RFC 7636 S256 PKCE challenge", () => {
  assert.equal(typeof siwc.pkceChallenge, "function", "pkceChallenge must be exported");
  assert.equal(
    siwc.pkceChallenge("dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"),
    "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM",
  );
});

test("pins SIWC inference to the listable GPT-6 Luna model", () => {
  assert.equal(typeof siwc.selectRequiredModel, "function", "selectRequiredModel must be exported");
  assert.equal(siwc.selectRequiredModel([
    { slug: "gpt-6.2-sol", visibility: "list" },
    { slug: "gpt-6-luna", visibility: "list" },
  ]), "gpt-6-luna");
  assert.throws(() => siwc.selectRequiredModel([
    { slug: "gpt-6.2-sol", visibility: "list" },
    { slug: "gpt-6-luna", visibility: "hidden" },
  ]), /not_listable/);
});

test("verifies ID-token signature and required claims", () => {
  assert.equal(typeof siwc.verifyIdentityToken, "function", "verifyIdentityToken must be exported");
  const { publicKey, privateKey } = generateKeyPairSync("rsa", { modulusLength: 2048 });
  const jwk = { ...publicKey.export({ format: "jwk" }), kid: "test-key", alg: "RS256", use: "sig" };
  const now = 1_800_000_000;
  const token = signedIdToken(
    { iss: "https://auth.openai.com", aud: "oaiapp_test", sub: "subject-1", nonce: "nonce-1", exp: now + 60, iat: now - 1 },
    privateKey,
  );

  assert.equal(
    siwc.verifyIdentityToken(token, { keys: [jwk] }, {
      issuer: "https://auth.openai.com",
      audience: "oaiapp_test",
      nonce: "nonce-1",
      now,
    }).sub,
    "subject-1",
  );
  assert.throws(() => siwc.verifyIdentityToken(token, { keys: [jwk] }, {
    issuer: "https://auth.openai.com",
    audience: "oaiapp_test",
    nonce: "wrong-nonce",
    now,
  }), /nonce/);
  assert.throws(() => siwc.verifyIdentityToken(token, { keys: [jwk] }, {
    issuer: "https://auth.openai.com",
    audience: "another-client",
    nonce: "nonce-1",
    now,
  }), /audience/);
});

test("reads SSE events split across chunks and requires response.completed", async () => {
  assert.equal(typeof siwc.readSseEvents, "function", "readSseEvents must be exported");
  assert.equal(typeof siwc.consumeResponseStream, "function", "consumeResponseStream must be exported");
  const encoder = new TextEncoder();
  const chunks = ["event: response.output_text.delta\ndata: {\"type\":\"response.output_text.delta\",", "\"delta\":\"ok\"}\n\nevent: response.completed\ndata: {\"type\":\"response.completed\"}\n\n"];
  const stream = new ReadableStream({
    start(controller) {
      for (const chunk of chunks) controller.enqueue(encoder.encode(chunk));
      controller.close();
    },
  });
  const events = [];
  for await (const event of siwc.readSseEvents(stream)) events.push(event);
  assert.deepEqual(events.map((event) => event.type), ["response.output_text.delta", "response.completed"]);
  assert.equal((await siwc.consumeResponseStream(new ReadableStream({
    start(controller) {
      controller.enqueue(encoder.encode("data: {\"type\":\"response.completed\"}\n\n"));
      controller.close();
    },
  }))).completed, true);

  const incomplete = new ReadableStream({
    start(controller) {
      controller.enqueue(encoder.encode("data: {\"type\":\"response.failed\",\"response\":{\"error\":{\"code\":\"denied\"}}}\n\n"));
      controller.close();
    },
  });
  await assert.rejects(siwc.consumeResponseStream(incomplete), /denied/);
  await assert.rejects(siwc.consumeResponseStream(new ReadableStream({
    start(controller) {
      controller.enqueue(encoder.encode("data: {\"type\":\"response.output_text.delta\",\"delta\":\"partial\"}\n\n"));
      controller.close();
    },
  })), /response.completed/);
});
