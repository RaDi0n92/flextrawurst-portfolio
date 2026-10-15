---
name: recorder-crawler-bediengrenze
description: Keeps manual tab-wise capture separate from universal crawling and prevents hidden clicks, scrolling, expansion, stale targets, and saved-URL shortcuts; use for crawler and capture behavior changes.
---

# Crawler- und Bediengrenze

Marker: `REC-CRAWL-001`

## Contract

- Tab switch alone does nothing; one visible capture action creates one snapshot of the active tab.
- Manual mode never auto-clicks, auto-scrolls, hash-navigates, expands, follows, or probes hidden resources.
- Universal mode may have explicit traversal, but its limits, actions, target URLs, and provenance are visible and distinct from manual mode.
- A saved URL, sitemap, offline manifest, or previous snapshot is not a substitute for the current visible tab.
- Every limit is finite and validated; zero is not silently converted to infinity.
- Snapshot source, visible range, full-document projection, fetched assets, and exports are separate statuses.

## Hard stop

Do not call a crawler result “complete” when only sitemaps, one tab, a shell, or a projection exists. State exactly what was observed and what was not.
