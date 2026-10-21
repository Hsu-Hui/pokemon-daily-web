const test = require('node:test');
const assert = require('node:assert');
const { load } = require('./load');

const DAY = 864e5;
const now = new Date('2026-10-21T01:00:00+08:00');
const iso = (ms) => new Date(now.getTime() + ms).toISOString();

test('mergeTimed_ keeps firstSeen and archives ended items for keepArchiveDays', () => {
  const { gas } = load();
  const existing = [
    { id: 'still', firstSeen: 'old', end: iso(DAY) },
    { id: 'ended10', firstSeen: 'old', end: iso(-10 * DAY) },
    { id: 'ended40', firstSeen: 'old', end: iso(-40 * DAY) },
    { id: 'noEnd', firstSeen: 'old', end: null },
  ];
  const out = gas.mergeTimed_(existing, [{ id: 'still', end: iso(DAY) }, { id: 'new', end: iso(DAY) }], now);
  assert.deepStrictEqual(out.map((r) => r.id), ['still', 'new', 'ended10']);
  assert.strictEqual(out[0].firstSeen, 'old');
  assert.strictEqual(out[1].firstSeen, now.toISOString());
});

test('mergeFresh_ adds only unseen items and drops expired ones', () => {
  const { gas } = load();
  const seen = { gone: iso(-8 * DAY) };
  const existing = [{ id: 'fresh', firstSeen: iso(-2 * DAY) }, { id: 'old', firstSeen: iso(-8 * DAY) }];
  const out = gas.mergeFresh_(existing, [{ id: 'fresh' }, { id: 'gone' }, { id: 'brand' }], seen, 7, now);
  assert.deepStrictEqual(out.map((r) => r.id), ['fresh', 'brand']);
  assert.strictEqual(seen.brand, now.toISOString());
});

test('doPost answers JSON for malformed body and wrong secret', () => {
  const { gas, sheets } = load();
  const reply = (e) => JSON.parse(gas.doPost(e).text);
  assert.strictEqual(reply({ postData: { contents: 'not json' } }).ok, false);
  assert.strictEqual(reply({}).ok, false);
  assert.deepStrictEqual(reply({ postData: { contents: JSON.stringify({ secret: 'x', data: {} }) } }),
    { ok: false, error: 'bad secret' });
  assert.deepStrictEqual(sheets, {});
});

test('doPost stores data with the right secret', () => {
  const { gas, sheets } = load();
  const data = { generatedAt: now.toISOString(), events: [], taskGroups: [], products: [{ id: 'p', media: '' }], news: [], errors: [] };
  const res = JSON.parse(gas.doPost({ postData: { contents: JSON.stringify({ secret: 'secret', data }) } }).text);
  assert.strictEqual(res.ok, true);
  assert.strictEqual(sheets.products[0].id, 'p');
});

function post(gas, errors) {
  const data = { generatedAt: now.toISOString(), events: [], taskGroups: [], products: [], news: [], errors };
  return JSON.parse(gas.doPost({ postData: { contents: JSON.stringify({ secret: 'secret', data }) } }).text);
}

test('doPost sends one Discord message when sources failed', () => {
  const { gas, fetched } = load({ scriptProps: { DISCORD_WEBHOOK_URL: 'https://discord/hook', VIEW_URL: 'https://view' } });
  assert.strictEqual(post(gas, ['PChome（請求次數過多被限制）', '寶可夢官網（HTTP 503）']).ok, true);
  assert.strictEqual(fetched.length, 1);
  assert.match(fetched[0].body.content, /⚠️ 每日抓取有來源失敗：PChome（請求次數過多被限制）、寶可夢官網（HTTP 503）/);
  assert.match(fetched[0].body.content, /<https:\/\/view>/);
});

test('doPost sends nothing when no source failed or no webhook', () => {
  const withHook = load({ scriptProps: { DISCORD_WEBHOOK_URL: 'https://discord/hook' } });
  post(withHook.gas, []);
  assert.strictEqual(withHook.fetched.length, 0);
  const noHook = load();
  post(noHook.gas, ['PChome（連不上）']);
  assert.strictEqual(noHook.fetched.length, 0);
});

test('doPost still answers ok when the webhook is down', () => {
  const { gas } = load({ scriptProps: { DISCORD_WEBHOOK_URL: 'https://discord/hook' }, fetchThrows: true });
  assert.strictEqual(post(gas, ['PChome（連不上）']).ok, true);
});

test('getData no longer returns errors', () => {
  const { gas, sheets } = load();
  sheets.meta = [{ key: 'updatedAt', value: now.toISOString() }, { key: 'errors', value: 'PChome（連不上）' }];
  const out = gas.getData();
  assert.ok(!('errors' in out));
  assert.strictEqual(out.updatedAt, now.toISOString());
});

test('setFlag only accepts taskDone and gaveUp', () => {
  const { gas } = load();
  assert.throws(() => gas.setFlag('done', 'e1', true), /bad kind/);
  assert.deepStrictEqual(Object.keys(gas.setFlag('gaveUp', 'g1', true)).sort(), ['gaveUp', 'taskDone']);
});
