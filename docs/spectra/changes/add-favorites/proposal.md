## Summary

Add a 我的最愛 tab. Each 台灣活動 news item and each 新商品 product gets a star button; starred items appear on 我的最愛 and stay there until un-starred, even after the original item is removed from the board.

## Motivation

News and products disappear after 7 days. Ryan wants to keep the ones he cares about in one place.

## Proposed Solution

- A star button (☆/★) on every news item in 台灣活動 and every product card in 新商品 (also on the overview's 今天新上架 cards). Clicking toggles the favourite immediately (not part of the 儲存 draft).
- A new 我的最愛 tab with two sections, 台灣活動 and 商品, newest-starred first, each with the same star to remove it.
- Favourites are stored per Google account in UserProperties as a snapshot (title/name, url, source, media, price, image, date, starredAt), so they keep showing after the item expires from the sheet.
- Apps Script functions `toggleFavorite(item, on)` and favourites returned by `getData`.

## Non-Goals (optional)

See design.md.

## Impact

- Affected specs: favorites (new), dashboard
- Affected code:
  - Modified: gas/Code.gs, gas/App.html, gas/Styles.html, tests/gas/app.test.js, tests/gas/merge.test.js, tests/gas/app.js, tests/gas/load.js, README.md
  - New: none
  - Removed: none
