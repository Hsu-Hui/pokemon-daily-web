const test = require('node:test');
const assert = require('node:assert');
const { loadApp, sampleData } = require('./app');

const TABS = ['overview', 'go', 'tasks', 'shop', 'tw', 'fav', 'archive'];

test('every tab renders without undefined values', () => {
  const { app, main } = loadApp(sampleData());
  for (const tab of TABS) {
    app.ui.tab = tab;
    app.render();
    assert.ok(main.innerHTML.length > 50, tab);
    assert.ok(!/undefined|NaN/.test(main.innerHTML), `${tab}: ${main.innerHTML.match(/.{0,40}(undefined|NaN).{0,40}/)}`);
  }
});

test('settings text comes from board.json', () => {
  const data = sampleData();
  data.config = Object.assign({}, data.config, { keepProductDays: 10, remindHours: 6 });
  const { app, main } = loadApp(data);
  app.ui.tab = 'shop'; app.render();
  assert.match(main.innerHTML, /最近 10 天新上架/);
  app.ui.tab = 'tasks'; app.render();
  assert.match(main.innerHTML, /結束前 6 小時/);
});

test('products tab shows only PChome; old announcement rows move to 活動&新聞', () => {
  const data = sampleData();
  data.products.push({ id: 'p3', source: 'PChome', name: '沒有價格的玩偶', url: 'u', price: '', image: '', firstSeen: new Date().toISOString(), media: '' });
  const { app, main } = loadApp(data);
  app.ui.tab = 'shop'; app.render();
  assert.match(main.innerHTML, /\$1,280/);
  assert.match(main.innerHTML, /沒有價格的玩偶[\s\S]*看消息/);
  assert.ok(!main.innerHTML.includes('寶可夢 伊布 馬克杯'), 'official announcement is not a product');
  assert.ok(!main.innerHTML.includes('data-src'), 'no source pills on 新商品');
  app.ui.tab = 'tw'; app.render();
  assert.match(main.innerHTML, /寶可夢 伊布 馬克杯/);
});

test('matchesQuery follows the product search examples', () => {
  const { app } = loadApp(sampleData());
  const cases = [
    ['Pokémon 皮卡丘 絨毛玩偶', '皮卡丘', true],
    ['POKEMON 卡牌 禮盒', 'pokemon', true],
    ['寶可夢 伊布 馬克杯', '皮卡丘', false],
    ['寶可夢 伊布 馬克杯', '  伊布 ', true],
    ['寶可夢 伊布 馬克杯', '', true],
  ];
  for (const [name, query, want] of cases) assert.strictEqual(app.matchesQuery(name, query), want, `${name} / ${query}`);
});

test('search combines with source filter and resets to page 1', () => {
  const data = sampleData();
  for (let i = 0; i < 30; i++) {
    data.products.push({ id: 'x' + i, source: 'PChome', name: 'Pikachu 貼紙 ' + i, url: 'u', price: '$100', image: '', firstSeen: new Date().toISOString(), media: '' });
  }
  const { app, main, listeners, searchBox } = loadApp(data);
  app.ui.tab = 'shop';
  app.ui.srcs = ['PChome'];
  app.ui.page.shop = 2;
  const input = { value: 'pikachu', selectionStart: 7, matches: (sel) => sel === 'input[data-shopquery]' };
  listeners.input({ target: input });
  assert.strictEqual(app.ui.page.shop, 1);
  assert.deepStrictEqual([searchBox.focused, searchBox.caret], [true, 7]);
  assert.match(main.innerHTML, /共 30 筆/);
  assert.ok(!main.innerHTML.includes('伊布'));
  app.ui.shopQuery = '不存在的商品';
  app.render();
  assert.match(main.innerHTML, /找不到符合「不存在的商品」的商品/);
});

test('overview does not show source failures', () => {
  const { app, main } = loadApp(sampleData({ errors: 'PChome（連不上）' }));
  app.ui.tab = 'overview'; app.render();
  assert.ok(!main.innerHTML.includes('抓取失敗'));
});

test('GO events have no done checkbox and ignore old done flags', () => {
  const data = sampleData();
  data.state.done = { e1: true };
  const { app, main } = loadApp(data);
  app.ui.tab = 'go'; app.render();
  assert.ok(!main.innerHTML.includes('data-flag="done"'));
  assert.ok(!main.innerHTML.includes('type="checkbox"'));
  assert.ok(!main.innerHTML.includes('<th>完成</th>'));
  assert.match(main.innerHTML, /聚焦時刻：皮卡丘/);
  app.ui.tab = 'overview'; app.render();
  assert.match(main.innerHTML, /進行中活動<\/span><b>1</);
});

test('ended events go to archive without restore', () => {
  const data = sampleData();
  const ended = new Date(Date.now() - 36e5).toISOString();
  data.events.push({ id: 'old', name: '已結束的活動', type: '活動', category: '其他', url: 'u', start: ended, end: ended, firstSeen: ended });
  const { app, main } = loadApp(data);
  app.ui.tab = 'go'; app.render();
  assert.ok(!main.innerHTML.includes('已結束的活動'));
  app.ui.tab = 'archive'; app.render();
  assert.match(main.innerHTML, /已結束的活動/);
  assert.ok(!main.innerHTML.includes('>復原</button>'));
});

test('events without end are hidden and no tab shows Infinity', () => {
  const data = sampleData();
  data.events.push({ id: 'noend', name: '極巨星期一：極巨化狃拉', type: '極巨星期一', category: '極巨化/超極巨化', url: 'u', start: null, end: null, firstSeen: null });
  const { app, main } = loadApp(data);
  for (const tab of ['overview', 'go', 'tasks', 'shop', 'tw', 'archive']) {
    app.ui.tab = tab; app.render();
    assert.ok(!main.innerHTML.includes('Infinity'), tab);
    assert.ok(!main.innerHTML.includes('極巨化狃拉'), tab);
  }
});

test('duplicate products (same name and price) are shown once', () => {
  const data = sampleData();
  const dup = (id, name, price) => ({ id, source: 'PChome', name, url: 'u', price, image: '', firstSeen: new Date().toISOString(), media: '' });
  data.products = [dup('a', '皮卡丘 卡比獸 造型存錢筒', '$590'), dup('b', '皮卡丘  卡比獸 造型存錢筒', '$590'), dup('c', '皮卡丘 卡比獸 造型存錢筒', '$650')];
  const { app, main } = loadApp(data);
  app.ui.tab = 'shop'; app.render();
  assert.strictEqual((main.innerHTML.match(/造型存錢筒/g) || []).length, 2);
});

test('event name column is not limited by the old checkbox width rule', () => {
  const css = require('fs').readFileSync(require('path').join(__dirname, '..', '..', 'gas', 'Styles.html'), 'utf8');
  assert.ok(!/td:first-child\s*\{[^}]*width/.test(css));
  assert.match(css, /\.col-name\s*\{[^}]*min-width:\s*240px/);
});

function researchData() {
  const data = sampleData();
  const end = new Date(Date.now() + 30 * 36e5).toISOString();
  const tasks = (n) => Array.from({ length: n }, (_, i) => ({ id: 't' + (i + 1), text: '任務 ' + (i + 1), reward: '' }));
  data.tasks = [
    { id: 'ld-adidas', name: '限時調查：adidas', url: 'u', start: null, end, firstSeen: null, tasks: tasks(25) },
    { id: 'field-202610', name: '10 月田野調查', url: 'u', start: null, end, firstSeen: null, tasks: tasks(10) },
  ];
  return data;
}
const doneOf = (data, groupId, app) => data.tasks.find((g) => g.id === groupId).tasks
  .map((t, i) => i + 1).filter((n) => (`${groupId}#t${n}` in app.ui.draft ? app.ui.draft[`${groupId}#t${n}`] : !!data.state.taskDone[`${groupId}#t${n}`]));

test('timed research checks in order (example table)', () => {
  const data = researchData();
  const { app } = loadApp(data);
  app.toggleTask('ld-adidas', 4, true);
  assert.deepStrictEqual(doneOf(data, 'ld-adidas', app), [1, 2, 3, 4, 5]);
  app.toggleTask('ld-adidas', 19, true);
  assert.deepStrictEqual(doneOf(data, 'ld-adidas', app), Array.from({ length: 20 }, (_, i) => i + 1));
  app.toggleTask('ld-adidas', 4, false);
  assert.deepStrictEqual(doneOf(data, 'ld-adidas', app), [1, 2, 3, 4]);
});

test('daily field research is a reward reference without task controls', () => {
  const data = researchData();
  data.tasks[1].tasks[0].reward = '遇見 皮卡丘';
  const { app, main } = loadApp(data);
  app.ui.tab = 'tasks'; app.render();
  assert.match(main.innerHTML, /日常田野調查獎勵/);
  assert.match(main.innerHTML, /任務 1[\s\S]*遇見 皮卡丘/);
  assert.ok(!main.innerHTML.includes('data-task="field-202610"'));
  assert.strictEqual((main.innerHTML.match(/type="checkbox"/g) || []).length, 25);
  app.ui.tab = 'overview'; app.render();
  assert.match(main.innerHTML, /任務進度<\/span><b[^>]*>0\/25<\/b>/);
  data.tasks[1].end = new Date(Date.now() - 36e5).toISOString();
  app.ui.tab = 'archive'; app.render();
  assert.ok(!main.innerHTML.includes('10 月田野調查'));
});

test('every trackable group checks in order, including a manual October group', () => {
  const data = researchData();
  const end = new Date(Date.now() + 30 * 36e5).toISOString();
  data.tasks.push({
    id: 'my-october', name: '10 月田野調查任務', url: '', manual: true,
    start: null, end, tasks: Array.from({ length: 8 }, (_, i) => ({ id: 'm' + (i + 1), text: '步驟 ' + (i + 1), reward: '' })),
  });
  const { app } = loadApp(data);
  app.toggleTask('my-october', 4, true);
  const checked = Array.from({ length: 8 }, (_, i) => i + 1).filter((n) => !!app.ui.draft[`my-october#m${n}`]);
  assert.deepStrictEqual(checked, [1, 2, 3, 4, 5]);
});

test('ticks stay as a draft until saved, then saved in one call', () => {
  const data = researchData();
  const { app, main, listeners, calls } = loadApp(data);
  app.ui.tab = 'tasks';
  app.toggleTask('ld-adidas', 2, true);
  assert.strictEqual(calls.saveTasks.length, 0);
  assert.match(main.innerHTML, /有 3 項變更未儲存/);
  app.ui.tab = 'shop'; app.render();
  assert.strictEqual(app.draftCount(), 3, 'tab switch keeps the draft');
  const ev = { preventDefault() { this.prevented = true; } };
  listeners['window:beforeunload'](ev);
  assert.ok(ev.prevented, 'leaving with unsaved changes asks first');
  assert.ok(!main.innerHTML.includes('data-save'), 'save control only on 任務待辦');
  app.ui.tab = 'tasks'; app.render();
  assert.match(main.innerHTML, /有 3 項變更未儲存/);
  listeners.click({ target: { closest: () => ({ disabled: false, dataset: { save: '' } }) } });
  assert.strictEqual(calls.saveTasks.length, 1);
  assert.deepStrictEqual(Object.keys(calls.saveTasks[0]).sort(), ['ld-adidas#t1', 'ld-adidas#t2', 'ld-adidas#t3']);
  assert.strictEqual(app.draftCount(), 0);
  assert.match(main.innerHTML, /已儲存/);
});

test('failed save keeps the draft', () => {
  const data = researchData();
  const { app, listeners, elements } = loadApp(data, { saveFails: true });
  app.toggleTask('ld-adidas', 1, true);
  listeners.click({ target: { closest: () => ({ disabled: false, dataset: { save: '' } }) } });
  assert.strictEqual(app.draftCount(), 2);
  assert.strictEqual(elements.toast.textContent, '儲存失敗，請再試一次');
});

test('overview lists unfinished task groups ending within 48 hours', () => {
  const data = researchData();
  data.tasks[1].end = new Date(Date.now() + 50 * 36e5).toISOString();
  const { app, main } = loadApp(data);
  app.ui.tab = 'overview'; app.render();
  assert.match(main.innerHTML, /限時調查：adidas/);
  assert.ok(!main.innerHTML.includes('10 月田野調查'));
});

test('overview immediately removes any group the task page marks all done', () => {
  const data = researchData();
  data.tasks = [
    { id: 'my-orion', name: '小隕星流星雨：獵戶座 2026', url: '', manual: true, start: null,
      end: new Date(Date.now() + 3 * 36e5).toISOString(), tasks: [{ id: 'a', text: '任務 A', reward: '' }, { id: 'b', text: '任務 B', reward: '' }] },
    { id: 'ld-generic', name: '其他快結束任務', url: 'u', start: null,
      end: new Date(Date.now() + 3 * 36e5).toISOString(), tasks: [{ id: 'a', text: '任務 A', reward: '' }] },
  ];
  const { app, main } = loadApp(data);
  app.ui.tab = 'overview'; app.render();
  assert.match(main.innerHTML, /小隕星流星雨：獵戶座 2026/);
  assert.match(main.innerHTML, /其他快結束任務/);
  app.toggleTask('my-orion', 1, true);
  app.toggleTask('ld-generic', 0, true);
  app.ui.tab = 'overview'; app.render();
  assert.ok(!main.innerHTML.includes('小隕星流星雨：獵戶座 2026'));
  assert.ok(!main.innerHTML.includes('其他快結束任務'));
});

const clickStar = (listeners, kind, id) => listeners.click({ target: { closest: () => ({ disabled: false, dataset: { fav: kind, id } }) } });

test('every news item and product card has a star outside its link', () => {
  const { app, main } = loadApp(sampleData());
  for (const tab of ['tw', 'shop', 'overview']) {
    app.ui.tab = tab; app.render();
    const links = main.innerHTML.match(/<a [^>]*>[\s\S]*?<\/a>/g) || [];
    assert.ok(links.every((a) => !a.includes('class="star"')), tab + ': star inside a link');
  }
  app.ui.tab = 'tw'; app.render();
  assert.strictEqual((main.innerHTML.match(/class="star"/g) || []).length, 2);
  app.ui.tab = 'shop'; app.render();
  assert.strictEqual((main.innerHTML.match(/class="star"/g) || []).length, 1);
});

test('starring a news item shows it on 我的最愛 and unstarring removes it', () => {
  const data = sampleData();
  const { app, main, listeners, calls } = loadApp(data);
  clickStar(listeners, 'news', 'n1');
  assert.strictEqual(calls.toggleFavorite[0][0].title, '寶可夢嘉年華');
  app.ui.tab = 'tw'; app.render();
  assert.match(main.innerHTML, /aria-pressed="true"[^>]*>★/);
  app.ui.tab = 'fav'; app.render();
  assert.match(main.innerHTML, /寶可夢嘉年華/);
  clickStar(listeners, 'news', 'n1');
  app.render();
  assert.match(main.innerHTML, /還沒有收藏，按 ☆ 加入/);
});

test('failed star reverts', () => {
  const { app, main, listeners, elements } = loadApp(sampleData(), { favFails: true });
  clickStar(listeners, 'product', 'p1');
  app.ui.tab = 'shop'; app.render();
  assert.ok(!main.innerHTML.includes('★'));
  assert.strictEqual(elements.toast.textContent, '儲存失敗，請再試一次');
});

test('我的最愛 keeps removed items, marks them 已下架, newest first', () => {
  const data = sampleData();
  data.favorites = [
    { kind: 'product', id: 'gone-p', title: '已下架的玩偶', url: 'https://p', source: 'PChome', media: '', price: '$300', image: '', date: '2026-10-01T00:00:00Z', starredAt: '2026-10-20T00:00:00Z' },
    { kind: 'news', id: 'old-n', title: '舊新聞', url: 'https://n', source: 'A 報', date: '2026-10-01T00:00:00Z', starredAt: '2026-10-02T00:00:00Z' },
    { kind: 'news', id: 'n1', title: '寶可夢嘉年華', url: 'https://n1', source: '寶可夢官網', date: '2026-10-21T00:00:00Z', starredAt: '2026-10-21T00:00:00Z' },
  ];
  const { app, main } = loadApp(data);
  app.ui.tab = 'fav'; app.render();
  assert.match(main.innerHTML, /已下架的玩偶[\s\S]*\$300/);
  assert.match(main.innerHTML, /舊新聞[^<]*<\/b><span[^>]*>A 報 · 已下架/);
  assert.ok(main.innerHTML.indexOf('寶可夢嘉年華') < main.innerHTML.indexOf('舊新聞'), 'newest starred first');
  assert.ok(!/寶可夢嘉年華<\/b><span[^>]*>[^<]*已下架/.test(main.innerHTML), 'item still on the board is not marked');
});

test('我的最愛 tab sits between 台灣活動 and 封存', () => {
  const { app, elements } = loadApp(sampleData());
  app.render();
  const order = elements.tabs.innerHTML.match(/data-tab="(\w+)"/g).map((x) => x.slice(10, -1));
  assert.deepStrictEqual(order.slice(4), ['tw', 'fav', 'archive']);
});

test('活動&新聞 source pills follow the feed table and reset to page 1', () => {
  const data = sampleData();
  const now = new Date().toISOString();
  data.news = [
    { id: 'o1', kind: 'event', title: '官網活動公告', url: 'u', source: '寶可夢官網', others: [], published: now },
    { id: 'o2', kind: 'product', title: '官網商品公告', url: 'u', source: '寶可夢官網', others: [], published: now },
    { id: 'c1', kind: 'product', title: '寶可夢中心新品報導', url: 'u', source: '上報', others: [], published: now },
    { id: 'e1', kind: 'event', title: '台灣快閃活動報導', url: 'u', source: '自由時報', others: [], published: now },
  ];
  data.products = data.products.filter((p) => p.source === 'PChome');
  const { app, main, listeners, elements } = loadApp(data);
  app.ui.tab = 'tw'; app.ui.page.tw = 2; app.render();
  assert.match(elements.tabs.innerHTML, /活動&新聞/);
  const pick = (feed) => listeners.click({ target: { closest: () => ({ disabled: false, dataset: { feed } }) } });
  pick('官方');
  assert.strictEqual(app.ui.page.tw, 1);
  assert.match(main.innerHTML, /官網活動公告/);
  assert.match(main.innerHTML, /官網商品公告/);
  assert.ok(!main.innerHTML.includes('寶可夢中心新品報導') && !main.innerHTML.includes('台灣快閃活動報導'));
  pick('官方'); pick('新聞');
  assert.match(main.innerHTML, /寶可夢中心新品報導/);
  assert.ok(!main.innerHTML.includes('官網活動公告') && !main.innerHTML.includes('台灣快閃活動報導'));
  pick('新聞'); pick('活動');
  assert.match(main.innerHTML, /台灣快閃活動報導/);
  assert.match(main.innerHTML, /data-feed="官方"[^>]*>官方 2/);
});

test('old 寶可夢中心 product rows show under 新聞 and can be starred', () => {
  const data = sampleData();
  data.products.push({ id: 'c-old', source: '寶可夢中心', name: '寶可夢中心聖誕新品', url: 'https://c', price: '', image: '', firstSeen: new Date().toISOString(), media: '上報' });
  const { app, main, listeners, calls } = loadApp(data);
  app.ui.tab = 'tw'; app.ui.feeds = ['新聞']; app.render();
  assert.match(main.innerHTML, /寶可夢中心聖誕新品[\s\S]*上報/);
  listeners.click({ target: { closest: () => ({ disabled: false, dataset: { fav: 'news', id: 'c-old' } }) } });
  assert.strictEqual(calls.toggleFavorite[0][0].title, '寶可夢中心聖誕新品');
});

// ---------- GO 活動行事曆 ----------

const DAY = 864e5, HOUR = 36e5, TZ = 8 * HOUR;
/** 台灣時間本週一往後 weeks 週的日期編號 */
function mondayNo(weeks) {
  const today = Math.floor((Date.now() + TZ) / DAY);
  return today - ((new Date(today * DAY).getUTCDay() + 6) % 7) + weeks * 7;
}
const at = (day, h) => new Date(day * DAY - TZ + h * HOUR).toISOString();
const mmdd = (day) => new Date(day * DAY).toISOString().slice(5, 10).replace('-', '/');
const click = (listeners, dataset) => listeners.click({ target: { closest: () => ({ disabled: false, dataset }) } });
/** 寬螢幕行事曆裡某活動色條的 HTML */
const wideBar = (html, id) => {
  const wide = html.slice(html.indexOf('only-wide stack'), html.indexOf('only-narrow stack'));
  return (wide.match(new RegExp(`<a class="cal-bar[^"]*"[^>]*data-cal="${id}"[^>]*>[^<]*</a>`)) || [''])[0];
};

test('calendar bars follow the example table', () => {
  const b = mondayNo(2);
  const ev = (id, s, e, category = '其他') => ({ id, name: '活動 ' + id, type: '活動', category, url: 'u', start: s, end: e, firstSeen: at(b, 0) });
  const data = sampleData({ events: [
    ev('a', at(b - 22, 10), at(b + 12, 20), 'GO Pass'),
    ev('b', at(b + 3, 10), at(b + 9, 20)),
    ev('c', at(b + 8, 18), at(b + 8, 19), '聚焦時刻'),
    ev('d', at(b + 9, 10), at(b + 15, 20)),
    ev('e', at(b + 11, 0), at(b + 12, 0)),
  ] });
  const { app, main } = loadApp(data);
  app.ui.tab = 'go'; app.ui.calWeek = 2; app.render();
  assert.match(main.innerHTML, new RegExp(`${mmdd(b)} – ${mmdd(b + 13)}`));
  const rows = [
    ['a', 2, 13, true, false, `‹ ${mmdd(b - 22)} – ${mmdd(b + 12)}`],
    ['b', 5, 7, false, false, `${mmdd(b + 3)} – ${mmdd(b + 9)}`],
    ['c', 10, 1, false, false, '18:00'],
    ['d', 11, 5, false, true, `${mmdd(b + 9)} – ${mmdd(b + 15)} ›`],
    ['e', 13, 1, false, false, '00:00'],
  ];
  for (const [id, col, span, cutL, cutR, text] of rows) {
    const bar = wideBar(main.innerHTML, id);
    assert.ok(bar, id);
    assert.match(bar, new RegExp(`grid-column:${col} / span ${span};`), id);
    assert.strictEqual(/cut-l/.test(bar), cutL, id + ' cut-l');
    assert.strictEqual(/cut-r/.test(bar), cutR, id + ' cut-r');
    assert.ok(bar.endsWith(`>${text}</a>`), `${id}: ${bar}`);
  }
  // 依開始時間排序；GO Pass 用第 4 個顏色，聚焦時刻用第 1 個
  const ids = main.innerHTML.slice(main.innerHTML.indexOf('only-wide stack'), main.innerHTML.indexOf('only-narrow stack')).match(/data-cal="(\w)"/g);
  assert.deepStrictEqual(ids.map((x) => x[10]), ['a', 'b', 'c', 'd', 'e']);
  assert.match(wideBar(main.innerHTML, 'a'), /background:#BBD4FA/);
  assert.match(wideBar(main.innerHTML, 'c'), /background:#FFE08A/);
});

test('calendar narrow view shows 7 days and today is marked', () => {
  const { app, main } = loadApp(sampleData());
  app.ui.tab = 'go'; app.render();
  const narrow = main.innerHTML.slice(main.innerHTML.indexOf('only-narrow stack'));
  assert.strictEqual((narrow.match(/class="cal-day/g) || []).length, 7);
  // 窄螢幕從今天開始
  assert.match(narrow.match(/class="cal-day[^"]*"/)[0], /today/);
  assert.match(main.innerHTML, /cal-day[^"]*today[^>]*><b>[^<]*<\/b>今天/);
  assert.match(main.innerHTML, /class="cal-today"/);
});

test('calendar follows category filter, week buttons and collapse', () => {
  const b = mondayNo(0);
  const data = sampleData();
  data.events.push({ id: 'pass', name: '十月 GO Pass', type: '活動', category: 'GO Pass', url: 'u', start: at(b - 3, 10), end: at(b + 30, 20), firstSeen: at(b, 0) });
  const store = {};
  const storage = { getItem: (k) => (k in store ? store[k] : null), setItem: (k, v) => { store[k] = String(v); } };
  const { app, main, listeners } = loadApp(data, { storage });
  app.ui.tab = 'go'; app.render();
  assert.ok(wideBar(main.innerHTML, 'e1') && wideBar(main.innerHTML, 'pass'));
  click(listeners, { gocat: '聚焦時刻' });
  assert.ok(wideBar(main.innerHTML, 'e1') && !wideBar(main.innerHTML, 'pass'));
  click(listeners, { gocat: '全部' });
  click(listeners, { calmove: '1' }); click(listeners, { calmove: '1' });
  assert.strictEqual(app.ui.calWeek, 2);
  assert.match(main.innerHTML, new RegExp(`${mmdd(b + 14)} – ${mmdd(b + 27)}`));
  assert.ok(!wideBar(main.innerHTML, 'e1'), 'e1 ends today');
  click(listeners, { calmove: '0' });
  assert.match(main.innerHTML, new RegExp(`${mmdd(b)} – ${mmdd(b + 13)}`));
  click(listeners, { caltoggle: '1' });
  assert.strictEqual(store.calOpen, '0');
  assert.ok(!main.innerHTML.includes('cal-bar') && /data-caltoggle[^>]*>展開/.test(main.innerHTML));
  // 重新整理後仍是收合
  const again = loadApp(data, { storage });
  again.app.ui.tab = 'go'; again.app.render();
  assert.ok(!again.main.innerHTML.includes('cal-bar'));
});

test('calendar shows a hint when nothing falls in the range', () => {
  const { app, main } = loadApp(sampleData());
  app.ui.tab = 'go'; app.ui.calWeek = 5; app.render();
  assert.match(main.innerHTML, /這段期間沒有活動/);
});

// ---------- 已完成的任務組 ----------

function doneData() {
  const data = sampleData();
  const iso = (h) => new Date(Date.now() + h * 36e5).toISOString();
  data.tasks = [
    { id: 'ld-done', name: '限時調查：已做完', url: 'u', start: iso(-24), end: iso(2), firstSeen: iso(-1),
      tasks: [{ id: 'a', text: '捕捉 1 隻', reward: '' }, { id: 'b', text: '捕捉 2 隻', reward: '' }] },
    { id: 'ld-todo', name: '限時調查：還沒做', url: 'u', start: iso(-24), end: iso(48), firstSeen: iso(-1),
      tasks: [{ id: 'c', text: '孵化 1 顆蛋', reward: '' }] },
  ];
  data.state.taskDone = { 'ld-done#a': true, 'ld-done#b': true };
  return data;
}

test('saved-done task groups go last, folded, and can be opened', () => {
  const { app, main, listeners } = loadApp(doneData());
  app.ui.tab = 'tasks'; app.render();
  const html = main.innerHTML;
  assert.ok(html.indexOf('還沒做') < html.indexOf('已完成 1 組') && html.indexOf('已完成 1 組') < html.indexOf('已做完'), 'done group is last');
  assert.ok(!html.includes('捕捉 1 隻'), 'folded group hides its tasks');
  assert.match(html, /data-taskopen="ld-done"[^>]*>展開/);
  click(listeners, { taskopen: 'ld-done' });
  assert.match(main.innerHTML, /捕捉 1 隻/);
  assert.match(main.innerHTML, /data-taskopen="ld-done"[^>]*>收合/);
  click(listeners, { taskopen: 'ld-done' });
  assert.ok(!main.innerHTML.includes('捕捉 1 隻'));
});

test('a group ticked to done stays in place until saved', () => {
  const data = doneData();
  data.state.taskDone = {};
  const { app, main } = loadApp(data);
  app.ui.tab = 'tasks'; app.render();
  app.toggleTask('ld-done', 1, true);
  const html = main.innerHTML;
  assert.ok(html.indexOf('已做完') < html.indexOf('還沒做'), 'not moved before saving');
  assert.ok(!html.includes('已完成 1 組') && html.includes('捕捉 1 隻'));
});

// ---------- 手動新增任務組 ----------

test('parseManualLines follows the arrow examples', () => {
  const { app } = loadApp(sampleData());
  const got = app.parseManualLines('捕捉 30 隻寶可夢 → 精靈球 ×10\n\n  轉動 5 個補給站  \n孵化 1 顆蛋 -> 星星沙 ×500\n使用 3 個莓果=>經驗值');
  assert.deepStrictEqual(JSON.parse(JSON.stringify(got)), [
    { text: '捕捉 30 隻寶可夢', reward: '精靈球 ×10' },
    { text: '轉動 5 個補給站', reward: '' },
    { text: '孵化 1 顆蛋', reward: '星星沙 ×500' },
    { text: '使用 3 個莓果', reward: '經驗值' },
  ]);
});

test('manual task form adds a group that checks in order and can be deleted', () => {
  const data = sampleData();
  const { app, main, listeners, calls } = loadApp(data);
  app.ui.tab = 'tasks'; app.render();
  click(listeners, { mfopen: '1' });
  assert.match(main.innerHTML, /新增任務組[\s\S]*data-mf="name"/);
  const type = (field, value) => listeners.input({ target: { value, dataset: { mf: field }, matches: (sel) => sel === '[data-mf]' } });
  const end = new Date(Date.now() + 3 * 864e5);
  type('name', '限時調查：30 年的軌跡');
  type('end', new Date(end.getTime() - end.getTimezoneOffset() * 6e4).toISOString().slice(0, 16));
  type('lines', '捕捉 30 隻寶可夢 → 精靈球 ×10\n轉動 5 個補給站');
  click(listeners, { mfsave: '1' });
  assert.strictEqual(calls.addManualTask.length, 1);
  assert.strictEqual(calls.addManualTask[0].tasks.length, 2);
  assert.match(main.innerHTML, /30 年的軌跡[\s\S]*手動/);
  assert.ok(!main.innerHTML.includes('data-mf="name"'), 'form closes after adding');
  assert.ok(!/30 年的軌跡[\s\S]*見原文/.test(main.innerHTML.slice(main.innerHTML.indexOf('30 年的軌跡'))), 'no 見原文 link without url');
  // 照順序勾：勾第 2 項時第 1 項一起勾
  app.toggleTask('my-1', 1, true);
  assert.strictEqual(app.draftCount(), 2);
  click(listeners, { mfdel: 'my-1' });
  assert.deepStrictEqual(calls.deleteManualTask, ['my-1']);
  assert.ok(!main.innerHTML.includes('30 年的軌跡'));
});

test('manual task form checks the input before sending', () => {
  const { app, main, listeners, calls, elements } = loadApp(sampleData());
  app.ui.tab = 'tasks'; app.render();
  click(listeners, { mfopen: '1' });
  click(listeners, { mfsave: '1' });
  assert.strictEqual(calls.addManualTask.length, 0);
  assert.match(elements.toast.textContent, /名稱/);
  assert.match(main.innerHTML, /data-mf="name"/);
});

function manualEditData() {
  const data = sampleData();
  data.tasks.push({
    id: 'my-edit', name: '打錯字的任務', url: '', manual: true,
    start: new Date(Date.now() - 864e5).toISOString(), end: new Date(Date.now() + 4 * 864e5).toISOString(),
    tasks: [
      { id: 't1', text: '捕捉 10 隻寶可夢', reward: '精靈球 ×10' },
      { id: 't2', text: '轉動 5 個補給站', reward: '' },
      { id: 't3', text: '孵化 1 顆蛋', reward: '星星沙 ×500' },
    ],
  });
  return data;
}

test('manual task edit prefills values and updates the same group with stable item ids', () => {
  const data = manualEditData();
  const { app, main, listeners, calls } = loadApp(data);
  app.ui.tab = 'tasks'; app.render();
  click(listeners, { mfedit: 'my-edit' });
  assert.strictEqual(app.ui.mf.id, 'my-edit');
  assert.strictEqual(app.ui.mf.name, '打錯字的任務');
  assert.match(app.ui.mf.lines, /捕捉 10 隻寶可夢 → 精靈球 ×10[\s\S]*孵化 1 顆蛋 → 星星沙 ×500/);
  assert.match(main.innerHTML, /編輯任務組[\s\S]*data-mf="name"/);

  const type = (field, value) => listeners.input({ target: { value, dataset: { mf: field }, matches: (sel) => sel === '[data-mf]' } });
  type('name', '修正後的任務');
  type('lines', '捕捉 20 隻寶可夢 → 精靈球 ×20\n孵化 1 顆蛋 → 星星沙 ×500\n完成 3 次團體戰 → 神奇糖果');
  click(listeners, { mfsave: '1' });

  assert.strictEqual(calls.updateManualTask.length, 1);
  assert.strictEqual(calls.updateManualTask[0][0], 'my-edit');
  assert.deepStrictEqual(JSON.parse(JSON.stringify(calls.updateManualTask[0][1].tasks)), [
    { id: 't1', text: '捕捉 20 隻寶可夢', reward: '精靈球 ×20' },
    { id: 't3', text: '孵化 1 顆蛋', reward: '星星沙 ×500' },
    { text: '完成 3 次團體戰', reward: '神奇糖果' },
  ]);
  assert.match(main.innerHTML, /修正後的任務[\s\S]*捕捉 20 隻寶可夢/);
  assert.ok(!main.innerHTML.includes('打錯字的任務'));
  assert.ok(!main.innerHTML.includes('data-mf="name"'), 'form closes after updating');
});

test('failed manual task edit keeps the form and typed values', () => {
  const data = manualEditData();
  const { app, main, listeners, calls, elements } = loadApp(data, { manualUpdateFails: true });
  app.ui.tab = 'tasks'; app.render();
  click(listeners, { mfedit: 'my-edit' });
  listeners.input({ target: { value: '尚未儲存的修正', dataset: { mf: 'name' }, matches: (sel) => sel === '[data-mf]' } });
  click(listeners, { mfsave: '1' });
  assert.strictEqual(calls.updateManualTask.length, 1);
  assert.strictEqual(app.ui.mf.open, true);
  assert.strictEqual(app.ui.mf.name, '尚未儲存的修正');
  assert.match(main.innerHTML, /編輯任務組[\s\S]*尚未儲存的修正/);
  assert.match(elements.toast.textContent, /更新失敗/);
});

test('task-local actions preserve scroll while tab and page navigation go to the top', () => {
  const data = manualEditData();
  data.tasks.unshift(doneData().tasks[0]);
  data.state.taskDone['ld-done#a'] = true;
  data.state.taskDone['ld-done#b'] = true;
  const { app, listeners, scrollCalls, window } = loadApp(data, { scrollY: 640 });
  app.ui.tab = 'tasks'; app.render();
  const preserved = (action, label) => {
    window.scrollY = 640; window.pageYOffset = 640; scrollCalls.length = 0;
    action();
    assert.deepStrictEqual(scrollCalls.at(-1), [0, 640], label);
  };
  preserved(() => listeners.change({ target: { checked: true, dataset: { task: 'my-edit', index: '1' }, matches: (sel) => sel === 'input[data-task]' } }), 'checkbox');
  preserved(() => click(listeners, { taskopen: 'ld-done' }), 'fold');
  preserved(() => click(listeners, { flag: 'gaveUp', id: 'ld-done', value: '1' }), 'abandon and response');
  preserved(() => click(listeners, { mfedit: 'my-edit' }), 'edit');
  preserved(() => click(listeners, { mfdel: 'my-edit' }), 'delete and response');

  window.scrollY = 640; scrollCalls.length = 0;
  click(listeners, { tab: 'shop' });
  assert.deepStrictEqual(scrollCalls.at(-1), [0, 0], 'tab');
  window.scrollY = 640; scrollCalls.length = 0;
  click(listeners, { page: 'shop:2' });
  assert.deepStrictEqual(scrollCalls.at(-1), [0, 0], 'pager');
});

test('task save status and button share the title row and do not use a standalone savebar', () => {
  const { app, main } = loadApp(researchData());
  app.ui.tab = 'tasks'; app.render();
  assert.match(main.innerHTML, /class="task-title-row"[\s\S]*<h2>任務待辦<\/h2>[\s\S]*data-save/);
  assert.ok(!main.innerHTML.includes('class="savebar'));
  app.ui.tab = 'overview'; app.render();
  assert.ok(!main.innerHTML.includes('data-save'));
});
