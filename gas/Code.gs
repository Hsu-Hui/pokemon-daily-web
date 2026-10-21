/**
 * 寶可夢每日看板（Google Apps Script）
 *
 * - doPost：GitHub Actions 每天凌晨把爬到的資料送進來，存到這個試算表；有來源抓取失敗時發 Discord。
 * - doGet：看板網頁。
 * - remindTasks：每小時檢查，任務快結束還沒完成就發 Discord。
 *
 * 勾選、放棄的紀錄存在每個人自己的 UserProperties，互不影響。
 * 保留天數、提醒時間等設定在 shared/board.json（這裡用產生的 Board.gs 裡的 BOARD）。
 */

const SHEETS = {
  events: { name: '活動', headers: ['id', 'name', 'type', 'url', 'start', 'end', 'firstSeen', 'category'] },
  tasks: { name: '任務', headers: ['id', 'name', 'url', 'start', 'end', 'tasks', 'firstSeen'] },
  products: { name: '商品', headers: ['id', 'source', 'name', 'url', 'price', 'image', 'firstSeen', 'media'] },
  news: { name: '新聞', headers: ['id', 'kind', 'title', 'url', 'source', 'others', 'published', 'firstSeen'] },
  seen: { name: '已看過', headers: ['id', 'firstSeen'] },
  meta: { name: '狀態', headers: ['key', 'value'] },
};
const JSON_COLUMNS = ['tasks', 'others'];
const DAY = 24 * 3600 * 1000;

// ---------- 試算表讀寫 ----------

function sheet_(key) {
  const def = SHEETS[key];
  const ss = SpreadsheetApp.getActive();
  let sh = ss.getSheetByName(def.name);
  if (!sh) {
    sh = ss.insertSheet(def.name);
    sh.getRange(1, 1, 1, def.headers.length).setValues([def.headers]).setFontWeight('bold');
    sh.setFrozenRows(1);
  }
  return sh;
}

function readRows_(key) {
  const sh = sheet_(key);
  const headers = SHEETS[key].headers;
  if (sh.getLastRow() < 2) return [];
  return sh.getRange(2, 1, sh.getLastRow() - 1, headers.length).getValues().map((row) => {
    const obj = {};
    headers.forEach((h, i) => {
      let v = row[i];
      if (v instanceof Date) v = v.toISOString();
      if (JSON_COLUMNS.includes(h)) v = v ? JSON.parse(v) : [];
      obj[h] = v === '' ? null : v;
    });
    return obj;
  });
}

function writeRows_(key, objs) {
  const sh = sheet_(key);
  const headers = SHEETS[key].headers;
  sh.getRange(1, 1, 1, headers.length).setValues([headers]); // 欄位有增加時更新標題列
  if (sh.getLastRow() > 1) sh.getRange(2, 1, sh.getLastRow() - 1, headers.length).clearContent();
  if (!objs.length) return;
  const values = objs.map((o) => headers.map((h) => {
    const v = o[h];
    if (v === null || v === undefined) return '';
    return JSON_COLUMNS.includes(h) ? JSON.stringify(v) : v;
  }));
  // 先設成純文字，避免日期、價格被試算表自動轉格式
  sh.getRange(2, 1, values.length, headers.length).setNumberFormat('@').setValues(values);
}

function readMeta_() {
  const meta = {};
  readRows_('meta').forEach((r) => { meta[r.key] = r.value; });
  return meta;
}

// ---------- 合併每日資料 ----------

/** 活動、任務：用新資料覆蓋；不在新資料裡的，結束後保留一段時間給封存頁。 */
function mergeTimed_(existing, incoming, now) {
  const old = {};
  existing.forEach((r) => { old[r.id] = r; });
  const seen = {};
  const out = incoming.map((r) => {
    seen[r.id] = true;
    return Object.assign({}, r, { firstSeen: (old[r.id] && old[r.id].firstSeen) || now.toISOString() });
  });
  existing.forEach((r) => {
    if (seen[r.id] || !r.end) return;
    if (now - new Date(r.end) < BOARD.keepArchiveDays * DAY) out.push(r);
  });
  return out;
}

/** 商品、新聞：只加第一次看到的，超過保留天數就刪掉。 */
function mergeFresh_(existing, incoming, seenMap, keepDays, now) {
  const have = {};
  existing.forEach((r) => { have[r.id] = true; });
  const added = incoming
    .filter((r) => !have[r.id] && !seenMap[r.id])
    .map((r) => Object.assign({}, r, { firstSeen: now.toISOString() }));
  added.forEach((r) => { seenMap[r.id] = r.firstSeen; });
  return existing.concat(added).filter((r) => now - new Date(r.firstSeen) < keepDays * DAY);
}

/** 格式錯誤、密碼不對或處理失敗都回 JSON，不回 Apps Script 的錯誤頁。 */
function doPost(e) {
  try {
    const body = JSON.parse(e.postData.contents);
    const secret = PropertiesService.getScriptProperties().getProperty('INGEST_SECRET');
    if (!secret || body.secret !== secret) return json_({ ok: false, error: 'bad secret' });
    const data = body.data || {};
    const result = ingest_(data);
    notifyErrors_(data.errors || [], data.generatedAt);
    return json_(result);
  } catch (err) {
    return json_({ ok: false, error: String(err && err.message || err) });
  }
}

function ingest_(data) {
  const lock = LockService.getScriptLock();
  lock.waitLock(30000);
  try {
    const now = new Date();
    const seenMap = {};
    readRows_('seen').forEach((r) => {
      if (now - new Date(r.firstSeen) < BOARD.keepSeenDays * DAY) seenMap[r.id] = r.firstSeen;
    });

    const events = mergeTimed_(readRows_('events'), data.events || [], now);
    const tasks = mergeTimed_(readRows_('tasks'), data.taskGroups || [], now);
    const products = mergeFresh_(readRows_('products'), data.products || [], seenMap, BOARD.keepProductDays, now);
    const news = mergeFresh_(readRows_('news'), data.news || [], seenMap, BOARD.keepNewsDays, now);

    writeRows_('events', events);
    writeRows_('tasks', tasks);
    writeRows_('products', products);
    writeRows_('news', news);
    writeRows_('seen', Object.keys(seenMap).map((id) => ({ id: id, firstSeen: seenMap[id] })));
    writeRows_('meta', [
      { key: 'updatedAt', value: data.generatedAt || now.toISOString() },
      { key: 'errors', value: (data.errors || []).join('、') },
    ]);
    return { ok: true, events: events.length, tasks: tasks.length, products: products.length, news: news.length };
  } finally {
    lock.releaseLock();
  }
}

/** 每日抓取有來源失敗時發一則 Discord；webhook 失敗只記錄，不影響接收資料。 */
function notifyErrors_(errors, generatedAt) {
  const props = PropertiesService.getScriptProperties();
  const webhook = props.getProperty('DISCORD_WEBHOOK_URL');
  if (!errors.length || !webhook) return;
  const when = Utilities.formatDate(generatedAt ? new Date(generatedAt) : new Date(), 'Asia/Taipei', 'yyyy/MM/dd HH:mm');
  const lines = [`⚠️ 每日抓取有來源失敗：${errors.join('、')}`, `抓取時間：${when}`];
  const viewUrl = props.getProperty('VIEW_URL');
  if (viewUrl) lines.push(`<${viewUrl}>`);
  try {
    UrlFetchApp.fetch(webhook, {
      method: 'post',
      contentType: 'application/json',
      payload: JSON.stringify({ content: lines.join('\n').slice(0, 1900) }),
    });
  } catch (err) {
    Logger.log('Discord 通知失敗：' + err);
  }
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

// ---------- 網頁 ----------

function doGet() {
  // 接收資料用的部署（任何人都能存取）沒有登入者，不顯示看板
  if (!Session.getActiveUser().getEmail()) {
    return HtmlService.createHtmlOutput('請用看板的網址開啟。');
  }
  return HtmlService.createTemplateFromFile('Index').evaluate()
    .setTitle('寶可夢每日看板')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1');
}

/** Index.html 用 <?!= include('Styles') ?> 把其他 HTML 檔接進來。 */
function include(name) {
  return HtmlService.createHtmlOutputFromFile(name).getContent();
}

/** 每個人自己的勾選紀錄：done（活動）、taskDone（"任務組id#第幾項"）、gaveUp（任務組）。 */
function loadState_() {
  const raw = PropertiesService.getUserProperties().getProperty('state');
  const state = raw ? JSON.parse(raw) : {};
  return { done: state.done || {}, taskDone: state.taskDone || {}, gaveUp: state.gaveUp || {} };
}

function getData() {
  const meta = readMeta_();
  return {
    updatedAt: meta.updatedAt || null,
    events: readRows_('events'),
    tasks: readRows_('tasks'),
    products: readRows_('products'),
    news: readRows_('news'),
    state: loadState_(),
    config: BOARD,
  };
}

/** 網頁呼叫：kind 是 done / taskDone / gaveUp，value 為 false 時取消。 */
function setFlag(kind, id, value) {
  if (['done', 'taskDone', 'gaveUp'].indexOf(kind) < 0) throw new Error('bad kind');
  const lock = LockService.getUserLock();
  lock.waitLock(10000);
  try {
    const state = loadState_();
    if (value) state[kind][id] = true;
    else delete state[kind][id];
    PropertiesService.getUserProperties().setProperty('state', JSON.stringify(state));
    return state;
  } finally {
    lock.releaseLock();
  }
}

// ---------- Discord 任務提醒 ----------

function remindTasks() {
  const webhook = PropertiesService.getScriptProperties().getProperty('DISCORD_WEBHOOK_URL');
  if (!webhook) return;
  const viewUrl = PropertiesService.getScriptProperties().getProperty('VIEW_URL');
  const state = loadState_();
  const now = new Date();
  readRows_('tasks').forEach((g) => {
    if (!g.end || state.gaveUp[g.id]) return;
    const left = new Date(g.end) - now;
    if (left <= 0 || left > BOARD.remindHours * 3600 * 1000) return;
    const todo = g.tasks.filter((t, i) => !state.taskDone[g.id + '#' + (t.id || i)]);
    if (!todo.length) return;
    const h = Math.floor(left / 3600000);
    const m = Math.floor((left % 3600000) / 60000);
    const lines = [
      `⏰ **任務快結束：${g.name}**`,
      `剩 ${h} 小時 ${m} 分，還有 ${todo.length} 項沒完成：`,
    ].concat(todo.slice(0, 15).map((t) => `・${t.text}${t.reward ? ' → ' + t.reward : ''}`));
    if (todo.length > 15) lines.push(`…還有 ${todo.length - 15} 項`);
    if (viewUrl) lines.push(`<${viewUrl}>`);
    UrlFetchApp.fetch(webhook, {
      method: 'post',
      contentType: 'application/json',
      payload: JSON.stringify({ content: lines.join('\n').slice(0, 1900) }),
    });
  });
}

// ---------- 第一次設定 ----------

/** 在編輯器選這個函式按「執行」一次：建立分頁、產生密碼、設定每小時提醒。 */
function setup() {
  Object.keys(SHEETS).forEach(sheet_);
  const props = PropertiesService.getScriptProperties();
  let secret = props.getProperty('INGEST_SECRET');
  if (!secret) {
    secret = Utilities.getUuid().replace(/-/g, '');
    props.setProperty('INGEST_SECRET', secret);
  }
  ScriptApp.getProjectTriggers()
    .filter((t) => t.getHandlerFunction() === 'remindTasks')
    .forEach((t) => ScriptApp.deleteTrigger(t));
  ScriptApp.newTrigger('remindTasks').timeBased().everyHours(1).create();
  Logger.log('GAS_INGEST_SECRET（貼到 GitHub Secrets）：' + secret);
}
