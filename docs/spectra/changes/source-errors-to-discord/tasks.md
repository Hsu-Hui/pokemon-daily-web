## 1. Discord notice

- [ ] 1.1 Add `notifyErrors_(errors, generatedAt)` called at the end of `doPost`, posting to `DISCORD_WEBHOOK_URL` and swallowing webhook failures (Source failure notice requirement). Verify: node tests with a stubbed `UrlFetchApp` — one message when errors exist, none when empty, `ok:true` when the stub throws.

## 2. Overview

- [ ] 2.1 Remove the error banner from the overview renderer and `errors` from `getData` (Data loading requirement). Verify: node test that `getData()` has no `errors` key, plus manual check of 總覽. [after: 1.1]
