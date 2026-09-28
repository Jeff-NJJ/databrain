/* 前端 XSS 实弹渲染测试（Node，无浏览器依赖、零第三方包）。
 *
 * 做法：把 web/index.html 里的 <script> 整块取出来，套上最小 DOM 桩执行，
 * 然后喂进**带活体载荷的数据**跑 renderAll()，检查写进 innerHTML 的全部内容：
 *   载荷若以原样出现（`<`、`"` 未被转义）→ 说明某个插值点漏了 esc()，判 FAIL；
 *   载荷只以 &lt;/&quot; 形态出现      → 转义生效，判 PASS。
 *
 * 这是对 tools/audit_esc.py 静态判定的**动态交叉验证**：
 * 静态说"所有受控字段都在 esc() 里"，这里真跑一遍看渲染结果对不对得上。
 *
 * 用法：node tools/xss_render_test.js
 * 退出码 0 = 全部转义；1 = 有载荷原样进入 DOM；2 = 装载失败。
 */
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.dirname(__dirname);
const HTML = fs.readFileSync(path.join(ROOT, 'web', 'index.html'), 'utf8');

const m = HTML.match(/<script>([\s\S]*?)<\/script>/);
if (!m) { console.error('找不到 <script> 块'); process.exit(2); }
const CODE = m[1];

/* ---------------- 最小 DOM 桩 ----------------
 * 页面自己用 `const $ = s => document.querySelector(s)`，
 * 所以这里只提供 document.*，不要往 context 里塞同名标识符
 * （否则页面脚本的 const $ 会与它冲突，直接 SyntaxError）。
 */
const sinks = [];
function makeEl(key) {
  const el = {
    __key: key,
    _html: '',
    textContent: '',
    value: '',
    disabled: false,
    style: {},
    dataset: {},
    classList: { add() {}, remove() {}, toggle() {}, contains() { return false; } },
    appendChild() {}, addEventListener() {}, setAttribute() {}, removeAttribute() {},
    getAttribute() { return null; },
    querySelector() { return null; },
    querySelectorAll() { return []; },
    setAttributeNS() {}, insertAdjacentHTML(_, v) { sinks.push({ key, html: String(v) }); },
    remove() {},
  };
  Object.defineProperty(el, 'innerHTML', {
    get() { return this._html; },
    set(v) { sinks.push({ key, html: String(v) }); this._html = String(v); },
  });
  return el;
}
const els = new Map();
function getEl(key) {
  if (!els.has(key)) els.set(key, makeEl(key));
  return els.get(key);
}
const document = {
  createElement: (t) => makeEl('<' + t + '>'),
  createElementNS: (ns, t) => makeEl('<' + t + '>'),
  createDocumentFragment: () => makeEl('#frag'),
  getElementById: (id) => getEl('#' + id),
  querySelector: (s) => getEl(String(s)),
  querySelectorAll: () => [],
  addEventListener() {},
  body: makeEl('body'),
  documentElement: makeEl('html'),
};

const _store = new Map();
const context = vm.createContext({
  document,
  console,
  fetch: async () => ({ ok: true, json: async () => ({}) }),
  /* N17 配套：页面脚本顶层现在会用 sessionStorage 存取口令，
     桩里没有它，脚本装载阶段就会 ReferenceError → 退出码 2（假失败）。 */
  sessionStorage: {
    getItem: (k) => (_store.has(k) ? _store.get(k) : null),
    setItem: (k, v) => { _store.set(k, String(v)); },
    removeItem: (k) => { _store.delete(k); },
  },
  window: { prompt: () => null },
  getComputedStyle: () => ({ getPropertyValue: () => '' }),
  requestAnimationFrame: (fn) => { try { fn(0); } catch (e) {} },
  ResizeObserver: class { observe() {} disconnect() {} },
  IntersectionObserver: class { observe() {} disconnect() {} },
  alert: () => { throw new Error('alert 被执行 = XSS 成功'); },
  Image: class { set src(v) {} },
  setTimeout, clearTimeout, setInterval, clearInterval,
  Math, JSON, Date, Object, Array, String, Number, Boolean, RegExp, Error,
  isNaN, parseFloat, parseInt, encodeURIComponent, decodeURIComponent,
});

try {
  vm.runInContext(CODE, context, { filename: 'index.html<script>' });
} catch (e) {
  console.error('页面脚本装载失败：', e.message);
  process.exit(2);
}

/* ---------------- 活体载荷 ----------------
 * 夹具不是手写的：直接读**真实发布产物** web/real.redacted.json，
 * 再把载荷塞进"语料可控字段"。这样数据结构与线上完全一致，
 * 不会因为手写夹具形状不对而让 renderAll() 提前崩掉、
 * 把"没泄露"变成假阴性。
 *
 * 同时补上 redacted 版被清掉、但**未脱敏版（DATABRAIN_FULL=1）仍在**的字段
 * （chains[].date / .text / .detail、recon_log[].detail），
 * 因为自用模式同样要抗注入。
 */
const PAYLOADS = [
  '<script>alert(1)</script>',
  '<img src=x onerror=alert(1)>',
  'x" onload="alert(1)"',
  '\'; fetch(\'//evil/\')//',
  '<svg/onload=alert(document.domain)>',
  'javascript:alert(1)',
  '<b>b</b>',
];
const N = PAYLOADS[0], S = PAYLOADS[1], T = PAYLOADS[2], D = PAYLOADS[4];

const ART = JSON.parse(fs.readFileSync(path.join(ROOT, 'web', 'real.redacted.json'), 'utf8'));

function inject(o) {
  if (Array.isArray(o)) return o.map(inject);
  if (!o || typeof o !== 'object') return o;
  const r = {};
  for (const [k, v] of Object.entries(o)) {
    if (k === 'subject' || k === 'stim' || k === 'name') r[k] = N;
    else if (k === 'text') r[k] = T;
    else if (k === 'detail' || k === 'note') r[k] = D;
    else if (k === 'bucket' || k === 'bucket_id' || k === 'theme_key') r[k] = N + '|warm|日常';
    else if (k === 'hits' && Array.isArray(v)) r[k] = [N, S];
    else if (k === 'id' && typeof v === 'string') r[k] = v.replace(/P\d+/, N);
    else if (k === 'date') r[k] = D;
    else if (k === 'persons' && v && typeof v === 'object' && !Array.isArray(v)) {
      r[k] = { [N]: Object.values(v)[0] || 1 };
    } else r[k] = inject(v);
  }
  return r;
}

const DATA = inject(ART);
// redacted 版没有这些字段，补上以覆盖未脱敏模式的渲染路径
(DATA.chains || []).forEach(c => { c.date = D; c.text = T; c.detail = D; });
(DATA.recon_log || []).forEach(x => { if (typeof x === 'object') x.detail = D; });
DATA.people_kept = [N];
DATA.source = 'real';
DATA.redacted = false;
DATA.diag = { failures: ['t=1h 桶 ' + N + ' 非法值'], warnings: ['归档 ' + S],
              hormone_extremes: { [N]: [0, 1] }, nan_count: 0 };

/* 把数据注入页面脚本所在的作用域并跑渲染。
 * 页面用 `let DATA / let SRC` 声明，词法声明进的是 context 的全词法环境，
 * 所以必须用同一 context 的脚本去赋值，不能用 context.DATA = …。 */
let crashed = null;
try {
  vm.runInContext('SRC="real"; CUR="person"; DATA=' + JSON.stringify(DATA) +
                  ';\nrenderAll();', context, { filename: 'render' });
} catch (e) {
  crashed = e.constructor.name + ': ' + e.message;
}

/* ---------------- 判定 ---------------- */
const raw = sinks.map(s => s.html).join('\n');
const leaked = PAYLOADS.filter(p => raw.includes(p));

/* 与 esc() 一致的转义规则（改一处必须同步改另一处，见 web/index.html:const esc） */
const escape = s => String(s).replace(/[&<>"']/g,
  c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

/* **防空转断言**：光看"载荷没原样出现"是不够的 ——
 * 如果渲染路径根本没把这些字段画出来（字段改名、数据没接上），
 * leaked 也是空的，测试就会假绿。所以同时要求：
 * 载荷必须**以转义形态真实出现在 DOM 里**。
 */
const escapedHits = PAYLOADS.map(p => [p, (raw.split(escape(p)).length - 1)]);
const present = escapedHits.filter(([, n]) => n > 0);
const minPresent = 3;   // 至少 3 种载荷真的被渲染出来（转义形态）
const vacuous = present.length < minPresent;

console.log('innerHTML/insertAdjacentHTML 写入次数：', sinks.length);
console.log('renderAll 异常：', crashed || '无');
console.log('DOM 写入总字节：', raw.length);
console.log('原样进入 DOM 的活体载荷：', leaked.length ? leaked : 'NONE');
console.log('转义形态出现次数（证明载荷真的走到了 DOM）：',
            escapedHits.map(([p, n]) => n).join(' '));
console.log('以转义形态出现的载荷种类数：', present.length, '（要求 ≥' + minPresent + '）');

const ok = !crashed && leaked.length === 0 && !vacuous;
console.log('结论：', ok ? 'PASS —— 全部载荷以转义形态进入 DOM'
     : crashed ? 'FAIL —— 渲染崩溃，判定无意义'
     : vacuous ? 'FAIL —— 载荷没走到 DOM（测试空转，不能算通过）'
     : 'FAIL —— 有载荷原样进入 DOM');
process.exit(ok ? 0 : 1);

