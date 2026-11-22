import { createHash, createPublicKey, randomBytes, randomUUID, timingSafeEqual, verify } from "node:crypto";
import { spawn } from "node:child_process";
import { createServer } from "node:http";
import { mkdir, readFile, rename, writeFile } from "node:fs/promises";
import { homedir } from "node:os";
import { dirname, join } from "node:path";
import { pathToFileURL } from "node:url";

const AUTH_ORIGIN = "https://auth.openai.com";
const RESOURCE = "https://api.openai.com/v1";
const AUTHORIZE_ENDPOINT = `${AUTH_ORIGIN}/api/accounts/authorize`;
const TOKEN_ENDPOINT = `${AUTH_ORIGIN}/api/accounts/oauth/token`;
const CALLBACK_PATH = "/auth/callback";
const SCOPES = "openid offline_access resource.invoke chatgpt.tokens.use.direct";
const REQUIRED_MODEL = "gpt-6-luna";
const APP_NAME = "Medical Diagnostics Game";

export function pkceChallenge(verifier) {
  return createHash("sha256").update(verifier, "ascii").digest("base64url");
}

export function selectRequiredModel(models) {
  const selected = Array.isArray(models)
    ? models.find((model) => model?.slug === REQUIRED_MODEL && model.visibility === "list")
    : undefined;
  if (!selected) throw new Error("siwc_required_model_not_listable_gpt_6_luna");
  return selected.slug;
}

export function verifyIdentityToken(token, jwks, { issuer, audience, nonce, now = Math.floor(Date.now() / 1000) }) {
  const parts = typeof token === "string" ? token.split(".") : [];
  if (parts.length !== 3) throw new Error("invalid_id_token_format");

  let header;
  let claims;
  try {
    header = JSON.parse(Buffer.from(parts[0], "base64url").toString("utf8"));
    claims = JSON.parse(Buffer.from(parts[1], "base64url").toString("utf8"));
  } catch {
    throw new Error("invalid_id_token_json");
  }

  if (header.alg !== "RS256" || typeof header.kid !== "string") throw new Error("unsupported_id_token_signing_key");
  const jwk = jwks?.keys?.find((key) => key.kid === header.kid && key.kty === "RSA" && (!key.use || key.use === "sig") && (!key.alg || key.alg === "RS256"));
  if (!jwk) throw new Error("id_token_signing_key_not_found");

  let signatureValid = false;
  try {
    const publicKey = createPublicKey({ key: jwk, format: "jwk" });
    signatureValid = verify("RSA-SHA256", Buffer.from(`${parts[0]}.${parts[1]}`, "ascii"), publicKey, Buffer.from(parts[2], "base64url"));
  } catch {
    throw new Error("invalid_id_token_signature");
  }
  if (!signatureValid) throw new Error("invalid_id_token_signature");

  if (claims.iss !== issuer) throw new Error("invalid_id_token_issuer");
  const audiences = Array.isArray(claims.aud) ? claims.aud : [claims.aud];
  if (!audiences.includes(audience) || (audiences.length > 1 && claims.azp !== audience)) throw new Error("invalid_id_token_audience");
  if (!Number.isFinite(claims.exp) || claims.exp <= now) throw new Error("expired_id_token");
  if (!equalSecret(claims.nonce, nonce)) throw new Error("invalid_id_token_nonce");
  if (typeof claims.sub !== "string" || claims.sub.length === 0) throw new Error("invalid_id_token_subject");
  return claims;
}

export async function* readSseEvents(stream) {
  if (!stream?.getReader) throw new Error("responses_stream_missing");
  const reader = stream.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  const parseFrame = (frame) => {
    const data = frame.split(/\r?\n/).filter((line) => line.startsWith("data:")).map((line) => line.slice(5).trimStart()).join("\n");
    if (!data || data === "[DONE]") return null;
    try {
      return JSON.parse(data);
    } catch {
      throw new Error("invalid_responses_sse_event");
    }
  };

  try {
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      let boundary;
      while ((boundary = buffer.search(/\r?\n\r?\n/)) !== -1) {
        const frame = buffer.slice(0, boundary);
        const delimiter = buffer.slice(boundary).match(/^\r?\n\r?\n/)[0];
        buffer = buffer.slice(boundary + delimiter.length);
        const event = parseFrame(frame);
        if (event) yield event;
      }
    }
    buffer += decoder.decode();
    if (buffer.trim()) {
      const event = parseFrame(buffer);
      if (event) yield event;
    }
  } finally {
    reader.releaseLock();
  }
}

export async function consumeResponseStream(stream) {
  let completed = false;
  for await (const event of readSseEvents(stream)) {
    if (event.type === "response.failed") throw new Error(`responses_failed_${safeErrorCode(event.response?.error?.code)}`);
    if (event.type === "response.incomplete") throw new Error(`responses_incomplete_${safeErrorCode(event.response?.incomplete_details?.reason)}`);
    if (event.type === "response.completed") completed = true;
  }
  if (!completed) throw new Error("responses_stream_ended_without_response.completed");
  return { completed: true };
}

function safeErrorCode(value) {
  const code = typeof value === "string" && value.trim() ? value : "unknown_error";
  return code.replace(/[^A-Za-z0-9_.-]/g, "_").slice(0, 80);
}

function equalSecret(left, right) {
  if (typeof left !== "string" || typeof right !== "string") return false;
  const a = Buffer.from(left, "utf8");
  const b = Buffer.from(right, "utf8");
  return a.length === b.length && timingSafeEqual(a, b);
}

function localStatePath() {
  const base = process.env.LOCALAPPDATA || join(homedir(), ".local", "share");
  return join(base, "MedicalDiagnosticsGame", "siwc-smoke.json");
}

async function loadLocalState() {
  const file = localStatePath();
  let state;
  try {
    state = JSON.parse(await readFile(file, "utf8"));
  } catch (error) {
    if (error?.code !== "ENOENT" && !(error instanceof SyntaxError)) throw error;
  }

  if (typeof state?.hostId !== "string" || !/^urn:uuid:[0-9a-f-]{36}$/i.test(state.hostId)) {
    state = { hostId: `urn:uuid:${randomUUID()}` };
    await saveLocalState(file, state);
  }
  if (state.clientId !== undefined && !/^oaiapp_[A-Za-z0-9._-]+$/.test(state.clientId)) {
    throw new Error("stored_oauth_client_id_invalid");
  }
  return { file, state };
}

async function saveLocalState(file, state) {
  await mkdir(dirname(file), { recursive: true });
  const temp = `${file}.${process.pid}.tmp`;
  await writeFile(temp, `${JSON.stringify(state, null, 2)}\n`, { encoding: "utf8", mode: 0o600 });
  await rename(temp, file);
}

function requireTrustedOpenAiUrl(value, purpose) {
  const url = new URL(value);
  if (url.protocol !== "https:" || url.hostname !== "auth.openai.com") throw new Error(`untrusted_${purpose}_endpoint`);
  return url.toString();
}

async function fetchJson(url, options, label) {
  let response;
  try {
    response = await fetch(url, { ...options, signal: AbortSignal.timeout(30_000) });
  } catch {
    throw new Error(`${label}_network_error`);
  }
  let body;
  try {
    body = await response.json();
  } catch {
    body = null;
  }
  if (!response.ok) {
    const providerCode = typeof body?.error === "string" ? body.error : body?.error?.code;
    throw new Error(`${label}_${safeErrorCode(providerCode)}_http_${response.status}`);
  }
  if (!body || typeof body !== "object") throw new Error(`${label}_invalid_json`);
  return body;
}

async function fetchOpenIdConfiguration() {
  const metadata = await fetchJson(`${AUTH_ORIGIN}/.well-known/openid-configuration`, undefined, "openid_configuration");
  if (metadata.issuer !== AUTH_ORIGIN) throw new Error("unexpected_openid_issuer");
  for (const key of ["authorization_endpoint", "token_endpoint", "jwks_uri", "revocation_endpoint"]) {
    if (typeof metadata[key] !== "string") throw new Error(`openid_${key}_missing`);
    metadata[key] = requireTrustedOpenAiUrl(metadata[key], key);
  }
  if (metadata.authorization_endpoint !== AUTHORIZE_ENDPOINT || metadata.token_endpoint !== TOKEN_ENDPOINT) {
    throw new Error("unexpected_openid_oauth_endpoints");
  }
  return metadata;
}

async function startCallbackListener(expectedState, timeoutMs = 10 * 60 * 1000) {
  let settle;
  let reject;
  let settled = false;
  let expectedHost;
  const callbackResult = new Promise((resolve, fail) => {
    settle = resolve;
    reject = fail;
  });
  const server = createServer((request, response) => {
    const remote = request.socket.remoteAddress;
    if (remote !== "127.0.0.1" && remote !== "::ffff:127.0.0.1") {
      response.writeHead(403).end("Loopback only.");
      return;
    }
    if (request.headers.host !== expectedHost) {
      response.writeHead(403).end("Unexpected callback host.");
      return;
    }
    let uri;
    try {
      uri = new URL(request.url || "/", "http://127.0.0.1");
    } catch {
      response.writeHead(400).end("Invalid callback.");
      return;
    }
    if (request.method !== "GET" || uri.pathname !== CALLBACK_PATH) {
      response.writeHead(404).end("Not found.");
      return;
    }
    if (!equalSecret(uri.searchParams.get("state"), expectedState)) {
      response.writeHead(400, { "Content-Type": "text/plain; charset=utf-8", "Cache-Control": "no-store" }).end("Invalid sign-in state. You may close this tab.");
      if (!settled) {
        settled = true;
        reject(new Error("oauth_state_mismatch"));
      }
      return;
    }
    const error = uri.searchParams.get("error");
    if (error) {
      response.writeHead(200, { "Content-Type": "text/plain; charset=utf-8", "Cache-Control": "no-store" }).end("Sign-in was not completed. You may close this tab.");
      if (!settled) {
        settled = true;
        reject(new Error(`oauth_${safeErrorCode(error)}`));
      }
      return;
    }
    const code = uri.searchParams.get("code");
    if (!code) {
      response.writeHead(400, { "Content-Type": "text/plain; charset=utf-8", "Cache-Control": "no-store" }).end("Missing authorization code. You may close this tab.");
      if (!settled) {
        settled = true;
        reject(new Error("oauth_code_missing"));
      }
      return;
    }
    response.writeHead(200, { "Content-Type": "text/plain; charset=utf-8", "Cache-Control": "no-store", "Referrer-Policy": "no-referrer" }).end("Sign-in returned to the local verifier. You may close this tab.");
    if (!settled) {
      settled = true;
      settle({ code, state: uri.searchParams.get("state"), clientId: uri.searchParams.get("client_id") });
    }
  });

  await new Promise((resolve, fail) => {
    server.once("error", fail);
    server.listen(0, "127.0.0.1", resolve);
  });
  const address = server.address();
  if (!address || typeof address === "string") throw new Error("loopback_callback_listener_failed");
  expectedHost = `127.0.0.1:${address.port}`;
  const redirectUri = `http://127.0.0.1:${address.port}${CALLBACK_PATH}`;
  const timer = setTimeout(() => {
    if (!settled) {
      settled = true;
      reject(new Error("oauth_callback_timeout"));
    }
  }, timeoutMs);
  timer.unref();
  return {
    redirectUri,
    result: callbackResult,
    close: () => new Promise((resolve) => {
      clearTimeout(timer);
      if (!server.listening) return resolve();
      server.close(() => resolve());
    }),
  };
}

function openSystemBrowser(url) {
  const [command, args] = process.platform === "win32"
    ? ["rundll32.exe", ["url.dll,FileProtocolHandler", url]]
    : process.platform === "darwin"
      ? ["open", [url]]
      : ["xdg-open", [url]];
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, { detached: true, stdio: "ignore", windowsHide: true });
    child.once("error", reject);
    child.once("spawn", () => {
      child.unref();
      resolve();
    });
  });
}

function buildAuthorizationUrl({ clientId, hostId, redirectUri, state, nonce, verifier, isNewClient }) {
  const url = new URL(AUTHORIZE_ENDPOINT);
  const values = {
    client_id: clientId,
    ...(isNewClient ? { agent_name_hint: APP_NAME } : {}),
    ext_agent_host_id: hostId,
    response_type: "code",
    redirect_uri: redirectUri,
    scope: SCOPES,
    resource: RESOURCE,
    state,
    nonce,
    code_challenge_method: "S256",
    code_challenge: pkceChallenge(verifier),
  };
  for (const [key, value] of Object.entries(values)) url.searchParams.set(key, value);
  return url;
}

async function exchangeAuthorizationCode({ clientId, code, verifier, redirectUri }) {
  return fetchJson(TOKEN_ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded", Accept: "application/json" },
    body: new URLSearchParams({
      grant_type: "authorization_code",
      client_id: clientId,
      code,
      code_verifier: verifier,
      redirect_uri: redirectUri,
      resource: RESOURCE,
    }),
  }, "oauth_token_exchange");
}

async function revokeRefreshToken(metadata, clientId, refreshToken) {
  const response = await fetch(metadata.revocation_endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded", Accept: "application/json" },
    body: new URLSearchParams({ token: refreshToken, token_type_hint: "refresh_token", client_id: clientId }),
    signal: AbortSignal.timeout(15_000),
  });
  if (!response.ok) throw new Error(`oauth_revocation_http_${response.status}`);
}

async function fetchModels(accessToken) {
  const response = await fetch(`${RESOURCE}/models`, {
    headers: { Authorization: `Bearer ${accessToken}`, Accept: "application/json" },
    signal: AbortSignal.timeout(30_000),
  }).catch(() => { throw new Error("siwc_models_network_error"); });
  let body;
  try {
    body = await response.json();
  } catch {
    body = null;
  }
  if (!response.ok) throw new Error(`siwc_models_http_${response.status}`);
  const models = Array.isArray(body?.models) ? body.models : [];
  const visible = models.filter((model) => model?.visibility === "list" && typeof model.slug === "string" && model.slug.length > 0);
  if (visible.length === 0) throw new Error("siwc_no_listable_models");
  return { visible, count: models.length };
}

async function sendSmokeResponse(accessToken, model) {
  const response = await fetch(`${RESOURCE}/responses`, {
    method: "POST",
    headers: { Authorization: `Bearer ${accessToken}`, "Content-Type": "application/json", Accept: "text/event-stream" },
    body: JSON.stringify({
      model,
      input: [{ role: "user", content: "Reply with exactly: SIWC smoke test passed." }],
      store: false,
      stream: true,
    }),
    signal: AbortSignal.timeout(90_000),
  }).catch(() => { throw new Error("siwc_responses_network_error"); });
  if (!response.ok) {
    const body = await response.text().catch(() => "");
    let code = "unknown_error";
    try {
      const json = JSON.parse(body);
      code = safeErrorCode(json?.error?.code ?? json?.error?.type ?? json?.error);
    } catch {
      code = `http_${response.status}`;
    }
    throw new Error(`siwc_responses_${code}_http_${response.status}`);
  }
  await consumeResponseStream(response.body);
}

function validateGrantedScopes(tokenResponse) {
  if (typeof tokenResponse.scope !== "string") throw new Error("oauth_granted_scopes_missing");
  const granted = new Set(tokenResponse.scope.split(/\s+/).filter(Boolean));
  for (const required of ["openid", "offline_access", "resource.invoke", "chatgpt.tokens.use.direct"]) {
    if (!granted.has(required)) throw new Error(`oauth_scope_not_granted_${required}`);
  }
}

export async function runSmoke({ openBrowser = true, callbackTimeoutMs = 10 * 60 * 1000 } = {}) {
  const metadata = await fetchOpenIdConfiguration();
  const { file: stateFile, state: localState } = await loadLocalState();
  const verifier = randomBytes(32).toString("base64url");
  const nonce = randomBytes(32).toString("base64url");
  const state = randomBytes(32).toString("base64url");
  const callback = await startCallbackListener(state, callbackTimeoutMs);
  let tokenResponse;
  let clientId = localState.clientId || "dynamic_agent_client";
  let revokeConfirmed = null;
  let outcome;

  try {
    const url = buildAuthorizationUrl({
      clientId,
      hostId: localState.hostId,
      redirectUri: callback.redirectUri,
      state,
      nonce,
      verifier,
      isNewClient: !localState.clientId,
    });
    process.stdout.write("Waiting for Sign in with ChatGPT in your browser. Approve ChatGPT plan usage if you want the inference check to run.\n");
    if (openBrowser) await openSystemBrowser(url.toString());
    else process.stdout.write(`Open this authorization URL: ${url.toString()}\n`);

    const returned = await callback.result;
    if (localState.clientId) {
      if (returned.clientId && returned.clientId !== localState.clientId) throw new Error("oauth_client_id_mismatch");
    } else {
      if (!/^oaiapp_[A-Za-z0-9._-]+$/.test(returned.clientId || "")) throw new Error("oauth_issued_client_id_missing");
      clientId = returned.clientId;
      localState.clientId = clientId;
      await saveLocalState(stateFile, localState);
    }

    tokenResponse = await exchangeAuthorizationCode({ clientId, code: returned.code, verifier, redirectUri: callback.redirectUri });
    validateGrantedScopes(tokenResponse);
    if (typeof tokenResponse.id_token !== "string" || typeof tokenResponse.access_token !== "string" || typeof tokenResponse.refresh_token !== "string") {
      throw new Error("oauth_token_response_incomplete");
    }
    if (String(tokenResponse.token_type).toLowerCase() !== "bearer") throw new Error("oauth_token_type_not_bearer");

    const jwks = await fetchJson(metadata.jwks_uri, { headers: { Accept: "application/json" } }, "openid_jwks");
    const identity = verifyIdentityToken(tokenResponse.id_token, jwks, {
      issuer: metadata.issuer,
      audience: clientId,
      nonce,
    });
    const catalog = await fetchModels(tokenResponse.access_token);
    const selectedModel = selectRequiredModel(catalog.visible);
    await sendSmokeResponse(tokenResponse.access_token, selectedModel);
    outcome = { model: selectedModel, modelCatalogEntries: catalog.count, inferenceCompleted: true };
  } finally {
    await callback.close();
    if (tokenResponse) {
      if (tokenResponse.refresh_token) {
        try {
          await revokeRefreshToken(metadata, clientId, tokenResponse.refresh_token);
          revokeConfirmed = true;
        } catch {
          revokeConfirmed = false;
        }
      }
      tokenResponse.access_token = "";
      tokenResponse.id_token = "";
      tokenResponse.refresh_token = "";
    }
  }
  return { ...outcome, revokeConfirmed };
}

async function main() {
  let result;
  try {
    result = await runSmoke({ openBrowser: !process.argv.includes("--no-browser") });
  } catch (error) {
    const code = error instanceof Error ? safeErrorCode(error.message) : "unknown_error";
    process.stderr.write(`SIWC smoke test did not complete: ${code}\n`);
    process.exitCode = 1;
    return;
  }
  process.stdout.write(`SIWC verified for this authorization: response.completed received; model=${result.model}; model_catalog_entries=${result.modelCatalogEntries}; refresh_token_revoked=${result.revokeConfirmed === true ? "yes" : result.revokeConfirmed === false ? "no" : "not_applicable"}.\n`);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) await main();
