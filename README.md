# 寶可夢每日看板

每天台灣時間凌晨 01:00 由 GitHub Actions 抓資料，存進 Google 試算表，用 Google Apps Script 做成網頁看板：

- **GO 活動**：進行中和 14 天內開始的活動（LeekDuck / ScrapedDuck，名稱用字典翻成中文），分成聚焦時刻、極巨化/超極巨化、團體戰/超級團體戰、GO Pass、限時調查、其他六類，可多選；預設依類型 → 開始 → 結束排序，點標題可以改排序。
- **任務待辦**：目前的田野調查任務和獎勵（LeekDuck / ScrapedDuck，翻成中文），加上巴哈姆特 Pokémon GO 哈啦板情報文裡的限時調查。任務結束前 4 小時還沒做完，每小時發一次 Discord 提醒；不想做可以按「放棄」。
- **新商品**：PChome 24h 最新上架的寶可夢商品、寶可夢中心新品新聞、寶可夢官網的商品公告，來源可多選，可依價格或上架時間排序。7 天後自動移除。
- **台灣活動**：寶可夢官網公告和最近 24 小時的新聞，同一件事被不同媒體報導只列一則。7 天後自動移除。
- **封存**：已完成、已放棄或已結束的項目，按錯可以「復原」。

每頁最多 25 筆，超過會分頁。勾選紀錄存在每個人自己的 Google 帳號（Apps Script 的 UserProperties），手機電腦同步，不同人互不影響。整個流程不使用 AI，不花 token。

## 檔案

| 路徑 | 用途 |
|---|---|
| `scraper/` | Python 爬蟲，`python -m scraper.main` |
| `gas/Code.gs` | Apps Script：接收資料、網頁後端、Discord 提醒 |
| `gas/Index.html` | 看板網頁 |
| `gas/appsscript.json` | Apps Script 設定（時區） |
| `.github/workflows/daily.yml` | 每天 01:00 執行 |

## 第一次設定（約 10 分鐘）

### 1. 建立試算表和 Apps Script

1. 到 [Google 試算表](https://sheets.new) 建一個新的試算表，名稱隨意（例如「寶可夢看板資料」）。
2. 上方選單 **擴充功能 → Apps Script**。
3. 把預設的 `程式碼.gs` 內容全部刪掉，貼上本 repo 的 `gas/Code.gs`。
4. 左邊「檔案」旁的 **＋ → HTML**，檔名輸入 `Index`（不用打 .html），內容貼上 `gas/Index.html`。
5. 左邊齒輪 **專案設定**，勾「在編輯器中顯示『appsscript.json』資訊清單檔案」，回到編輯器把 `appsscript.json` 換成本 repo 的 `gas/appsscript.json`（時區設成台北）。
6. 按儲存。

### 2. 執行一次 setup

1. 編輯器上方的函式選單選 `setup`，按 **執行**。
2. 第一次會要求授權：選你的帳號 →「進階」→「前往（不安全）」→ 允許。這是你自己的程式，Google 對沒有送審的程式都會這樣顯示。
3. 下方「執行記錄」會出現 `GAS_INGEST_SECRET（貼到 GitHub Secrets）：xxxx`，把這串密碼記下來。

setup 會建立試算表分頁、產生接收資料用的密碼、設定每小時的 Discord 提醒。

### 3. 部署兩個網址

右上角 **部署 → 新增部署**，類型選 **網頁應用程式**，要部署兩次：

| | 看板（你自己開的網址） | 接收資料（給 GitHub Actions 用） |
|---|---|---|
| 說明 | 看板 | 接收資料 |
| 執行身分 | **存取網頁應用程式的使用者** | **我** |
| 誰可以存取 | **只有我自己** | **所有人** |

兩次部署完成後各會給一個網址（`https://script.google.com/macros/s/.../exec`），分別記下來。接收資料的網址有密碼保護，別人拿到網址也寫不進資料，打開也看不到看板。

### 4. 設定 Discord 提醒

1. Discord 要收提醒的頻道 → **編輯頻道 → 整合 → Webhook → 新 Webhook** → **複製 Webhook 網址**。
2. 回到 Apps Script 的 **專案設定 → 指令碼屬性 → 新增指令碼屬性**：

| 屬性 | 值 |
|---|---|
| `DISCORD_WEBHOOK_URL` | 剛剛複製的 Webhook 網址 |
| `VIEW_URL` | 看板的網址（提醒訊息會附上，點了直接打開） |

### 5. 設定 GitHub Secrets

到這個 repo 的 **Settings → Secrets and variables → Actions → New repository secret**：

| 名稱 | 值 |
|---|---|
| `GAS_INGEST_URL` | 接收資料的網址 |
| `GAS_INGEST_SECRET` | 步驟 2 的密碼 |

### 6. 測試

到 **Actions → 寶可夢每日看板 → Run workflow** 手動跑一次，跑完打開看板網址就會看到資料。

## 之後更新程式

改了 `gas/` 的檔案後，要把新內容貼回 Apps Script，再到 **部署 → 管理部署**，兩個部署都按鉛筆 → 版本選「新版本」→ 部署。網址不會變。

## 給其他人使用

1. 試算表右上角「共用」，把對方加成**檢視者**。
2. **部署 → 管理部署**，看板那個部署的「誰可以存取」改成「任何已登入 Google 帳戶的使用者」。
3. 把看板網址給對方。每個人的勾選紀錄各自分開。Discord 提醒只會依你自己的勾選紀錄發送。

## 調整

- 來源網址、關鍵字、新聞相似度門檻：`scraper/config.py`
- 保留天數、提醒時間（結束前幾小時）：`gas/Code.gs` 最上面的常數
- 抓資料時間：`.github/workflows/daily.yml` 的 `cron`（UTC 時間，台灣 = UTC+8）

## 已知限制

- 巴哈的情報文是人寫的，格式不固定。程式抓「有動作（捕捉、轉動、孵化…）的條列句」當任務，箭頭或「獎勵：」後面當獎勵；抓不到獎勵會顯示「見原文」。
- 活動名稱用字典翻譯，活動專有名稱對不到時保留英文。
- 每次執行的原始資料會存成 Actions 的 artifact（`payload`，保留 7 天），抓取有問題時可以下載來看。

## 本機執行

```bash
pip install -r requirements.txt
python -m unittest
python -m scraper.main   # 沒設 GAS_INGEST_URL 時只輸出 out/payload.json
```
