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

test('products tab shows announcements without price as 看消息', () => {
  const { app, main } = loadApp(sampleData());
  app.ui.tab = 'shop'; app.render();
  assert.match(main.innerHTML, /寶可夢 伊布 馬克杯[\s\S]*看消息/);
  assert.match(main.innerHTML, /\$1,280/);
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

test('field research ticks one task only', () => {
  const data = researchData();
  const { app } = loadApp(data);
  app.toggleTask('field-202610', 4, true);
  assert.deepStrictEqual(doneOf(data, 'field-202610', app), [5]);
});

test('ticks stay as a draft until saved, then saved in one call', () => {
  const data = researchData();
  const { app, savebar, listeners, calls } = loadApp(data);
  app.ui.tab = 'tasks';
  app.toggleTask('ld-adidas', 2, true);
  assert.strictEqual(calls.saveTasks.length, 0);
  assert.match(savebar.innerHTML, /有 3 項變更未儲存/);
  app.ui.tab = 'shop'; app.render();
  assert.strictEqual(app.draftCount(), 3, 'tab switch keeps the draft');
  const ev = { preventDefault() { this.prevented = true; } };
  listeners['window:beforeunload'](ev);
  assert.ok(ev.prevented, 'leaving with unsaved changes asks first');
  listeners.click({ target: { closest: () => ({ disabled: false, dataset: { save: '' } }) } });
  assert.strictEqual(calls.saveTasks.length, 1);
  assert.deepStrictEqual(Object.keys(calls.saveTasks[0]).sort(), ['ld-adidas#t1', 'ld-adidas#t2', 'ld-adidas#t3']);
  assert.strictEqual(app.draftCount(), 0);
  assert.match(savebar.innerHTML, /已儲存/);
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

const clickStar = (listeners, kind, id) => listeners.click({ target: { closest: () => ({ disabled: false, dataset: { fav: kind, id } }) } });

test('every news item and product card has a star outside its link', () => {
  const { app, main } = loadApp(sampleData());
  for (const tab of ['tw', 'shop', 'overview']) {
    app.ui.tab = tab; app.render();
    const links = main.innerHTML.match(/<a [^>]*>[\s\S]*?<\/a>/g) || [];
    assert.ok(links.every((a) => !a.includes('class="star"')), tab + ': star inside a link');
  }
  app.ui.tab = 'tw'; app.render();
  assert.strictEqual((main.innerHTML.match(/class="star"/g) || []).length, 1);
  app.ui.tab = 'shop'; app.render();
  assert.strictEqual((main.innerHTML.match(/class="star"/g) || []).length, 2);
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
