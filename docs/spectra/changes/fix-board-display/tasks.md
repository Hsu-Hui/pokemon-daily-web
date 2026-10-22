## 1. Scraper

- [ ] 1.1 "Drop events without an end time": `build_events` skips events with no `end` (Event filtering requirement). Verify: unittest with a `start=None, end=None` event expecting it absent.
- [ ] 1.2 "Remove claim-reward rows": skip `Claim Reward!` steps and tasks translated to 領取獎勵, ids of other tasks unchanged (Claim reward rows skipped requirement). Verify: unittest on a step list with Use a Star Piece + Claim Reward!.
- [ ] 1.3 "Product dedupe key": `product_key` and first-wins dedupe in `fetch_pchome` (Duplicate products removed requirement). Verify: unittest with the two $590 piggy-bank listings and a same-name different-price pair.

## 2. Dashboard

- [ ] 2.1 Page-side safety: `derive()` drops events without `end` and dedupes products with `productKey` (Readable layout scenario "Event without end on the page", Duplicate products removed). Verify: node tests — no 「Infinity」 in any tab, duplicate products shown once. [after: 1.3]
- [ ] 2.2 "Layout fixes per tab" (Readable layout requirement): remove the first-child width rule, name column min 240 px, scrolling tab bar, stacked task rows and group header on phones, `min-width:0`/`overflow-wrap` on text containers. Verify: node test that Styles.html has no `td:first-child { ... width` rule, plus a screenshot pass of all tabs at 375/768/1280 px with the 2026-10-21 payload. [after: 2.1]
