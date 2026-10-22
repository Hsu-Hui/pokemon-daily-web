# 寶可夢每日看板

每天台灣時間凌晨 01:00 由 GitHub Actions 抓資料，存進 Google 試算表，用 Google Apps Script 做成網頁看板：

- **GO 活動**：進行中和 14 天內開始的活動（LeekDuck / ScrapedDuck，名稱用字典翻成中文），分成聚焦時刻、極巨化/超極巨化、團體戰/超級團體戰、GO Pass、限時調查、其他六類（名稱有分類關鍵字的也會歸進去），可多選；預設依類型 → 開始 → 結束排序，點標題可以改排序。
- **任務待辦**：目前的田野調查任務和獎勵（LeekDuck / ScrapedDuck，翻成中文）、進行中活動在 LeekDuck 活動頁上的限時調查，加上巴哈姆特 Pokémon GO 哈啦板情報文裡的任務。任務結束前 4 小時還沒做完，每小時發一次 Discord 提醒；不想做可以按「放棄」。限時調查要照順序做，勾第 N 項時前面的項目會一起打勾；勾完要按最上面的「儲存」才會存起來。總覽的「快結束了，還沒完成」會列出 2 天內結束、還沒做完的任務。
- **新商品**：PChome 24h 最新上架的寶可夢商品、寶可夢中心新品新聞、寶可夢官網的商品公告，來源可多選，可以搜尋商品名稱，可依價格或上架時間排序。7 天後自動移除。
- **台灣活動**：寶可夢官網公告和最近 24 小時的新聞，同一件事被不同媒體報導只列一則。7 天後自動移除。
- **我的最愛**：台灣活動的新聞和新商品的商品旁邊有 ☆，按了就收藏到這一頁（★ 再按一次取消）。收藏會存一份當時的內容，原本的新聞或商品 7 天後被移除也還看得到，並標示「已下架」。每個 Google 帳號各自分開，最多 500 筆。
- **封存**：已結束的活動，以及已放棄或已結束的任務；放棄按錯可以「復原」。活動不用勾選，結束後自動移過來。

每頁最多 25 筆，超過會分頁。某個來源抓取失敗時，會發一則 Discord 訊息通知（不顯示在看板上）。勾選紀錄存在每個人自己的 Google 帳號（Apps Script 的 UserProperties），手機電腦同步，不同人互不影響。整個流程不使用 AI，不花 token。

## 檔案

| 路徑 | 用途 |
|---|---|
| `shared/board.json` | 爬蟲和 Apps Script 共用的設定：活動分類、提醒時間、保留天數 |
| `scraper/` | Python 爬蟲，`python -m scraper.main`；每個來源一個檔案在 `scraper/sources/` |
| `gas/Code.gs` | Apps Script：接收資料、網頁後端、Discord 提醒 |
| `gas/Board.gs` | 由 `shared/board.json` 產生（`python scripts/build_gas_config.py`），不要直接改 |
| `gas/Index.html`、`gas/Styles.html`、`gas/App.html` | 看板網頁：版面、樣式、程式 |
| `gas/appsscript.json` | Apps Script 設定（時區） |
| `.github/workflows/daily.yml` | 每天 01:00 執行 |
| `.github/workflows/deploy-gas.yml`、`scripts/deploy_gas.sh` | `gas/` 有改時自動部署到 Apps Script |

## 第一次設定（約 10 分鐘）

### 1. 建立試算表和 Apps Script

1. 到 [Google 試算表](https://sheets.new) 建一個新的試算表，名稱隨意（例如「寶可夢看板資料」）。
2. 上方選單 **擴充功能 → Apps Script**，開啟後不用貼任何程式，按一下儲存。
3. 左邊齒輪 **專案設定**，複製「指令碼 ID」。

### 2. 讓 GitHub 可以自動部署

程式碼由 GitHub Actions 用 Google 官方的 [clasp](https://github.com/google/clasp) 上傳，不用自己貼。

1. 打開 [Apps Script 設定](https://script.google.com/home/usersettings)，把 **Google Apps Script API** 切成「開啟」。
2. 在自己的電腦（要有 [Node.js](https://nodejs.org/)）開終端機執行：
   ```bash
   npx @google/clasp@2.4.2 login
   ```
   瀏覽器會跳出 Google 登入，選你的帳號並允許。完成後家目錄會多一個 `.clasprc.json`（Windows 在 `C:\Users\你的名字\.clasprc.json`，Mac 在 `~/.clasprc.json`）。
3. 到這個 repo 的 **Settings → Secrets and variables → Actions → New repository secret** 新增：

| 名稱 | 值 |
|---|---|
| `CLASPRC_JSON` | `.clasprc.json` 的完整內容（這是你的登入憑證，不要貼到別的地方） |
| `GAS_SCRIPT_ID` | 步驟 1 的指令碼 ID |

4. 到 **Actions → 部署 Apps Script → Run workflow** 跑一次。跑完在執行結果的摘要會看到兩個網址：「看板」（你自己開的）和「接收資料」（給 GitHub Actions 用）。

之後只要 `gas/` 的檔案有改並合併到 main，就會自動上傳並更新這兩個部署，網址不會變。憑證不會定期過期，只有超過 6 個月沒用、改 Google 密碼或自己撤銷授權時才要重新 login 並更新 `CLASPRC_JSON`。

### 3. 執行一次 setup

1. 回到 Apps Script 編輯器（重新整理就會看到上傳的程式），上方函式選單選 `setup`，按 **執行**。
2. 第一次會要求授權：選你的帳號 →「進階」→「前往（不安全）」→ 允許。這是你自己的程式，Google 對沒有送審的程式都會這樣顯示。
3. 下方「執行記錄」會出現 `GAS_INGEST_SECRET（貼到 GitHub Secrets）：xxxx`，把這串密碼記下來。

setup 會建立試算表分頁、產生接收資料用的密碼、設定每小時的 Discord 提醒。

兩個部署的權限由自動部署設定好：看板是「存取網頁應用程式的使用者／只有我自己」，接收資料是「我／所有人」。接收資料的網址有密碼保護，別人拿到網址也寫不進資料，打開也看不到看板。如果你之前手動建過部署，說明要是「看板」和「接收資料」，自動部署才會更新同一個網址；說明不同的話會新建部署。

### 4. 設定 Discord 提醒

任務快結束的提醒和「每日抓取有來源失敗」的通知都發到這個頻道。

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
| `GAS_INGEST_URL` | 步驟 2 摘要裡「接收資料」的網址 |
| `GAS_INGEST_SECRET` | 步驟 3 的密碼 |

### 6. 測試

到 **Actions → 寶可夢每日看板 → Run workflow** 手動跑一次，跑完打開看板網址就會看到資料。

## 之後更新程式

合併到 main 後由「部署 Apps Script」自動上傳和更新部署，不用手動貼。要重新部署也可以到 Actions 手動 Run workflow。

## 給其他人使用

1. 試算表右上角「共用」，把對方加成**檢視者**。
2. 把 `scripts/deploy_gas.sh` 最後一行的 `MYSELF` 改成 `ANYONE`（任何已登入 Google 帳戶的使用者），合併後會自動重新部署。不要在 Apps Script 管理部署裡手動改，下次自動部署會蓋回去。
3. 把看板網址給對方。每個人的勾選紀錄各自分開。Discord 提醒只會依你自己的勾選紀錄發送。

## 調整

- 來源網址、關鍵字、新聞相似度門檻：`scraper/config.py`
- 活動分類、保留天數、提醒時間（結束前幾小時）：`shared/board.json`，改完執行 `python scripts/build_gas_config.py` 更新 `gas/Board.gs`（忘了的話測試會失敗）
- 月份、流星雨、地名的中文對照：`scraper/data/translations.json`
- 活動分類的關鍵字：`shared/board.json` 每個分類的 `keywords`。活動類型對不到分類時，英文原名或中文名稱含哪個分類的關鍵字（英文不分大小寫）就歸到那一類，依分類順序取第一個符合的。例如想讓名稱有「Hour」的活動歸到聚焦時刻，就在「聚焦時刻」的 `keywords` 加上 `"Hour"`，再執行 `python scripts/build_gas_config.py`。
- 抓資料時間：`.github/workflows/daily.yml` 的 `cron`（UTC 時間，台灣 = UTC+8）

## 已知限制

- 巴哈的情報文是人寫的，格式不固定。程式抓「有動作（捕捉、轉動、孵化…）的條列句」當任務，箭頭或「獎勵：」後面當獎勵；抓不到獎勵會顯示「見原文」。
- 活動名稱用字典翻譯，活動專有名稱對不到時保留英文。
- 每次執行的原始資料會存成 Actions 的 artifact（`payload`，保留 7 天），抓取有問題時可以下載來看。

## 本機執行

```bash
pip install -r requirements.txt
python -m unittest
node --test tests/gas/*.test.js   # Apps Script 的測試（要有 Node.js）
python -m scraper.main   # 沒設 GAS_INGEST_URL 時只輸出 out/payload.json
```
