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

test('saveTasks writes all changes at once', () => {
  const { gas } = load();
  gas.saveTasks({ 'g1#a': true, 'g1#b': true });
  const state = gas.saveTasks({ 'g1#a': false, 'g2#c': true });
  assert.deepStrictEqual(Object.keys(state.taskDone).sort(), ['g1#b', 'g2#c']);
  assert.deepStrictEqual(Object.keys(gas.loadState_().taskDone).sort(), ['g1#b', 'g2#c']);
});

test('saveTasks rejects bad keys or values without writing', () => {
  const { gas } = load();
  gas.saveTasks({ 'g1#a': true });
  assert.throws(() => gas.saveTasks({ 'g1#t1': 'yes' }), /bad change/);
  assert.throws(() => gas.saveTasks({ 'no-hash': true, 'g1#b': true }), /bad change/);
  assert.deepStrictEqual(Object.keys(gas.loadState_().taskDone), ['g1#a']);
});

const newsItem = (id, title) => ({ kind: 'news', id, title, url: 'https://n/' + id, source: '寶可夢官網', date: '2026-10-21T01:00:00Z' });

test('toggleFavorite adds a snapshot and removes it again', () => {
  const { gas, userStores } = load();
  let favs = gas.toggleFavorite(newsItem('n1', '寶可夢嘉年華'), true);
  assert.deepStrictEqual(Array.from(favs, (f) => f.id), ['n1']);
  assert.ok(favs[0].starredAt);
  assert.strictEqual(Object.keys(userStores.me).filter((k) => k.startsWith('fav:news:')).length, 1);
  favs = gas.toggleFavorite(newsItem('n1', '寶可夢嘉年華'), false);
  assert.strictEqual(favs.length, 0);
});

test('toggleFavorite rejects bad items', () => {
  const { gas } = load();
  assert.throws(() => gas.toggleFavorite({ kind: 'event', id: 'x', title: 't', url: 'https://x' }, true), /bad favorite/);
  assert.throws(() => gas.toggleFavorite({ kind: 'news', id: 'x', title: 't', url: 'javascript:alert(1)' }, true), /bad favorite/);
  assert.throws(() => gas.toggleFavorite({ kind: 'news', id: '', title: 't', url: 'https://x' }, true), /bad favorite/);
});

test('long fields are trimmed and the 500 cap is enforced', () => {
  const { gas } = load();
  const [f] = gas.toggleFavorite(Object.assign(newsItem('long', 'x'.repeat(1000))), true);
  assert.strictEqual(f.title.length, 300);
  for (let i = 0; i < 499; i++) gas.toggleFavorite(newsItem('n' + i, 't'), true);
  assert.throws(() => gas.toggleFavorite(newsItem('one-more', 't'), true), /我的最愛已滿/);
  assert.strictEqual(gas.toggleFavorite(newsItem('n1', 't'), true).length, 500, 're-starring an existing one is fine');
});

test('favorites are per user and survive the news row being deleted', () => {
  const stores = {};
  const a = load({ userStores: stores });
  a.gas.toggleFavorite(newsItem('n1', '寶可夢嘉年華'), true);
  a.sheets.news = [];
  assert.deepStrictEqual(Array.from(a.gas.getData().favorites, (f) => f.title), ['寶可夢嘉年華']);
  a.gas.user = 'someone-else';
  assert.strictEqual(a.gas.getData().favorites.length, 0);
});

test('remindTasks: one early reminder within 2 days, then hourly in the last 4 hours', () => {
  const HOUR = 36e5;
  const { gas, sheets, fetched } = load({ scriptProps: { DISCORD_WEBHOOK_URL: 'https://hook' } });
  const group = (id, ms) => ({ id, name: id, end: new Date(Date.now() + ms).toISOString(), tasks: [{ id: 't', text: '捕捉 1 隻寶可夢' }] });
  sheets.tasks = [group('soon', 3 * HOUR), group('twoDays', 40 * HOUR), group('far', 60 * HOUR)];
  gas.remindTasks();
  gas.remindTasks();
  const names = fetched.map((f) => f.body.content.split('\n')[0]);
  assert.deepStrictEqual(names.filter((n) => n.includes('twoDays')).length, 1);
  assert.deepStrictEqual(names.filter((n) => n.includes('soon')).length, 2);
  assert.ok(!names.some((n) => n.includes('far')));
});

test('daily field research rewards never send Discord task reminders', () => {
  const { gas, sheets, fetched } = load({ scriptProps: { DISCORD_WEBHOOK_URL: 'https://hook' } });
  const end = new Date(Date.now() + 3 * 36e5).toISOString();
  sheets.tasks = [
    { id: 'field-202610', name: '10 月田野調查', end, tasks: [{ id: 'field', text: '捕捉 5 隻', reward: '遇見皮卡丘' }] },
    { id: 'ld-timed', name: '限時調查', end, tasks: [{ id: 'timed', text: '捕捉 10 隻' }] },
  ];
  gas.remindTasks();
  assert.strictEqual(fetched.length, 1);
  assert.match(fetched[0].body.content, /限時調查/);
  assert.ok(!fetched[0].body.content.includes('10 月田野調查'));
});

test('manual task groups: add, list in getData, remind, delete and prune', () => {
  const HOUR = 36e5;
  const { gas, sheets, fetched, userStores } = load({ scriptProps: { DISCORD_WEBHOOK_URL: 'https://hook' } });
  sheets.tasks = [];
  const end = new Date(Date.now() + 3 * HOUR).toISOString();
  const list = gas.addManualTask({ name: '限時調查：30 年的軌跡', end, tasks: [{ text: '捕捉 30 隻寶可夢', reward: '精靈球 ×10' }, { text: '  ' }] });
  assert.strictEqual(list.length, 1);
  const g = list[0];
  assert.match(g.id, /^my-[0-9a-z]+$/);
  assert.strictEqual(g.manual, true);
  assert.deepStrictEqual(JSON.parse(JSON.stringify(g.tasks)), [{ id: 't1', text: '捕捉 30 隻寶可夢', reward: '精靈球 ×10' }]);
  assert.strictEqual(gas.getData().tasks.length, 1);
  gas.remindTasks();
  assert.match(fetched[0].body.content, /30 年的軌跡/);
  // 別人看不到
  gas.user = 'other';
  assert.strictEqual(gas.getData().tasks.length, 0);
  gas.user = 'me';
  assert.strictEqual(gas.deleteManualTask(g.id).length, 0);
  // 結束超過 keepArchiveDays 天的組在 getData 時刪掉
  userStores.me['manual:my-old'] = JSON.stringify({ id: 'my-old', name: 'old', end: new Date(Date.now() - 40 * 864e5).toISOString(), tasks: [] });
  assert.strictEqual(gas.getData().tasks.length, 0);
  assert.ok(!('manual:my-old' in userStores.me));
});

test('addManualTask rejects bad input', () => {
  const { gas } = load();
  const end = new Date(Date.now() + 36e5).toISOString();
  assert.throws(() => gas.addManualTask({ name: '', end, tasks: [{ text: 'a' }] }));
  assert.throws(() => gas.addManualTask({ name: 'x', end: new Date(Date.now() - 1000).toISOString(), tasks: [{ text: 'a' }] }));
  assert.throws(() => gas.addManualTask({ name: 'x', end, tasks: [] }));
  assert.throws(() => gas.addManualTask({ name: 'x', end, tasks: Array.from({ length: 31 }, () => ({ text: 'a' })) }));
  assert.throws(() => gas.deleteManualTask('manual:../x'));
  // 中文一個字 3 個位元組：30 項 × 160 字超過 9 KB
  const long = '捕'.repeat(80);
  assert.throws(() => gas.addManualTask({ name: 'x', end, tasks: Array.from({ length: 30 }, () => ({ text: long, reward: long })) }), /太長/);
});

test('updateManualTask keeps stable ids and atomically cleans removed progress', () => {
  const { gas, userStores } = load();
  const end = new Date(Date.now() + 36e5).toISOString();
  const original = gas.addManualTask({
    name: '打錯的名稱', end,
    tasks: [
      { text: '捕捉 10 隻寶可夢', reward: '精靈球 ×5' },
      { text: '轉動 3 個補給站', reward: '' },
    ],
  })[0];
  gas.saveTasks({ [`${original.id}#t1`]: true, [`${original.id}#t2`]: true });

  const nextEnd = new Date(Date.now() + 2 * 36e5).toISOString();
  const updated = gas.updateManualTask(original.id, {
    name: '修正後名稱', end: nextEnd,
    tasks: [
      { id: 't1', text: '捕捉 10 隻寶可夢', reward: '精靈球 ×10' },
      { text: '孵化 1 顆蛋', reward: '星星沙 ×500' },
    ],
  }).find((g) => g.id === original.id);

  assert.strictEqual(updated.id, original.id);
  assert.strictEqual(updated.start, original.start);
  assert.strictEqual(updated.name, '修正後名稱');
  assert.strictEqual(updated.end, nextEnd);
  assert.deepStrictEqual(JSON.parse(JSON.stringify(updated.tasks)), [
    { id: 't1', text: '捕捉 10 隻寶可夢', reward: '精靈球 ×10' },
    { id: 't3', text: '孵化 1 顆蛋', reward: '星星沙 ×500' },
  ]);
  const state = JSON.parse(userStores.me.state);
  assert.strictEqual(state.taskDone[`${original.id}#t1`], true);
  assert.ok(!state.taskDone[`${original.id}#t2`]);
  assert.ok(!state.taskDone[`${original.id}#t3`]);
});

test('updateManualTask rejects invalid edits without changing group or progress', () => {
  const { gas, userStores } = load();
  const end = new Date(Date.now() + 36e5).toISOString();
  const group = gas.addManualTask({ name: '原本', end, tasks: [{ text: '任務一' }, { text: '任務二' }] })[0];
  gas.saveTasks({ [`${group.id}#t1`]: true, [`${group.id}#t2`]: true });
  const before = JSON.stringify(userStores.me);

  assert.throws(() => gas.updateManualTask('manual:../x', { name: 'x', end, tasks: [{ id: 't1', text: 'x' }] }), /bad id/);
  assert.throws(() => gas.updateManualTask(group.id, { name: '', end, tasks: [{ id: 't1', text: 'x' }] }));
  assert.throws(() => gas.updateManualTask(group.id, { name: 'x', end, tasks: [{ id: 'missing', text: 'x' }] }), /bad task id/);
  assert.throws(() => gas.updateManualTask(group.id, { name: 'x', end, tasks: [{ id: 't1', text: 'x' }, { id: 't1', text: 'y' }] }), /bad task id/);
  assert.throws(() => gas.updateManualTask(group.id, { name: 'x', end, tasks: Array.from({ length: 31 }, () => ({ text: 'x' })) }));
  const long = '捕'.repeat(80);
  assert.throws(() => gas.updateManualTask(group.id, {
    name: 'x', end, tasks: Array.from({ length: 30 }, (_, i) => ({ id: i < 2 ? `t${i + 1}` : undefined, text: long, reward: long })),
  }), /太長/);

  assert.strictEqual(JSON.stringify(userStores.me), before);
});
