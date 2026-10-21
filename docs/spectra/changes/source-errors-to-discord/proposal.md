## Summary

Stop showing scrape failures on the 總覽 page; send one Discord message to the existing webhook when a daily run has failed sources.

## Motivation

The red 「今天這些來源抓取失敗」 banner sits on top of 總覽 every day a source fails, although only Ryan can act on it. Ryan already gets task reminders in Discord and wants failures there too.

## Proposed Solution

- `doPost`, after the data is written, posts one message to `DISCORD_WEBHOOK_URL` when `data.errors` is not empty: 「⚠️ 每日抓取有來源失敗：<來源（原因）、…>」, the run time, and the dashboard link if `VIEW_URL` is set.
- A failed webhook call is logged and does not change the ingest response.
- The overview banner and the `errors` field in `getData` are removed; errors stay recorded in the 狀態 sheet.

## Non-Goals (optional)

- No new secrets or webhooks; GitHub Actions does not post to Discord itself.
- No retry or de-duplication across days.

## Impact

- Affected specs: dashboard, discord-reminder
- Affected code:
  - Modified: gas/Code.gs, gas/App.html, tests/gas/merge.test.js, README.md
  - New: none
  - Removed: none
