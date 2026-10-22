## Context

The dashboard is one Apps Script page (`gas/Index.html`, `Styles.html`, `App.html`). Layout was reviewed on 2026-10-22 by rendering the real 2026-10-21 payload in a local harness at 375, 768 and 1280 px.

## Goals / Non-Goals

**Goals:**

- Remove events that have no end time.
- No squeezed text on any tab at phone, tablet or desktop width.
- No 領取獎勵 rows; no exact duplicate products.

**Non-Goals:**

- Visual redesign, new colours or fonts.
- Changing how the scraper picks sources.

## Decisions

### Drop events without an end time

`build_events` skips events whose `end` is missing; `mergeTimed_` already removes stored rows that are absent from the new payload and have no end. The page's `derive()` also filters out events without `end` so a stale row can never show 「Infinity」. Alternative rejected: show 「未定」 and keep them — Ryan wants them gone, and in the observed data they are past events.

### Layout fixes per tab

- GO 活動 table: remove the `first-child` 56 px width rule; give the name column `min-width: 240px`, let 類型 size to its tag, keep 開始/結束 `nowrap` without extra width, 剩餘 fixed at 160 px.
- Tab bar: one horizontal scrolling row on narrow screens instead of wrapping (seven tabs after favourites).
- 任務待辦 rows: below 600 px the reward moves under the task text (full width); task-group header puts the title on its own line and 完成數/放棄 on the next.
- Text containers (`.name`, task text, news titles, overview rows) use `min-width: 0` and `overflow-wrap: anywhere` so flex children can shrink without crushing.
- Verification: a node test asserts the CSS no longer contains the `first-child` width rule, and a manual screenshot pass at 375/768/1280 px of all tabs.

### Remove claim-reward rows

`build_event_research` skips steps whose English text matches `^Claim Reward!?$`; `build_tasks` and `build_event_research` both skip tasks whose translated text is 「領取獎勵」. Task ids of the remaining tasks are unchanged because ids depend on step, text and occurrence only.

### Product dedupe key

Key = name with whitespace collapsed and lower-cased + price string. `fetch_pchome` keeps the first product per key (results are newest first). `derive()` applies the same key to the stored list so duplicates already in the 商品 sheet disappear immediately; they also age out after 7 days.

## Implementation Contract

- Behaviour: no event without `end` in payload or page; no 「Infinity」 text; no 「領取獎勵」 task; one product per name+price.
- Interface: `scraper.sources.pchome.product_key(name, price) -> str`; App.html `productKey(p)` with the same normalisation.
- Acceptance: unittests for `build_events` (no-end event dropped), `build_event_research` (Claim Reward skipped), `fetch_pchome` (same name+price kept once); node tests for page dedupe and no 「Infinity」; manual screenshots at three widths.
- Scope: in — the four problems above. Out — favourites, save button, sequential tasks.

## Risks / Trade-offs

- [A real event with an unannounced end is hidden] → acceptable; ScrapedDuck lists upcoming events with dates, and the event reappears once it has an end.
- [Two different products share name and price] → treated as one; PChome product names include set/size, so this is unlikely.
