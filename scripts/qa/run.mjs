// Screen QA driver: drives a running headless Chrome (CDP) through checklist JSON files. Started by scripts/qa.sh.
//   node scripts/qa/run.mjs [--check] <checklist.json>...
//   env: QA_PORT (Chrome remote debugging, 9339), QA_BASE (UI, http://localhost:5173), QA_OUT (screenshots, logs/qa)
// Steps act, then wait, then read: {viewport:[w,h]} {nav:"/#live"} {click:"button text"} {clickSel:css} {clickAt:[x,y]}
//   {select:[css,value]} {type:[css,value]} {key} {wait:ms} {eval:js, label, expect?|match?} {layout:label} {shot:file}.
// A step fails on a missing or disabled button, a console error, an uncaught exception, an HTTP >= 400 response,
// a wrong expect (exact JSON) or match (regex on the string or its JSON), or a layout probe that finds overflow.
// --check only validates the files (no browser): unknown keys and steps that neither act nor read are errors.
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const ACTS = ["viewport", "nav", "click", "clickSel", "clickAt", "select", "type", "key", "wait", "eval", "layout", "shot"];
const KEYS = new Set([...ACTS, "label", "expect", "match"]);
const args = process.argv.slice(2);
const checkOnly = args[0] === "--check";
const files = checkOnly ? args.slice(1) : args;

function problemsIn(steps) {
  if (!Array.isArray(steps)) return ["not a list of steps"];
  return steps.flatMap((s, i) => {
    const out = Object.keys(s).filter((k) => !KEYS.has(k)).map((k) => `step ${i + 1}: unknown key "${k}"`);
    if (!ACTS.some((k) => k in s)) out.push(`step ${i + 1}: does nothing (no action and no read)`);
    if (("expect" in s || "match" in s) && !("eval" in s || "layout" in s)) out.push(`step ${i + 1}: expect/match without eval`);
    return out;
  });
}

const lists = files.map((f) => ({ file: f, steps: JSON.parse(readFileSync(f, "utf8")) }));
const bad = lists.flatMap(({ file, steps }) => problemsIn(steps).map((p) => `${file}: ${p}`));
if (bad.length || checkOnly) {
  for (const p of bad) console.log(p);
  if (!bad.length) console.log(`== ${files.length} checklist(s) OK`);
  process.exit(bad.length ? 1 : 0);
}

const PORT = process.env.QA_PORT ?? "9339";
const BASE = process.env.QA_BASE ?? "http://localhost:5173";
const OUT = process.env.QA_OUT ?? "logs/qa";
mkdirSync(OUT, { recursive: true });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const targets = await (await fetch(`http://127.0.0.1:${PORT}/json`)).json();
const ws = new WebSocket(targets.find((t) => t.type === "page").webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener("open", r));
let id = 0;
const pending = new Map();
const problems = [];
const send = (method, params = {}) => new Promise((r) => { const i = ++id; pending.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
ws.addEventListener("message", (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
  if (m.method === "Page.javascriptDialogOpening") send("Page.handleJavaScriptDialog", { accept: true });
  if (m.method === "Runtime.exceptionThrown") problems.push("EXCEPTION " + (m.params.exceptionDetails.exception?.description ?? m.params.exceptionDetails.text).split("\n")[0]);
  if (m.method === "Runtime.consoleAPICalled" && ["error", "assert"].includes(m.params.type))
    problems.push("CONSOLE " + m.params.args.map((a) => a.value ?? a.description).join(" ").split("\n")[0]);
  if (m.method === "Network.responseReceived" && m.params.response.status >= 400 && !/favicon/.test(m.params.response.url))
    problems.push(`HTTP ${m.params.response.status} ${m.params.response.url.replace(/^https?:\/\/[^/]+/, "")}`);
});
await send("Page.enable"); await send("Runtime.enable"); await send("Network.enable");

const ev = async (expr) => {
  const r = await send("Runtime.evaluate", { expression: expr, returnByValue: true, awaitPromise: true });
  return r.result?.exceptionDetails ? "ERR " + (r.result.exceptionDetails.exception?.description ?? "").split("\n")[0] : r.result?.result?.value;
};
const clickExpr = (t) => `(() => { const el = [...document.querySelectorAll("button, a")].filter(b => b.offsetParent !== null).find(b => b.innerText.trim().includes(${JSON.stringify(t)}));
  if (!el) return "NOT FOUND " + ${JSON.stringify(t)}; if (el.disabled) return "DISABLED " + el.innerText.trim(); el.click(); return "clicked " + el.innerText.trim().split("\\n")[0]; })()`;
const setExpr = (proto, [sel, v], evt) => `(() => { const el = document.querySelector(${JSON.stringify(sel)}); if (!el) return "NOT FOUND " + ${JSON.stringify(sel)};
  Object.getOwnPropertyDescriptor(${proto}.prototype, "value").set.call(el, ${JSON.stringify(v)}); el.dispatchEvent(new Event("${evt}", { bubbles: true })); return "set " + el.value; })()`;
// Overflow probe: the page must not scroll sideways and no panel may cut its content off.
const LAYOUT = `(() => { const de = document.documentElement; const over = [];
  for (const el of document.querySelectorAll("aside, .runbar, .tabs, .editor-main, .play-sidebar, .card, .switchpanel, .metrics"))
    if (el.scrollWidth > el.clientWidth + 2 && getComputedStyle(el).overflowX !== "auto") over.push(el.className || el.tagName);
  return { viewport: innerWidth + "x" + innerHeight, pageOverflowX: de.scrollWidth > innerWidth + 1, clipped: [...new Set(over)].slice(0, 6) }; })()`;

async function act(s) {
  if (s.viewport) { await send("Emulation.setDeviceMetricsOverride", { width: s.viewport[0], height: s.viewport[1], deviceScaleFactor: 1, mobile: false }); return "viewport " + s.viewport.join("x"); }
  if (s.nav) { await send("Page.navigate", { url: s.nav.startsWith("/") ? BASE + s.nav : s.nav }); return "nav " + s.nav; }
  if (s.click) return ev(clickExpr(s.click));
  if (s.select) return ev(setExpr("HTMLSelectElement", s.select, "change"));
  if (s.type) return ev(setExpr("HTMLInputElement", s.type, "input"));
  if (s.clickSel || s.clickAt) {
    let xy = s.clickAt;
    if (s.clickSel) xy = await ev(`(() => { const el = document.querySelector(${JSON.stringify(s.clickSel)}); if (!el) return null; const r = el.getBoundingClientRect(); return [r.x + r.width / 2, r.y + r.height / 2]; })()`);
    if (!xy) return "NOT FOUND " + s.clickSel;
    for (const type of ["mouseMoved", "mousePressed", "mouseReleased"]) await send("Input.dispatchMouseEvent", { type, x: xy[0], y: xy[1], button: "left", clickCount: 1 });
    return "mouse " + xy.map(Math.round) + " " + (s.clickSel ?? "");
  }
  if (s.key) { for (const type of ["keyDown", "keyUp"]) await send("Input.dispatchKeyEvent", { type, key: s.key, code: s.key, windowsVirtualKeyCode: s.key === "Escape" ? 27 : 0 }); return "key " + s.key; }
  return "";
}

function judge(s, note, got, errs) {
  let ok = !/^(NOT FOUND|DISABLED)/.test(String(note)) && !String(got ?? "").startsWith("ERR ") && errs.length === 0;
  if ("expect" in s) ok &&= JSON.stringify(got) === JSON.stringify(s.expect);
  if ("match" in s) ok &&= new RegExp(s.match).test(typeof got === "string" ? got : JSON.stringify(got));
  if (s.layout) ok &&= !got.pageOverflowX && got.clipped.length === 0;
  return ok;
}

let total = 0, fails = 0;
for (const { file, steps } of lists) {
  console.log(`-- ${file}`);
  for (const s of steps) {
    const before = problems.length;
    const note = await act(s);
    if (s.wait) await sleep(s.wait);
    let got;
    if (s.eval) got = await ev(s.eval);
    if (s.layout) got = await ev(LAYOUT);
    let shot = "";
    if (s.shot) { const c = await send("Page.captureScreenshot", { format: "png" }); writeFileSync(join(OUT, s.shot), Buffer.from(c.result.data, "base64")); shot = "shot " + join(OUT, s.shot); }
    const errs = problems.slice(before);
    const ok = judge(s, note, got, errs);
    total++; if (!ok) fails++;
    if (!s.label && !s.layout && ok) continue; // plain actions print only when they fail
    const want = "expect" in s ? " (want " + JSON.stringify(s.expect) + ")" : "match" in s ? " (want /" + s.match + "/)" : "";
    console.log(`${ok ? "PASS" : "FAIL"} ${s.label ?? s.layout ?? ""} ${note || shot}${got !== undefined ? " → " + JSON.stringify(got) : ""}${ok ? "" : want}${errs.length ? " !! " + errs.join(" | ") : ""}`);
  }
}
console.log(`== ${total - fails}/${total} PASS`);
ws.close();
process.exit(fails ? 1 : 0);
