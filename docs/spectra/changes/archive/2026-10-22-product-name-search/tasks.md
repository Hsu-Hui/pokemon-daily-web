## 1. Search box

- [x] 1.1 Add the search input and `ui.shopQuery` filtering to the shop renderer, combined with source filter, sort and pagination, resetting to page 1 and keeping focus/caret across re-render (Product name search requirement). Verify: node test of the exported `matchesQuery(name, query)` helper over the example table, plus manual check on the deployed page that typing does not lose focus.
- [x] 1.2 Show 「找不到符合「…」的商品」 when nothing matches. Verify: manual check on the deployed page. [after: 1.1]
