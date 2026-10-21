## Summary

Add a search box to the 新商品 tab that filters products by name.

## Motivation

The tab can hold dozens of products from PChome, 寶可夢中心 and 官網; finding a specific item (for example 皮卡丘 plush) means paging through the list.

## Proposed Solution

- A search input above the product grid. Typing filters to products whose name contains the text (case-insensitive, leading/trailing spaces ignored), together with the source filter and the chosen sort; pagination counts only matching products and jumps back to page 1 on every change.
- The input keeps focus and caret position while the list re-renders; clearing it shows all products again.
- An empty result shows 「找不到符合「…」的商品」.

## Non-Goals (optional)

- No search on other tabs, no fuzzy matching, no server-side search.
- The search text is not remembered across page loads.

## Impact

- Affected specs: dashboard
- Affected code:
  - Modified: gas/App.html, gas/Styles.html
  - New: none
  - Removed: none
