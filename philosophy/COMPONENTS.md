# Philosophy Book System — Component Reference

Every book page loads `../css/styles.css` + `philosophy.css` + `philosophy.js`.
No inline styles. To write Book III, copy the structure of `presocratics.html`
and use only the components below.

## Page scaffold
```html
<div class="book-page"><div class="container-main">
  <div class="breadcrumb">
    <a href="../philosophy.html">About Me</a><span class="sep">›</span>
    <a href="README.html">Library</a><span class="sep">›</span>
    <span class="current">Book N: Title</span>
  </div>
</div></div>
```
Body content lives in `<section class="section-padding book-section">` →
`<div class="container-main book-container">` (the 720px reading column).

## Book cover
```html
<header class="book-header book-cover">
  <div class="book-header-content reveal">
    <span class="cover-num">Book I</span>
    <h1>Title</h1>
    <p class="cover-subtitle">Deck Line <span class="dot"></span> ~Dates BCE</p>
    <p class="cover-epigraph">Italic opening inscription…</p>
    <div class="cover-actions">
      <a href="#first-chapter-id" class="btn-primary-custom">Begin Reading</a>
      <a href="#toc" class="cover-contents-link">Contents &darr;</a>
    </div>
    <div class="book-meta-row">
      <span><span class="dot"></span> N Chapters</span>
      <span><span class="dot"></span> ~N min read</span>
      <span><span class="dot"></span> Updated Month Year</span>
    </div>
  </div>
</header>
```
Give the TOC block `id="toc"`. A "Resume: Chapter" chip is injected
automatically once a reader has scrolled past Chapter 1 (localStorage).

## Chapter
```html
<article class="chapter reveal" id="slug">          <!-- add class "draft" if unwritten -->
  <span class="chapter-number">Chapter 01</span>
  <div class="chapter-head">
    <img src="…" class="chapter-portrait">          <!-- or placeholder: -->
    <!-- <div class="chapter-glyph"><span>Σ</span></div>  (add "dim" if draft) -->
    <div>
      <h2>Name</h2>
      <p class="chapter-dates">~Dates · Place</p>
      <p class="chapter-thesis">One-sentence core thesis.</p>
    </div>
  </div>
  <div class="chapter-tags"><span class="chapter-tag">Theme</span></div>
  <span class="chapter-readtime">⏱ N min read</span>
  <div class="chapter-body clearfix">
    <p class="lead">Opening paragraph — gets an automatic drop cap.</p>
    <!-- add class "no-dropcap" to the lead if it starts with a number/symbol -->
  </div>
  <div class="chapter-foot-nav">
    <a class="prev" href="#prev">&larr; Prev</a>
    <a class="next" href="#next">Next &rarr;</a>
  </div>
</article>
```
The sticky mini-Contents (≥1280px) with scrollspy and reading % builds itself
from every `.chapter[id]` — no markup needed.

## In-prose components
**Fragment**
```html
<div class="fragment"><span class="fnum">Fragment 12</span><p>Text.</p></div>
```
**Figure** (auto-numbered "Fig. N —"; click opens lightbox)
```html
<figure class="pfig">…img + figcaption…</figure>
<!-- variants: float-left / float-right (unfloat on mobile), full (bleeds wide) -->
```
**Pull quote**
```html
<div class="pullquote"><p>Flux is the order.</p><cite>Heraclitus</cite></div>
```
**Margin note** — floats into the right margin ≥1360px, inline card below that
```html
<aside class="margin-note"><span class="mn-term">Logos</span>Universal order…</aside>
```
**Glossary term** — hover/focus tooltip (tabindex makes it keyboard-reachable)
```html
<span class="gloss" tabindex="0" data-def="Universal rational order.">Logos</span>
```
**Callout** `<div class="callout">…</div>` ·
**Comparison** `<div class="comparison"><div class="comparison-col"><h4>A</h4><p>…</p></div>…</div>`

## Appendix
`<details class="appendix-block"><summary>Title</summary><div class="appendix-content">…`
with nested `<details class="sub-appendix">`. Deep-link via
`<a class="appendix-jump" href="#id">` — ancestors auto-open.

## Reader features (automatic on book pages)
- Reading progress bar + % in mini-Contents
- Lightbox on all figures/portraits (✕, backdrop, or Esc closes)
- Focus mode: corner button hides nav/breadcrumb/mini-TOC; Esc exits
- Print: `@media print` gives a clean, chapter-per-page document
- Resume-reading chip on the cover
- Running header ("BOOK I · Chapter") in the navbar once past the cover (≥900px)
- Era timeline built from each chapter's `.chapter-dates` (needs 3+ chapters
  with distinct years; dots deep-link to chapters)
- "Contents" link injected into every chapter foot nav
- The TOC is a `<details id="toc">`: open on desktop, collapsed on mobile

## Rules
1. No inline `style=""` — if a style is needed twice, it becomes a class here.
2. Spacing, widths, and labels come from the system, not per-page values.
3. Bump `philosophy.css?v=N` on every stylesheet change (GitHub Pages caching).
