const test = require('node:test');
const assert = require('node:assert');
const { loadApp, sampleData } = require('./app');

const TABS = ['overview', 'go', 'tasks', 'shop', 'tw', 'archive'];

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
