## Context

Per-user data already lives in UserProperties (`state`). Apps Script limits each property value to 9 KB and all user properties to 500 KB. News and product rows are deleted from the sheet 7 days after first seen.

## Goals / Non-Goals

**Goals:**

- Star/unstar news and products from their tabs and from 我的最愛.
- Favourites survive the 7-day cleanup.

**Non-Goals:**

- Favourites for GO events or tasks.
- Sharing favourites between users.
- Notes, folders or sorting options on 我的最愛.

## Decisions

### Snapshot per favourite in its own property

Each favourite is stored as UserProperties key `fav:<kind>:<sha-1 of id, 16 hex>` with a JSON snapshot `{kind, id, title, url, source, media, price, image, date, starredAt}` (`kind` is `news` or `product`). One property per item avoids the 9 KB single-value limit; at about 400 bytes per item, 500 favourites use about 200 KB of the 500 KB quota (estimate; confirm by measuring one stored snapshot). A cap of 500 favourites returns 「我的最愛已滿」. Alternative rejected: keep only ids — starred items would vanish after 7 days.

### Immediate toggle

`toggleFavorite(item, on)` validates `kind`, requires `id`, `title` and an `http(s)` url, trims every string to 300 characters, writes or deletes the property under the user lock and returns the full favourites list. The page updates optimistically and reverts with 「儲存失敗，請再試一次」 on failure. Favourites are not part of the task 儲存 draft.

### Star placement

News items and product cards are links, so the star is a separate `<button>` placed beside the link (not inside it) and clicking it never opens the link. The star shows ★ when starred, ☆ otherwise, with `aria-pressed`.

### Favourites tab

Seventh tab 我的最愛 after 台灣活動. Two sections (台灣活動, 商品), each sorted by `starredAt` descending and paginated 25 per page; empty state 「還沒有收藏，按 ☆ 加入」. Items show the snapshot; a 「已下架」 hint appears when the item is no longer in the current list.

## Implementation Contract

- Behaviour: starring a news item makes it appear on 我的最愛 immediately and after reload; it stays after the news is removed from the sheet; un-starring anywhere removes it everywhere.
- Interface: `toggleFavorite(item, on) -> favorites[]`; `getData().favorites` array of snapshots.
- Failure modes: invalid item → `bad favorite`; more than 500 → `我的最愛已滿`; network failure → star reverts with a toast.
- Acceptance: node tests for toggle on/off, validation, cap, snapshot kept when the source row is gone, star button outside links, favourites tab rendering and empty state; manual check on the deployed page.
- Scope: in — news and product favourites, the tab. Out — events/tasks favourites.

## Risks / Trade-offs

- [UserProperties quota] → cap at 500 and per-field trimming.
- [Snapshot goes stale (price changes)] → favourites show the starred snapshot; the link opens the live page.
