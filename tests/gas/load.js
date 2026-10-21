// 把 gas/ 的 .gs 檔載入 Node 的 vm，Apps Script 的服務換成可以檢查的假物件。
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const GAS = path.join(__dirname, '..', '..', 'gas');

function load(overrides = {}) {
  const props = Object.assign({ INGEST_SECRET: 'secret' }, overrides.scriptProps);
  const fetched = [];
  const context = {
    console,
    ContentService: {
      MimeType: { JSON: 'json' },
      createTextOutput: (text) => ({ text, setMimeType() { return this; } }),
    },
    PropertiesService: {
      getScriptProperties: () => ({ getProperty: (k) => (k in props ? props[k] : null) }),
      getUserProperties: () => ({ getProperty: () => null, setProperty() {} }),
    },
    LockService: { getScriptLock: () => ({ waitLock() {}, releaseLock() {} }) },
    UrlFetchApp: {
      fetch: (url, options) => {
        if (overrides.fetchThrows) throw new Error('webhook down');
        fetched.push({ url, body: JSON.parse(options.payload) });
      },
    },
    Logger: { log() {} },
    Utilities: { formatDate: (d) => d.toISOString() },
  };
  vm.createContext(context);
  for (const file of ['Board.gs', 'Code.gs']) {
    vm.runInContext(fs.readFileSync(path.join(GAS, file), 'utf8'), context, { filename: file });
  }
  // 試算表換成記憶體裡的資料
  const sheets = {};
  context.readRows_ = (key) => (sheets[key] || []).map((r) => Object.assign({}, r));
  context.writeRows_ = (key, rows) => { sheets[key] = rows; };
  return { gas: context, sheets, fetched };
}

module.exports = { load };
