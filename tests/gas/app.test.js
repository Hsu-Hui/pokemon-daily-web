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
