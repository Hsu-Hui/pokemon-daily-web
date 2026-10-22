## 1. Server

- [ ] 1.1 "Snapshot per favourite in its own property" and "Immediate toggle" (Favorites storage requirement): `toggleFavorite(item, on)` with validation, 300-character trim, 500 cap, one property per item; `getData` returns `favorites`. Verify: node tests — on/off, `bad favorite`, cap, two users isolated, snapshot kept after the news row is removed.

## 2. Page

- [ ] 2.1 "Star placement" (Star buttons requirement): ☆/★ buttons beside news items, product cards and overview new-product cards, optimistic toggle with revert on failure, clicks never open the link. Verify: node tests that every news item and product card has a star button outside its `<a>`, and the failure path reverts. [after: 1.1]
- [ ] 2.2 "Favourites tab" (Favorites tab, Tabs requirements): seventh tab 我的最愛 between 台灣活動 and 封存 with two sections, pagination, 已下架 hint and empty state. Verify: node tests for both sections, sort order, 已下架, empty state; manual check on the deployed page. [after: 2.1]
- [ ] 2.3 README: describe 我的最愛 and where favourites are stored. Verify: content review. [after: 2.2]
