## Problem

Ryan reported four display problems on 2026-10-22:

1. GO 活動 shows events with 「剩餘 Infinity 天」 that are really past events.
2. Event names are squeezed into a narrow column; long text gets crushed in several places.
3. 任務待辦 lists 「領取獎勵」 as tasks.
4. 新商品 shows exact duplicate products.

## Root Cause

1. ScrapedDuck sometimes drops the dates of past events. On 2026-10-21 `events.min.json` had `Fall Marathon: Buddy Trek` and `Dynamax Sneasel during Max Monday` (Max Monday of 2026-10-19, already over) with `start` and `end` both `null`. `build_events` keeps events without an end ("Event without end" in go-events), and the page computes the remaining time as `Infinity`, so `leftText` prints 「Infinity 天」 and the event never moves to 封存.
2. `gas/Styles.html` has `th:first-child, td:first-child { width: 56px }`, written for the old checkbox column. Since `remove-event-checkbox` the event name is the first column, so it is capped at 56 px (measured 100 px with padding at 1280 px width) while 類型 takes 347 px and 開始/結束 230 px each; the table then overflows and 剩餘 is cut off. On phones, task rows keep the reward in a side column, which squeezes the task text to about five characters per line (10 月田野調查, 375 px width), and the task-group header squeezes the title next to 完成數 and 放棄.
3. LeekDuck research steps end with a 「Claim Reward!」 row (translated to 領取獎勵); it is the step reward, not a task.
4. PChome lists the same product under different product Ids. Example from 2026-10-21: `DECU5W-A900FSAGQ` and `DEAS4E-A900FSAIT`, both 「皮卡丘 卡比獸 百變怪 精靈球 造型存錢筒」 at $590. The scraper dedupes by Id only.

## Proposed Solution

- Scraper drops events without an end time; the page shows 「未定」 instead of 「Infinity」 for any row that still lacks one, and treats such rows as not listable.
- Layout fixes for every tab (details in design.md), checked at 375, 768 and 1280 px.
- Scraper drops tasks whose English text is 「Claim Reward!」 and any task whose translated text is 「領取獎勵」.
- Products are deduped by normalised name + price in the scraper, and the page hides any remaining exact duplicates already stored in the sheet.

## Non-Goals (optional)

- No new features; sequential tasks, the save button and favourites are separate changes.

## Success Criteria

- No event with a missing end appears on GO 活動; no 「Infinity」 text anywhere.
- At 375, 768 and 1280 px every event name, task text and news title wraps on whole lines with at least 12 characters per line, and no table column is cut off.
- No 「領取獎勵」 row on 任務待辦.
- The two $590 piggy-bank listings appear once.

## Impact

- Affected specs: go-events, event-research, product-feed, dashboard
- Affected code:
  - Modified: scraper/main.py, scraper/sources/pchome.py, gas/App.html, gas/Styles.html, tests/test_scraper.py, tests/gas/app.test.js
  - New: none
  - Removed: none
