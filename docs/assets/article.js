/* =============================================================================
 * article.js — interactivity for the manuscript page
 *   · reading-progress bar
 *   · sticky contents rail with scroll-spy (and mobile drawer)
 *   · figure lightbox (keyboard: ← → Esc)
 *   · collapsible Methods / Supplementary (auto-open on anchor navigation)
 *   · client-side search with highlight and next/previous
 *   · light / dark reading theme (remembered)
 *   · "Copy citation" (BibTeX) and print handling
 * No dependencies. Degrades gracefully when JavaScript is unavailable.
 * ========================================================================== */
(function () {
  "use strict";

  var body = document.body;
  var main = document.querySelector(".article-main");
  if (!main) return;

  /* ── reading progress ─────────────────────────────────────────────────── */
  var progress = document.getElementById("readProgress");
  function updateProgress() {
    if (!progress) return;
    var doc = document.documentElement;
    var max = doc.scrollHeight - doc.clientHeight;
    progress.style.width = (max > 0 ? (doc.scrollTop / max) * 100 : 0) + "%";
  }
  window.addEventListener("scroll", updateProgress, { passive: true });
  window.addEventListener("resize", updateProgress);
  updateProgress();

  /* ── theme ────────────────────────────────────────────────────────────── */
  var themeToggle = document.getElementById("themeToggle");
  try {
    if (localStorage.getItem("m2h-theme") === "dark") body.classList.add("theme-dark");
  } catch (e) { /* storage unavailable */ }
  if (themeToggle) {
    themeToggle.addEventListener("click", function () {
      body.classList.toggle("theme-dark");
      try {
        localStorage.setItem("m2h-theme",
          body.classList.contains("theme-dark") ? "dark" : "light");
      } catch (e) { /* ignore */ }
    });
  }

  /* ── text size (A- / A+) ───────────────────────────────────────────────── */
  var FONT_KEY = "m2h-font-scale";
  var FONT_MIN = 0.85, FONT_MAX = 1.6, FONT_STEP = 0.1;
  function applyFontScale(s) {
    s = Math.min(FONT_MAX, Math.max(FONT_MIN, Math.round(s * 100) / 100));
    document.documentElement.style.setProperty("--a-scale", String(s));
    try { localStorage.setItem(FONT_KEY, String(s)); } catch (e) { /* ignore */ }
  }
  var fontScale = 1;
  try {
    var savedScale = parseFloat(localStorage.getItem(FONT_KEY));
    if (!isNaN(savedScale)) fontScale = savedScale;
  } catch (e) { /* ignore */ }
  applyFontScale(fontScale);
  var fontMinus = document.getElementById("fontMinus");
  var fontPlus = document.getElementById("fontPlus");
  if (fontMinus) fontMinus.addEventListener("click", function () { fontScale -= FONT_STEP; applyFontScale(fontScale); });
  if (fontPlus) fontPlus.addEventListener("click", function () { fontScale += FONT_STEP; applyFontScale(fontScale); });

  /* ── contents rail ────────────────────────────────────────────────────── */
  var toc = document.getElementById("articleToc");
  var tocToggle = document.getElementById("tocToggle");
  if (tocToggle && toc) {
    tocToggle.addEventListener("click", function () {
      var open = toc.classList.toggle("open");
      tocToggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && toc.classList.contains("open")) {
        toc.classList.remove("open");
        tocToggle.setAttribute("aria-expanded", "false");
      }
    });
  }

  function openForHash() {
    var id = decodeURIComponent((location.hash || "").slice(1));
    if (!id) return;
    var el = document.getElementById(id);
    if (el) {
      var det = el.closest("details");
      if (det) det.open = true;
    }
    if (toc && toc.classList.contains("open")) toc.classList.remove("open");
  }
  window.addEventListener("hashchange", openForHash);
  openForHash();

  /* ── scroll-spy ───────────────────────────────────────────────────────── */
  var tocLinks = Array.prototype.slice.call(
    document.querySelectorAll('.toc-inner a[href^="#"]')
  );
  var linkById = {};
  tocLinks.forEach(function (a) { linkById[a.getAttribute("href").slice(1)] = a; });
  var headings = Array.prototype.slice
    .call(main.querySelectorAll("h2[id], h3[id]"))
    .filter(function (h) { return linkById[h.id]; });

  var active = null;
  function setActive(id) {
    if (id === active) return;
    if (active && linkById[active]) linkById[active].classList.remove("active");
    active = id;
    if (linkById[id]) linkById[id].classList.add("active");
  }
  function spy() {
    var current = headings.length ? headings[0].id : null;
    for (var i = 0; i < headings.length; i++) {
      if (headings[i].getBoundingClientRect().top <= 130) current = headings[i].id;
      else break;
    }
    if (current) setActive(current);
  }
  window.addEventListener("scroll", spy, { passive: true });
  spy();

  /* ── lightbox ─────────────────────────────────────────────────────────── */
  var lightbox = document.getElementById("lightbox");
  var lbImg = document.getElementById("lbImg");
  var lbCap = document.getElementById("lbCap");
  var lbClose = document.getElementById("lbClose");
  var lbPrev = document.getElementById("lbPrev");
  var lbNext = document.getElementById("lbNext");
  var figures = Array.prototype.slice.call(main.querySelectorAll(".fig"));
  var current = -1;

  function openFig(i) {
    if (!figures.length || !lightbox) return;
    current = (i + figures.length) % figures.length;
    var fig = figures[current];
    var img = fig.querySelector("img");
    var cap = fig.querySelector("figcaption");
    if (!img) return;
    lbImg.src = img.currentSrc || img.src;
    lbImg.alt = img.alt || "";
    lbCap.innerHTML = cap ? cap.innerHTML : "";
    lightbox.hidden = false;
    body.style.overflow = "hidden";
  }
  function closeFig() {
    if (!lightbox) return;
    lightbox.hidden = true;
    lbImg.src = "";
    body.style.overflow = "";
    current = -1;
  }
  figures.forEach(function (fig, i) {
    var btn = fig.querySelector(".fig-zoom");
    if (btn) btn.addEventListener("click", function () { openFig(i); });
  });
  if (lbClose) lbClose.addEventListener("click", closeFig);
  if (lbPrev) lbPrev.addEventListener("click", function () { openFig(current - 1); });
  if (lbNext) lbNext.addEventListener("click", function () { openFig(current + 1); });
  if (lightbox) {
    lightbox.addEventListener("click", function (e) {
      if (e.target === lightbox) closeFig();
    });
  }
  document.addEventListener("keydown", function (e) {
    if (!lightbox || lightbox.hidden) return;
    if (e.key === "Escape") closeFig();
    else if (e.key === "ArrowLeft") openFig(current - 1);
    else if (e.key === "ArrowRight") openFig(current + 1);
  });

  /* ── search ───────────────────────────────────────────────────────────── */
  var searchToggle = document.getElementById("searchToggle");
  var searchPanel = document.getElementById("searchPanel");
  var searchInput = document.getElementById("searchInput");
  var searchCount = document.getElementById("searchCount");
  var searchPrev = document.getElementById("searchPrev");
  var searchNext = document.getElementById("searchNext");
  var searchClear = document.getElementById("searchClear");
  var matches = [];
  var matchIndex = -1;

  function clearMarks() {
    Array.prototype.slice.call(main.querySelectorAll("mark.search-hit")).forEach(function (m) {
      var parent = m.parentNode;
      if (!parent) return;
      parent.replaceChild(document.createTextNode(m.textContent), m);
      parent.normalize();
    });
    matches = [];
    matchIndex = -1;
    if (searchCount) searchCount.textContent = "";
  }

  function gotoMatch(i) {
    if (!matches.length) return;
    matchIndex = (i + matches.length) % matches.length;
    matches.forEach(function (m) { m.classList.remove("current"); });
    var m = matches[matchIndex];
    m.classList.add("current");
    var det = m.closest("details");
    if (det) det.open = true;
    m.scrollIntoView({ block: "center", behavior: "smooth" });
    if (searchCount) searchCount.textContent = (matchIndex + 1) + " / " + matches.length;
  }

  function escapeRx(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); }

  function runSearch(query) {
    clearMarks();
    if (!query || query.length < 2) return;
    var rx = new RegExp(escapeRx(query), "gi");
    var walker = document.createTreeWalker(main, NodeFilter.SHOW_TEXT, {
      acceptNode: function (node) {
        if (!node.nodeValue || !node.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
        var tag = node.parentNode && node.parentNode.nodeName;
        if (tag === "SCRIPT" || tag === "STYLE" || tag === "MARK") return NodeFilter.FILTER_REJECT;
        rx.lastIndex = 0;
        return rx.test(node.nodeValue) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
      }
    });
    var nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    nodes.forEach(function (node) {
      var text = node.nodeValue;
      var frag = document.createDocumentFragment();
      var last = 0, m;
      rx.lastIndex = 0;
      while ((m = rx.exec(text)) !== null) {
        if (m.index > last) frag.appendChild(document.createTextNode(text.slice(last, m.index)));
        var mark = document.createElement("mark");
        mark.className = "search-hit";
        mark.textContent = m[0];
        frag.appendChild(mark);
        matches.push(mark);
        last = m.index + m[0].length;
        if (m[0].length === 0) rx.lastIndex++;
      }
      if (last < text.length) frag.appendChild(document.createTextNode(text.slice(last)));
      node.parentNode.replaceChild(frag, node);
    });
    if (matches.length) gotoMatch(0);
    else if (searchCount) searchCount.textContent = "0 / 0";
  }

  if (searchToggle && searchPanel && searchInput) {
    searchToggle.addEventListener("click", function () {
      var hidden = searchPanel.hasAttribute("hidden");
      if (hidden) {
        searchPanel.removeAttribute("hidden");
        searchToggle.setAttribute("aria-expanded", "true");
        searchInput.focus();
      } else {
        searchPanel.setAttribute("hidden", "");
        searchToggle.setAttribute("aria-expanded", "false");
      }
    });
  }
  var searchTimer = null;
  if (searchInput) {
    searchInput.addEventListener("input", function () {
      clearTimeout(searchTimer);
      var q = searchInput.value;
      searchTimer = setTimeout(function () { runSearch(q); }, 220);
    });
    searchInput.addEventListener("keydown", function (e) {
      if (e.key === "Enter") { e.preventDefault(); gotoMatch(matchIndex + (e.shiftKey ? -1 : 1)); }
      if (e.key === "Escape") { searchInput.value = ""; clearMarks(); }
    });
  }
  if (searchNext) searchNext.addEventListener("click", function () { gotoMatch(matchIndex + 1); });
  if (searchPrev) searchPrev.addEventListener("click", function () { gotoMatch(matchIndex - 1); });
  if (searchClear) searchClear.addEventListener("click", function () {
    if (searchInput) searchInput.value = "";
    clearMarks();
    if (searchInput) searchInput.focus();
  });

  /* ── citation + print ─────────────────────────────────────────────────── */
  var btnCite = document.getElementById("btnCite");
  var bibtex = document.getElementById("bibtex");
  if (btnCite && bibtex) {
    btnCite.addEventListener("click", function () {
      var text = bibtex.value;
      var done = function () {
        btnCite.textContent = "Copied ✓";
        setTimeout(function () { btnCite.textContent = "Copy citation (BibTeX)"; }, 1600);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, function () { btnCite.textContent = "Copy failed"; });
      } else {
        bibtex.hidden = false;
        bibtex.removeAttribute("readonly");
        bibtex.select();
        try { document.execCommand("copy"); done(); } catch (e) { btnCite.textContent = "Copy failed"; }
        bibtex.hidden = true;
      }
    });
  }
  var btnPrint = document.getElementById("btnPrint");
  if (btnPrint) btnPrint.addEventListener("click", function () { window.print(); });

  window.addEventListener("beforeprint", function () {
    Array.prototype.slice.call(document.querySelectorAll("details")).forEach(function (d) {
      if (!d.open) { d.open = true; d.setAttribute("data-was-closed", "1"); }
    });
  });
  window.addEventListener("afterprint", function () {
    Array.prototype.slice.call(document.querySelectorAll("details[data-was-closed]")).forEach(function (d) {
      d.open = false;
      d.removeAttribute("data-was-closed");
    });
  });
})();
