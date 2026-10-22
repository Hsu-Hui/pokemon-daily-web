## 問題

Ryan 在 2026-10-22 回報四個顯示問題：

1. GO 活動出現「剩餘 Infinity 天」的活動，其實都是已經結束的活動。
2. 活動名稱被擠在很窄的欄位；好幾個地方的長文字都被壓縮。
3. 任務待辦把「領取獎勵」列成任務。
4. 新商品有完全重複的商品。

## 根本原因

1. ScrapedDuck 會把已經結束的活動的時間清掉，但活動本身還留在清單裡。2026-10-21 的 `events.min.json` 有 `Fall Marathon: Buddy Trek` 和 `Dynamax Sneasel during Max Monday`（10/19 的極巨星期一，已經結束），`start` 和 `end` 都是 `null`；2026-10-22 有 `Pokémon TCG: 30th Celebration`、`Dialga in 5-star Raid Battles`、`Mega Dragonite in Mega Raids`、`Palkia Raid Hour`（10/21）。`build_events` 會保留沒有結束時間的活動（go-events 的「沒有結束時間的活動」情境），頁面把剩餘時間算成 `Infinity`，所以 `leftText` 顯示「Infinity 天」，這些活動也永遠不會進封存。
2. `gas/Styles.html` 有一條 `th:first-child, td:first-child { width: 56px }`，原本是給勾選方塊欄用的。`remove-event-checkbox` 之後活動名稱變成第一欄，就被限制在 56px（1280px 寬度下量到含內距 100px），類型欄卻有 347px、開始／結束各 230px，表格超出畫面，「剩餘」欄被裁掉。手機上任務列的獎勵放在旁邊一欄，任務文字被擠到每行約 5 個字（10 月田野調查，375px 寬度）；任務組標題也被「完成數」和「放棄」擠到。
3. LeekDuck 的調查步驟最後一列是「Claim Reward!」（翻成「領取獎勵」），那是步驟獎勵，不是任務。
4. PChome 同一件商品用不同的商品編號上架。2026-10-21 的例子：`DECU5W-A900FSAGQ` 和 `DEAS4E-A900FSAIT`，都是「皮卡丘 卡比獸 百變怪 精靈球 造型存錢筒」、$590。爬蟲只用商品編號去重。

## 解決方式

- 爬蟲不收沒有結束時間的活動；頁面也把這種活動擋掉，不再出現「Infinity」。
- 每個分頁的排版修正（細節見 design.md），在 375、768、1280px 寬度檢查。
- 爬蟲略過英文是「Claim Reward!」、以及翻譯後是「領取獎勵」的任務。
- 商品用「名稱（整理空白、不分大小寫）＋價格」去重；頁面顯示時再去重一次，試算表裡已經存的重複商品也不再顯示。

## 不做的事

- 不加新功能；任務依序勾選、儲存按鈕、我的最愛是另外的 change。

## 成功條件

- GO 活動不會出現沒有結束時間的活動，頁面上任何地方都沒有「Infinity」。
- 在 375、768、1280px 寬度下，活動名稱、任務文字和新聞標題都整行換行、每行至少 12 個字，表格欄位不被裁切。
- 任務待辦沒有「領取獎勵」。
- 那兩筆 $590 存錢筒只顯示一筆。

## 影響

- 影響的規格：go-events、event-research、product-feed、dashboard
- 影響的程式：
  - 修改：scraper/main.py、scraper/sources/pchome.py、gas/App.html、gas/Styles.html、tests/test_scraper.py、tests/gas/app.test.js
  - 新增：無
  - 刪除：無
