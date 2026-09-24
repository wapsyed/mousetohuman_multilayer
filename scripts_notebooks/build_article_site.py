#!/usr/bin/env python3
# =============================================================================
# build_article_site.py
#
# Build the interactive HTML version of the manuscript
#   "From mice to humans: A multi-omic predictive framework for
#    translational immunology"
# from the Word (.docx) source, in the visual language of the Mouse2Human
# project site (palette taken from the study's own figures; Merriweather
# headings + Arial body).
#
# The script is intentionally dependency-free (standard library only). It:
#   1. reads the manuscript .docx;
#   2. extracts the 15 embedded figures to docs/article-figures/ with
#      semantic file names (graphical-abstract, fig1..fig7, figS1..figS7);
#   3. converts headings, paragraphs, tables, lists, hyperlinks and
#      superscript citations to semantic HTML;
#   4. writes docs/article.html (the shell, CSS and JS are authored files
#      under docs/assets/).
#
# Usage
# -----
#   python3 scripts_notebooks/build_article_site.py \
#       --docx "/path/to/17-09-26_From Mice to Humans_Clean_numbered_WAPS.docx" \
#       --out  docs
#
# Re-run after every new manuscript revision to republish the site.
# =============================================================================

from __future__ import annotations

import argparse
import html
import os
import re
import shutil
import sys
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

# ── OOXML namespaces ─────────────────────────────────────────────────────────
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
PR_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
W = "{%s}" % W_NS
R = "{%s}" % R_NS
A = "{%s}" % A_NS
PR = "{%s}" % PR_NS
NS = {"w": W_NS}

# ── default source (rounded off by --docx) ───────────────────────────────────
DEFAULT_DOCX = (
    "/home/wasim/Área de trabalho/Github/academics_ai_personal/"
    "Article_MiceToHumans/Round 1/"
    "17-09-26_From Mice to Humans_Clean_numbered_WAPS.docx"
)

# ── project design tokens (mirrors docs/assets/style.css) ────────────────────
NAV = """<nav class="site-nav"><div class="inner">
  <a class="brand" href="index.html">Mouse2Human</a>
  <a href="overview.html">Overview</a>
  <a href="methodology.html">Methodology</a>
  <a href="code-planning.html">Code planning</a>
  <a href="predict.html">Predict</a>
  <a href="read-paper.html" class="active">Read paper</a>
  <a href="slides.html">Slides</a>
</div></nav>"""

SHELL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__TITLE__ | Mouse2Human</title>
<meta name="description" content="__DESC__">
<link rel="stylesheet" href="assets/style.css?v=d23f4625">
<link rel="stylesheet" href="assets/article.css?v=2">
</head>
<body class="article-page">
<div class="read-progress" aria-hidden="true"><span id="readProgress"></span></div>
__NAV__
<div class="article-toolbar" id="articleToolbar">
  <div class="toolbar-inner">
    <button class="tool-btn" id="tocToggle" aria-expanded="false" aria-controls="articleToc">Contents</button>
    <span class="toolbar-spacer"></span>
    <div class="font-controls" role="group" aria-label="Text size">
      <button class="tool-btn" id="fontMinus" aria-label="Decrease text size" title="Decrease text size">A&minus;</button>
      <button class="tool-btn" id="fontPlus" aria-label="Increase text size" title="Increase text size">A+</button>
    </div>
    <button class="tool-btn" id="searchToggle" aria-expanded="false" aria-controls="searchPanel">Search</button>
    <button class="tool-btn" id="themeToggle" aria-label="Toggle reading theme">Theme</button>
  </div>
  <div class="search-panel" id="searchPanel" hidden>
    <input type="search" id="searchInput" placeholder="Search the article..." autocomplete="off" aria-label="Search the article">
    <span class="search-count" id="searchCount" aria-live="polite"></span>
    <button class="tool-btn" id="searchPrev" aria-label="Previous match">&uarr;</button>
    <button class="tool-btn" id="searchNext" aria-label="Next match">&darr;</button>
    <button class="tool-btn" id="searchClear" aria-label="Clear search">&times;</button>
  </div>
</div>
<div class="article-shell">
  <aside class="article-toc" id="articleToc">__TOC__</aside>
  <main class="article-main" id="articleTop">
__CONTENT__
  </main>
</div>
<div class="foot"><span>Mouse2Human &middot; multilayer</span><span>Article &middot; September 2026</span></div>
<div class="lightbox" id="lightbox" hidden>
  <button class="lb-close" id="lbClose" aria-label="Close">&times;</button>
  <button class="lb-prev" id="lbPrev" aria-label="Previous figure">&lsaquo;</button>
  <figure class="lb-figure"><img id="lbImg" alt=""><figcaption class="lb-cap" id="lbCap"></figcaption></figure>
  <button class="lb-next" id="lbNext" aria-label="Next figure">&rsaquo;</button>
</div>
<textarea id="bibtex" hidden readonly>__BIBTEX__</textarea>
<script src="assets/article.js"></script>
</body>
</html>
"""

# ── small helpers ────────────────────────────────────────────────────────────
def esc(text: str) -> str:
    return html.escape(text or "", quote=False)


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "section"


def plain(runs_text) -> str:
    return "".join(runs_text)


# ── run / inline rendering ───────────────────────────────────────────────────
def run_inner(r: ET.Element) -> str:
    """Inner HTML of a single w:r (text, tabs and line breaks)."""
    out = []
    for child in r:
        tag = child.tag
        if tag == W + "t":
            out.append(esc(child.text or ""))
        elif tag == W + "tab":
            out.append(" ")
        elif tag == W + "br":
            out.append("<br>")
        elif tag == W + "noBreakHyphen":
            out.append("&#8209;")
        elif tag == W + "softHyphen":
            out.append("&shy;")
    return "".join(out)


def run_html(r: ET.Element) -> str:
    inner = run_inner(r)
    if not inner.strip() and "<br>" not in inner:
        return inner
    rpr = r.find(W + "rPr")
    bold = italic = False
    vert = None
    if rpr is not None:
        b = rpr.find(W + "b")
        if b is not None and b.get(W + "val", "1") not in ("0", "false", "False"):
            bold = True
        i = rpr.find(W + "i")
        if i is not None and i.get(W + "val", "1") not in ("0", "false", "False"):
            italic = True
        v = rpr.find(W + "vertAlign")
        if v is not None:
            vert = v.get(W + "val")
    if vert == "superscript":
        inner = f"<sup>{inner}</sup>"
    elif vert == "subscript":
        inner = f"<sub>{inner}</sub>"
    if bold:
        inner = f"<strong>{inner}</strong>"
    if italic:
        inner = f"<em>{inner}</em>"
    return inner


def children_html(parent: ET.Element, rels: dict) -> str:
    """Render w:r / w:hyperlink / w:ins children in document order."""
    out = []
    for child in parent:
        tag = child.tag
        if tag == W + "r":
            out.append(run_html(child))
        elif tag == W + "hyperlink":
            rid = child.get(R + "id")
            href = rels.get(rid, "")
            inner = "".join(run_html(rr) for rr in child.findall(W + "r"))
            if href:
                out.append(
                    f'<a href="{esc(href)}" target="_blank" rel="noopener">{inner}</a>'
                )
            else:
                out.append(inner)
        elif tag == W + "ins":
            out.append(children_html(child, rels))
        elif tag == W + "smartTag":
            out.append(children_html(child, rels))
    return "".join(out)


def para_text(p: ET.Element) -> str:
    return "".join(t.text or "" for t in p.iter(W + "t")).strip()


def cell_html(tc: ET.Element, rels: dict) -> str:
    """Render a table cell: join its paragraphs (runs, hyperlinks) with <br>."""
    parts = []
    for p in tc.findall(W + "p"):
        txt = children_html(p, rels).strip()
        if txt:
            parts.append(txt)
    return "<br>".join(parts)


def para_style(p: ET.Element) -> str:
    ppr = p.find(W + "pPr")
    if ppr is None:
        return ""
    ps = ppr.find(W + "pStyle")
    return ps.get(W + "val") if ps is not None else ""


def para_all_bold(p: ET.Element) -> bool:
    runs = [r for r in p.findall(W + "r") if "".join(t.text or "" for t in r.iter(W + "t")).strip()]
    if not runs:
        return False
    for r in runs:
        rpr = r.find(W + "rPr")
        if rpr is None:
            return False
        b = rpr.find(W + "b")
        if b is None or b.get(W + "val", "1") in ("0", "false", "False"):
            return False
    return True


# ── figure / caption matching ────────────────────────────────────────────────
CAP_RE = re.compile(
    r"^(Supplementary\s+table\s+\d+|Supplementary\s+Fig(?:ure)?\.?\s*S\d+|"
    r"Fig\.?\s*\d+|Figure\s*\d+)\s*\|\s*(.*)$",
    re.IGNORECASE | re.DOTALL,
)


def caption_kind(label: str):
    l = label.lower()
    m = re.match(r"supplementary\s+table\s+(\d+)", l)
    if m:
        return ("table", int(m.group(1)))
    m = re.match(r"supplementary\s+fig(?:ure)?\.?\s*s(\d+)", l)
    if m:
        return ("supp", int(m.group(1)))
    m = re.match(r"(?:fig\.?|figure)\s*(\d+)", l)
    if m:
        return ("fig", int(m.group(1)))
    return (None, None)


def figure_filename(kind: str, num: int) -> str:
    if kind == "graphical":
        return "graphical-abstract.png"
    if kind == "supp":
        return f"figS{num}.png"
    return f"fig{num}.png"


# ── inline post-processing: citation & affiliation links ─────────────────────
def link_refs(html_text: str) -> str:
    """Turn <sup>1,2,3</sup> citation runs into links to #ref-N."""
    def repl(m: re.Match) -> str:
        inner = m.group(1)
        out = []
        for part in re.split(r"(\d+)", inner):
            if part.isdigit():
                out.append(f'<a class="cite" href="#ref-{part}">{part}</a>')
            else:
                out.append(part)
        return "<sup>" + "".join(out) + "</sup>"
    return re.sub(r"<sup>([\d,\s]+)</sup>", repl, html_text)


def link_affs(html_text: str) -> str:
    """Turn <sup>1,2</sup> author affiliation markers into links to #aff-N."""
    def repl(m: re.Match) -> str:
        out = []
        for part in re.split(r"(\d+)", m.group(1)):
            if part.isdigit():
                out.append(f'<a class="aff-ref" href="#aff-{part}">{part}</a>')
            else:
                out.append(part)
        return "<sup>" + "".join(out) + "</sup>"
    return re.sub(r"<sup>([\d,\s]+)</sup>", repl, html_text)


# ── block model ──────────────────────────────────────────────────────────────
@dataclass
class Block:
    kind: str                       # heading | para | figure | table | list
    level: int = 0
    text: str = ""
    html: str = ""
    anchor: str = ""
    section: str = ""
    fig_kind: str = ""
    fig_num: int = 0
    fig_label: str = ""
    fig_media: str = ""
    fig_caption: str = ""
    rows: list = field(default_factory=list)


# headings that open a collapsible block on the site
FOLD_SECTIONS = {
    "METHODS": "methods",
    "SUPPLEMENTARY INFORMATION": "supp-info",
    "SUPPLEMENTARY TABLES": "supp-tables",
    "SUPPLEMENTARY FIGURES": "supp-figures",
}


# ── docx parsing ─────────────────────────────────────────────────────────────
def read_rels(zf: zipfile.ZipFile) -> dict:
    rels = {}
    try:
        data = zf.read("word/_rels/document.xml.rels")
    except KeyError:
        return rels
    for rel in ET.fromstring(data):
        rels[rel.get("Id")] = rel.get("Target")
    return rels


def media_target(target: str) -> str:
    # relationship targets look like "media/image1.png"
    return "word/" + target.lstrip("/")


def parse_docx(docx_path: Path):
    zf = zipfile.ZipFile(docx_path)
    rels = read_rels(zf)
    doc = ET.fromstring(zf.read("word/document.xml"))
    body = doc.find(W + "body")

    raw_blocks = []
    for el in body:
        if el.tag == W + "p":
            text = para_text(el)
            style = para_style(el)
            blip = el.find(".//" + A + "blip")
            media = None
            if blip is not None:
                rid = blip.get(R + "embed")
                if rid and rid in rels:
                    media = media_target(rels[rid])
            raw_blocks.append(
                {
                    "type": "p",
                    "text": text,
                    "style": style,
                    "html": children_html(el, rels),
                    "bold": para_all_bold(el),
                    "media": media,
                    "indent": el.find(".//" + W + "numPr") is not None,
                }
            )
        elif el.tag == W + "tbl":
            rows = []
            for tr in el.findall(W + "tr"):
                cells = []
                for tc in tr.findall(W + "tc"):
                    cells.append(cell_html(tc, rels))
                rows.append(cells)
            raw_blocks.append({"type": "tbl", "rows": rows})
    return zf, raw_blocks


def classify_heading(b, methods_region: bool) -> int:
    """Return heading level (2/3/4) or 0 if the paragraph is not a heading."""
    text = b["text"]
    if not text:
        return 0
    style = b["style"]
    upper = text.upper()
    if style == "Heading1" or upper in {
        "GRAPHICAL ABSTRACT", "ABSTRACT", "1. INTRODUCTION", "2. RESULTS",
        "3. DISCUSSION", "CONCLUSION", "METHODS", "SUPPLEMENTARY INFORMATION",
        "SUPPLEMENTARY TABLES", "SUPPLEMENTARY FIGURES", "REFERENCES",
    }:
        return 2
    if style == "Heading2":
        return 3
    if re.match(r"^\d+\.\d+\.\s", text) and b["bold"]:
        return 3
    if text == "Limitations" and b["bold"]:
        return 3
    if text in {"Data availability", "Author Contributions", "Acknowledgements"} and b["bold"]:
        return 3
    if methods_region and b["bold"] and len(text) < 90 and not text.endswith("."):
        return 4
    return 0


def parse_manuscript(docx_path: Path):
    zf, raw_blocks = parse_docx(docx_path)

    # ── front matter ────────────────────────────────────────────────────────
    title = ""
    authors_html = ""
    authors_plain = ""
    emails = ""
    equal_note = ""
    correspondence = ""
    affiliations = []

    section = ""
    for b in raw_blocks:
        if b["type"] != "p":
            continue
        text = b["text"]
        if not title and text.upper().startswith("TITLE:"):
            title = text.split(":", 1)[1].strip()
        elif not authors_html and text.upper().startswith("AUTHORS:"):
            authors_html = link_affs(b["html"].split(":", 1)[1].lstrip())
            authors_plain = text.split(":", 1)[1].strip()
            authors_plain = re.sub(r"\s*,?\s*[0-9]+(?:,[0-9]+)*", "", authors_plain)
            authors_plain = authors_plain.replace("*", "").replace("\u00b0", "")
            authors_plain = re.sub(r"\s*,\s*", ", ", authors_plain)
            authors_plain = re.sub(r"\s+", " ", authors_plain).strip(" ,")
        elif text.count("@") >= 3 and "," in text:
            emails = text
        elif text.startswith("\u00b0"):
            equal_note = text
        elif text.startswith("*Correspondence"):
            correspondence = text
        elif text.upper() == "AFFILIATIONS:":
            section = "aff"
        elif section == "aff":
            if text.upper() in {"GRAPHICAL ABSTRACT", "ABSTRACT"} or b["style"] == "Heading1":
                section = ""
            elif text:
                affiliations.append(text)

    # ── body assembly ───────────────────────────────────────────────────────
    blocks: list[Block] = []
    pending_media = None
    started = False
    current_h1 = ""
    current_section = ""
    methods_region = False
    fig_count = 0
    supp_count = 0
    refs: list[str] = []
    in_refs = False

    def flush_pending(context_h1: str, context_section: str) -> None:
        """Emit an image that was not followed by a caption (graphical abstract)."""
        nonlocal pending_media
        if not pending_media:
            return
        is_graphical = context_h1.upper() == "GRAPHICAL ABSTRACT"
        blocks.append(Block(
            kind="figure", section=context_section,
            fig_kind="graphical" if is_graphical else "extra",
            fig_num=0,
            fig_label="Graphical abstract" if is_graphical else "Figure",
            fig_media=pending_media,
            fig_caption="Graphical overview of the study." if is_graphical else "",
            anchor="fig-graphical" if is_graphical else "fig-extra",
        ))
        pending_media = None

    for b in raw_blocks:
        if b["type"] == "tbl":
            flush_pending(current_h1, current_section)
            blocks.append(Block(kind="table", rows=b["rows"], section=current_section))
            continue

        text, style, html_text = b["text"], b["style"], b["html"]
        media = b["media"]

        # references are collected separately (rendered as an ordered list)
        if in_refs:
            if text:
                refs.append(link_refs(html_text))
            continue

        # skip the front matter until the graphical-abstract heading
        if not started:
            if text.upper() == "GRAPHICAL ABSTRACT":
                started = True
                current_h1 = "GRAPHICAL ABSTRACT"
                current_section = text
                blocks.append(Block(kind="heading", level=2, text=text,
                                    anchor="graphical-abstract", section=text))
            continue

        if media:
            pending_media = media
            continue

        # caption → figure (its image is the one stored just before)
        m = CAP_RE.match(text)
        if m:
            label = m.group(1)
            caption = m.group(2).strip()
            kind, num = caption_kind(label)
            if pending_media:
                if kind == "supp":
                    supp_count += 1
                    num = supp_count
                elif kind == "fig":
                    fig_count += 1
                    num = fig_count
                anchor = f"fig-s{num}" if kind == "supp" else f"fig-{num}"
                blocks.append(Block(
                    kind="figure", section=current_section,
                    fig_kind=kind or "fig", fig_num=num, fig_label=label,
                    fig_media=pending_media, fig_caption=link_refs(caption),
                    anchor=anchor,
                ))
                pending_media = None
            continue

        if not text:
            continue

        # an image not followed by a caption (e.g. the graphical abstract)
        flush_pending(current_h1, current_section)

        # references section
        if text.upper() == "REFERENCES":
            in_refs = True
            blocks.append(Block(kind="heading", level=2, text="References",
                                anchor="references", section="references"))
            current_h1 = "REFERENCES"
            continue

        level = classify_heading(b, methods_region)
        if level:
            if level == 2:
                current_h1 = text
                current_section = text
                methods_region = text.upper() == "METHODS"
            blocks.append(Block(kind="heading", level=level, text=text,
                                anchor=slugify(text), section=current_section))
            continue

        if b["indent"]:
            blocks.append(Block(kind="list", html=link_refs(html_text),
                                section=current_section))
        else:
            blocks.append(Block(kind="para", html=link_refs(html_text),
                                text=text, section=current_section))

    flush_pending(current_h1, current_section)

    meta = {
        "title": title,
        "authors_html": authors_html,
        "authors_plain": authors_plain,
        "emails": emails,
        "equal_note": equal_note,
        "correspondence": correspondence,
        "affiliations": affiliations,
        "refs": refs,
    }
    return zf, blocks, meta


# ── HTML rendering ───────────────────────────────────────────────────────────
def render_header(meta) -> str:
    title = esc(meta["title"])
    aff_items = "".join(
        f'<li id="aff-{i}"><span class="aff-num">{i}</span><span>{esc(a)}</span></li>'
        for i, a in enumerate(meta["affiliations"], start=1)
    )
    corr = esc(meta["correspondence"])
    emails = esc(meta["emails"])
    equal_note = esc(meta["equal_note"])
    return f"""    <header class="article-head">
      <p class="eyebrow">Manuscript &middot; Genes and Immunity (under review)</p>
      <h1 id="article-title">{title}</h1>
      <p class="authors">{meta['authors_html']}</p>
      <p class="equal-note">{equal_note}</p>
      <details class="front-matter">
        <summary>Affiliations, correspondence and contact</summary>
        <ol class="affil-list">{aff_items}</ol>
        <p class="corr">{corr}</p>
        <p class="emails">{emails}</p>
      </details>
      <div class="article-actions">
        <button class="btn" id="btnCite" type="button">Copy citation (BibTeX)</button>
        <button class="btn btn-alt" id="btnPrint" type="button">Print / PDF</button>
        <a class="btn btn-alt" href="article-quarto.html">Quarto version</a>
        <a class="btn btn-alt" href="#references">Jump to references</a>
      </div>
    </header>"""


def render_figure(blk: Block, figures_dir_rel: str) -> str:
    src = f"{figures_dir_rel}/{figure_filename(blk.fig_kind, blk.fig_num)}"
    label = esc(blk.fig_label)
    cap = blk.fig_caption
    if blk.fig_kind == "graphical":
        alt = "Graphical abstract"
        cls = "fig fig-graphical"
    else:
        alt = label
        cls = "fig"
    cap_html = f'<figcaption><span class="fig-num">{label}</span> {cap}</figcaption>' if cap else ""
    return f"""    <figure class="{cls}" id="{blk.anchor}">
      <button class="fig-zoom" type="button" aria-label="Expand {label}">
        <img src="{src}" alt="{esc(alt)}" loading="lazy">
      </button>
      {cap_html}
    </figure>"""


def render_table(blk: Block) -> str:
    if not blk.rows:
        return ""
    rows = blk.rows
    thead = rows[0]
    body = rows[1:]
    head_html = "".join(f"<th>{c}</th>" for c in thead)
    body_html = "".join(
        "<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in body
    )
    return (f'<div class="table-wrap"><table class="supp-table">'
            f"<thead><tr>{head_html}</tr></thead><tbody>{body_html}</tbody>"
            f"</table></div>")


def render_body(blocks, figures_dir_rel, meta) -> tuple[str, list]:
    out = []
    toc = []
    fold_open = False
    list_buffer: list[Block] = []

    def flush_list():
        nonlocal list_buffer
        if list_buffer:
            out.append('<ul class="dot-list">')
            for it in list_buffer:
                out.append(f"<li>{it.html}</li>")
            out.append("</ul>")
            list_buffer = []

    for blk in blocks:
        if blk.kind == "heading":
            flush_list()
            if blk.level == 2 and fold_open:
                out.append("      </div></details>")
                fold_open = False
            if blk.level == 2 and blk.text.upper() in FOLD_SECTIONS:
                key = FOLD_SECTIONS[blk.text.upper()]
                out.append(
                    f'      <details class="fold" id="{key}">'
                    f'<summary><span class="fold-title">{esc(blk.text)}</span>'
                    f'<span class="fold-hint">Show</span></summary>'
                    f'<div class="fold-body">'
                )
                fold_open = True
                toc.append((2, blk.text, key))
                continue
            if blk.level == 2:
                out.append(f'      <h2 id="{blk.anchor}">{esc(blk.text)}</h2>')
                toc.append((2, blk.text, blk.anchor))
            elif blk.level == 3:
                out.append(f'      <h3 id="{blk.anchor}">{esc(blk.text)}</h3>')
                toc.append((3, blk.text, blk.anchor))
            else:
                out.append(f'      <h4 id="{blk.anchor}">{esc(blk.text)}</h4>')
                toc.append((4, blk.text, blk.anchor))
            continue

        if blk.kind == "figure":
            flush_list()
            out.append(render_figure(blk, figures_dir_rel))
            continue

        if blk.kind == "table":
            flush_list()
            out.append(render_table(blk))
            continue

        if blk.kind == "list":
            list_buffer.append(blk)
            continue

        flush_list()
        section = (blk.section or "").upper()
        cls = []
        if section == "ABSTRACT":
            cls.append("abstract")
        out.append(f'      <p class="{" ".join(cls)}">{blk.html}</p>' if cls
                   else f"      <p>{blk.html}</p>")

    flush_list()
    if fold_open:
        out.append("      </div></details>")
    return "\n".join(out), toc


def render_toc(toc) -> str:
    if not toc:
        return ""
    items = list(toc)
    # normalise the first entry to a top-level (2) item
    items[0] = (2, items[0][1], items[0][2])
    root: list = []
    stack = [(2, root)]
    for lvl, text, anchor in items:
        while len(stack) > 1 and lvl < stack[-1][0]:
            stack.pop()
        if lvl > stack[-1][0]:
            parent = stack[-1][1][-1]["children"]
            stack.append((lvl, parent))
        stack[-1][1].append(
            {"lvl": lvl, "text": text, "anchor": anchor, "children": []}
        )

    def render(nodes) -> str:
        out = ["<ol>"]
        for n in nodes:
            out.append(
                f'<li class="lvl{n["lvl"]}">'
                f'<a href="#{n["anchor"]}">{esc(n["text"])}</a>'
            )
            if n["children"]:
                out.append(render(n["children"]))
            out.append("</li>")
        out.append("</ol>")
        return "".join(out)

    return ('<nav class="toc-inner" aria-label="Article contents">'
            '<p class="toc-title">Contents</p>' + render(root) +
            '<a class="toc-top" href="#articleTop">&uarr; Back to top</a></nav>')


def render_refs(refs) -> str:
    if not refs:
        return ""
    items = "\n".join(
        f'        <li id="ref-{i}">{r}</li>' for i, r in enumerate(refs, start=1)
    )
    return f'      <ol class="ref-list">\n{items}\n      </ol>'


def build_bibtex(meta) -> str:
    first = meta["authors_plain"].split(",")[0].split()[-1] if meta["authors_plain"] else "Prates-Syed"
    year = "2026"
    return (
        "@article{PratesSyed2026Mouse2Human,\n"
        f"  author  = {{{meta['authors_plain']}}},\n"
        f"  title   = {{{meta['title']}}},\n"
        "  journal = {Genes and Immunity},\n"
        f"  year    = {{{year}}},\n"
        "  note    = {Under review}\n"
        "}"
    )


# ── figure trimming (remove the white A4 page around each figure) ────────────
def trim_whitespace(data: bytes, pad: int = 14, threshold: int = 250) -> bytes:
    """Crop the white page around a figure. Falls back to the original bytes
    when Pillow/numpy are unavailable or the image is fully white."""
    try:
        import io
        import numpy as np
        from PIL import Image
    except Exception:
        return data
    try:
        im = Image.open(io.BytesIO(data))
        if im.mode in ("RGBA", "LA", "P"):
            im = im.convert("RGBA")
            bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
            im = Image.alpha_composite(bg, im)
        im = im.convert("RGB")
        arr = np.asarray(im)
        # a pixel is "content" when any channel is clearly below white
        mask = (arr < threshold).any(axis=2)
        if not mask.any():
            return data
        ys, xs = np.where(mask)
        x0, y0 = int(xs.min()), int(ys.min())
        x1, y1 = int(xs.max()) + 1, int(ys.max()) + 1
        w, h = im.size
        x0 = max(0, x0 - pad); y0 = max(0, y0 - pad)
        x1 = min(w, x1 + pad); y1 = min(h, y1 + pad)
        if (x0, y0, x1, y1) == (0, 0, w, h):
            return data
        out = io.BytesIO()
        im.crop((x0, y0, x1, y1)).save(out, format="PNG", optimize=True)
        return out.getvalue()
    except Exception:
        return data


# ── Quarto (.qmd) rendering ──────────────────────────────────────────────────
def strip_html(text: str) -> str:
    text = re.sub(r"<br\s*/?>", " ", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def render_qmd(blocks, meta, figures_dir_rel: str) -> str:
    """Build a Quarto document that renders the same manuscript to HTML."""
    yaml = (
        "---\n"
        f'title: "{meta["title"].replace(chr(34), chr(39))}"\n'
        f'author: "{meta["authors_plain"].replace(chr(34), chr(39))}"\n'
        'date: "2026-09-23"\n'
        "format:\n"
        "  html:\n"
        "    toc: true\n"
        "    toc-depth: 3\n"
        "    toc-location: right\n"
        "    toc-title: Contents\n"
        "    theme: cosmo\n"
        "    css: assets/article-qmd.css\n"
        "    output-file: article-quarto.html\n"
        "    embed-resources: true\n"
        "    fig-cap-location: bottom\n"
        "    number-sections: false\n"
        "    lang: en\n"
        "---\n\n"
    )
    out = [yaml]
    out.append(
        '::: {.callout-note}\n'
        "Submitted to *Genes and Immunity* — currently under review. "
        "This HTML edition is generated from `article.qmd`; the fully "
        'interactive edition is [article.html](article.html).\n'
        ":::\n"
    )

    for blk in blocks:
        if blk.kind == "heading":
            out.append("#" * blk.level + " " + blk.text + "\n")
        elif blk.kind == "para":
            out.append(blk.html + "\n")
        elif blk.kind == "list":
            out.append("- " + blk.html + "\n")
        elif blk.kind == "figure":
            src = f"{figures_dir_rel}/{figure_filename(blk.fig_kind, blk.fig_num)}"
            cap = strip_html(blk.fig_caption)
            alt = f"{blk.fig_label} | {cap}" if cap else blk.fig_label
            out.append(f"![{alt}]({src}){{#{blk.anchor} width=100%}}\n")
        elif blk.kind == "table":
            out.append(render_table(blk) + "\n")

    if meta["refs"]:
        out.append('<ol class="ref-list">')
        for i, ref in enumerate(meta["refs"], start=1):
            out.append(f'<li id="ref-{i}">{ref}</li>')
        out.append("</ol>\n")
    return "\n".join(out)


def run_quarto(qmd_path: Path) -> int:
    """Render the .qmd with Quarto, trying a bundled binary if not on PATH."""
    import shutil as _shutil
    import subprocess
    exe = _shutil.which("quarto") or str(Path.home() / ".local/quarto/bin/quarto")
    if not Path(exe).exists():
        print("[quarto] not found — skipping HTML render (qmd written anyway)")
        return 1
    print(f"[quarto] rendering {qmd_path.name} …")
    res = subprocess.run([exe, "render", qmd_path.name],
                         cwd=str(qmd_path.parent))
    if res.returncode != 0:
        print(f"[quarto] render failed (exit {res.returncode})")
    return res.returncode


# ── main ─────────────────────────────────────────────────────────────────────
def main(argv=None):
    ap = argparse.ArgumentParser(description="Build the Mouse2Human article site.")
    ap.add_argument("--docx", default=DEFAULT_DOCX, help="manuscript .docx path")
    ap.add_argument("--out", default="docs", help="output directory (default: docs)")
    ap.add_argument("--figures-dir", default="article-figures",
                    help="figures folder name inside --out")
    ap.add_argument("--no-quarto", action="store_true",
                    help="write article.qmd but do not render it with Quarto")
    ap.add_argument("--no-crop", action="store_true",
                    help="keep the original figure images (do not trim white page)")
    args = ap.parse_args(argv)

    docx_path = Path(args.docx)
    if not docx_path.exists():
        sys.exit(f"[error] manuscript not found: {docx_path}")

    out_dir = Path(args.out)
    figures_dir = out_dir / args.figures_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[build] reading  {docx_path}")
    zf, blocks, meta = parse_manuscript(docx_path)

    # extract each figure, writing it with a semantic file name
    written = []
    for blk in blocks:
        if blk.kind == "figure" and blk.fig_media:
            try:
                data = zf.read(blk.fig_media)
            except KeyError:
                continue
            if not args.no_crop:
                data = trim_whitespace(data)
            name = figure_filename(blk.fig_kind, blk.fig_num)
            (figures_dir / name).write_bytes(data)
            written.append(name)
    print(f"[build] figures  {len(written)} → {figures_dir}")

    body_html, toc = render_body(blocks, args.figures_dir, meta)
    toc_html = render_toc(toc)
    refs_html = render_refs(meta["refs"])
    top_cta = (
        '    <div class="explore-cta">\n'
        '      <span class="explore-cta-label">New &middot; immersive edition</span>\n'
        '      <a class="btn" href="article-explore.html">Explore the data &rarr;</a>\n'
        '    </div>'
    )
    content = top_cta + "\n" + render_header(meta) + "\n" + body_html + "\n" + refs_html

    page = (SHELL
            .replace("__NAV__", NAV)
            .replace("__TOC__", toc_html)
            .replace("__CONTENT__", content)
            .replace("__TITLE__", esc(meta["title"]))
            .replace("__DESC__", esc(meta["title"]))
            .replace("__BIBTEX__", esc(build_bibtex(meta))))

    out_file = out_dir / "article.html"
    out_file.write_text(page, encoding="utf-8")
    print(f"[build] written  {out_file}")

    # ── Quarto edition ─────────────────────────────────────────────────────
    qmd_text = render_qmd(blocks, meta, args.figures_dir)
    qmd_file = out_dir / "article.qmd"
    qmd_file.write_text(qmd_text, encoding="utf-8")
    print(f"[build] written  {qmd_file}")
    if not args.no_quarto:
        run_quarto(qmd_file)

    print(f"[build] sections {len(toc)} · references {len(meta['refs'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
