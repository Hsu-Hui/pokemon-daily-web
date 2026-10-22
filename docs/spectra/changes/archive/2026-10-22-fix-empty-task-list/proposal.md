## 問題

任務待辦頁一直只有每月的田野調查任務組。2026-10-21 的每日執行（Actions run 39625663387）只送出 1 個任務組（10 月田野調查），Apps Script 也存進去了（`tasks: 1`）；活動的限時調查從來沒出現過。

## 根本原因

- 巴哈來源只讀標題含「調查／任務／課題」的【情報】文。2026-10-21 看板第一頁有 15 篇【情報】，只有置頂的整理串符合，而它沒有可解析的期間，所以被丟掉。
- 其他【情報】文是官方公告。內文會介紹活動（例如「田野調查課題即將登場」），但沒有列出實際任務，所以就算放寬標題條件，也只會抓到含數字的說明句子，變成假任務。
- 寫了年份的巴哈期間（「2026年11月9日10:00～2026年11月13日20:00」）會解析錯：結束時間被當成開始那天的 23:59。
- 巴哈任務沒有 id，勾選紀錄靠項目順序對應，文章被編輯後會對到別的任務。

LeekDuck 的活動頁（ScrapedDuck 的活動已經有連結）用固定結構列出真正的限時／特別調查步驟（`.special-research-list .step-item .task-reward`，裡面有 `.task-text` 和 `.reward-label`），例如「adidas Timed Research (1/3)：Spin 10 PokéStops or Gyms → Razz Berry ×5」。

## 解決方式

- 新來源：對 ScrapedDuck 裡目前進行中的活動（排除略過的類型）讀 LeekDuck 活動頁，把限時／特別調查步驟整理成任務組 `ld-<活動id>`，名稱 `限時調查：<中文活動名>`，期間沿用活動。任務和獎勵用現有字典加上一張道具對照表翻譯。
- 巴哈：支援含年份的完整日期；以「。」或「！」結尾的句子不當任務。
- 巴哈和 LeekDuck 的每個任務都有固定 `id`（任務文字的雜湊），勾選紀錄會跟著任務走。

## 不做的事

- 不用 AI 翻譯，也不加 LeekDuck 活動頁以外的新網站。
- 每月田野調查任務組的產生方式不變。

## 成功條件

- 解析存下來的 adidas 活動頁，得到 3 個步驟的任務和獎勵；解析 into-the-wild 活動頁（限時調查清單是空的）不產生任務組。
- `parse_period("台灣時間2026年11月9日10:00～2026年11月13日20:00", ...)` 回傳 11/9 10:00 到 11/13 20:00。
- 存下來的巴哈公告文（萬聖節 Part 1、曠野週）不產生任務組。
- 合併後，只要 LeekDuck 有進行中活動的限時調查，下一次每日執行的紀錄就會出現一組以上的「限時調查：」。

## 影響

- 影響的規格：event-research（新）、bahamut-tasks、user-progress
- 影響的程式：
  - 修改：scraper/main.py、scraper/config.py、scraper/translate.py、scraper/sources/bahamut.py、scraper/sources/dates.py、scraper/sources/__init__.py、scraper/data/translations.json、tests/test_scraper.py
  - 新增：scraper/sources/leekduck.py、tests/fixtures/leekduck_timed_research.html、tests/fixtures/leekduck_no_research.html
  - 刪除：無
