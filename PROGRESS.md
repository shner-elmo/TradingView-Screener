# Query Tester — Session Summary

## Goal
Add an interactive **Query Tester** page to the TradingView-Screener GitHub Pages docs, plus a navlink pointing to it.

---

## What's already been pushed

### 1. `docs` branch — `docs/screener.html` ✅
A self-contained interactive query builder page at `https://shner-elmo.github.io/TradingView-Screener/screener.html`.

Features:
- **Market selector** — same button-group style as the fields pages (Stocks, Crypto, Forex, Coin, CFD, Futures, Bonds, Bond, Economy, Options)
- **Columns (SELECT)** — tag-chip input with autocomplete from `../data/metainfo/{market}.json`; Enter to add, × or Backspace to remove
- **Filters (WHERE)** — dynamic rows with field autocomplete, 16 operators (`>`, `>=`, `between`, `isin`, `has`, `is empty`, etc.), context-aware value placeholders
- **Order By** — field + asc/desc
- **Limit / Offset** — number inputs
- **Output tabs** — Python code and JSON Payload, both syntax-highlighted (highlight.js) with Copy button; regenerates live as you type
- **Run Query** — POSTs to `scanner.tradingview.com/{market}/scan`; shows results table or a graceful CORS fallback message

### 2. `claude/add-screener-testing-page-Qme3x` branch — `templates/module.html.jinja2` ✅
Added `<li><a href="../screener.html">Query Tester</a></li>` next to the Fields link in the pdoc sidebar nav. This takes effect on next CI doc-generation run.

---

## What's still pending

### Navlink in the 18 already-generated HTML files
The live docs HTML files need the same one-line addition in their embedded navbar JavaScript. Push was paused pending go-ahead.

**Files to update (18 total):**

| Version | Files |
|---|---|
| `3.0.0-rc.1` | `tradingview_screener.html` + 5 submodule pages |
| `3.0.0` | `tradingview_screener.html` + 4 submodule pages |
| `dev` | `tradingview_screener.html` + 6 submodule pages |

The change in each file is inserting this single line between Fields and Screeners:
```html
<li><a href="../screener.html">Query Tester</a></li>
```

Patched versions of all 18 files are already prepared locally at `/tmp/nav-update/docs__*.html` and verified (1 occurrence of "Query Tester" confirmed in each). Blob SHAs for the update are known. Just say the word to push them.

---

## Branch Reference

| Branch | Purpose |
|---|---|
| `docs` | Live GitHub Pages content |
| `claude/add-screener-testing-page-Qme3x` | Template change for future CI doc generation |
