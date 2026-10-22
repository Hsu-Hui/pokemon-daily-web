// 在 Node 裡跑 gas/App.html 的 script：document、google.script.run 換成假物件，
// 用 render() 產生的 HTML 檢查每個分頁。
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const GAS = path.join(__dirname, '..', '..', 'gas');

function loadApp(data, opts = {}) {
  const calls = { saveTasks: [], toggleFavorite: [] };
  const html = fs.readFileSync(path.join(GAS, 'App.html'), 'utf8');
  const code = html.slice(html.indexOf('<script>') + 8, html.lastIndexOf('</script>'));
  const elements = {};
  const el = (id) => (elements[id] = elements[id] || { id, innerHTML: '', textContent: '', style: {}, focus() {} });
  const handlers = {};
  const listeners = {};
  const searchBox = { focused: false, caret: null, focus() { this.focused = true; }, setSelectionRange(a) { this.caret = a; } };
  const runner = {
    withSuccessHandler(fn) { handlers.success = fn; return runner; },
    withFailureHandler(fn) { handlers.failure = fn; return runner; },
    getData() { handlers.success(data); },
    setFlag() {},
    toggleFavorite(item, on) {
      calls.toggleFavorite.push([item, on]);
      if (opts.favFails) return handlers.failure(new Error('down'));
      const rest = data.favorites.filter((f) => !(f.kind === item.kind && f.id === item.id));
      handlers.success(on ? [Object.assign({ starredAt: new Date().toISOString() }, item)].concat(rest) : rest);
    },
    saveTasks(changes) {
      calls.saveTasks.push(changes);
      if (opts.saveFails) return handlers.failure(new Error('down'));
      const taskDone = Object.assign({}, data.state.taskDone);
      Object.keys(changes).forEach((k) => { if (changes[k]) taskDone[k] = true; else delete taskDone[k]; });
      handlers.success(Object.assign({}, data.state, { taskDone }));
    },
  };
  const context = {
    console, Intl, Date, setTimeout, clearTimeout,
    document: {
      getElementById: el,
      addEventListener(type, fn) { listeners[type] = fn; },
      querySelector: (sel) => (sel === 'input[data-shopquery]' ? searchBox : null),
    },
    window: { scrollTo() {}, addEventListener(type, fn) { listeners['window:' + type] = fn; } },
    localStorage: { getItem() { throw new Error('blocked'); }, setItem() { throw new Error('blocked'); } },
    google: { script: { run: runner } },
  };
  vm.createContext(context);
  vm.runInContext(code + '\n;this.__app = { ui, render, matchesQuery, toggleTask, draftCount };', context);
  return { app: context.__app, main: el('main'), savebar: el('savebar'), elements, listeners, searchBox, calls };
}

function sampleData(overrides = {}) {
  const now = Date.now();
  const iso = (h) => new Date(now + h * 36e5).toISOString();
  const board = JSON.parse(fs.readFileSync(path.join(__dirname, '..', '..', 'shared', 'board.json'), 'utf8'));
  return Object.assign({
    updatedAt: iso(-1),
    events: [{ id: 'e1', name: '聚焦時刻：皮卡丘', type: '聚焦時刻', category: '聚焦時刻', url: 'u', start: iso(-1), end: iso(2), firstSeen: iso(-1) }],
    tasks: [{ id: 'g1', name: '10 月田野調查', url: 'u', start: iso(-24), end: iso(3), firstSeen: iso(-1),
      tasks: [{ id: 't1', text: '捕捉 5 隻寶可夢', reward: '' }] }],
    products: [
      { id: 'p1', source: 'PChome', name: 'Pokémon 皮卡丘 絨毛玩偶', url: 'u', price: '$1,280', image: '', firstSeen: iso(-1), media: '' },
      { id: 'p2', source: '官網', name: '寶可夢 伊布 馬克杯', url: 'u', price: '', image: '', firstSeen: iso(-2), media: '' },
    ],
    news: [{ id: 'n1', kind: 'event', title: '寶可夢嘉年華', url: 'u', source: '寶可夢官網', others: ['A 報'], published: iso(-3), firstSeen: iso(-1) }],
    state: { taskDone: {}, gaveUp: {} },
    favorites: [],
    config: board,
  }, overrides);
}

module.exports = { loadApp, sampleData };
