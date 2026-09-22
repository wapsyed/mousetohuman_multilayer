#!/usr/bin/env python3
"""Build an editable PowerPoint (.pptx) from the reveal.js deck.

The Quarto/pandoc `--to pptx` route drops every figure and splits some
slides, so this script reads the *rendered* deck HTML
(`from-mice-to-humans-lab-meeting-quarto.html`) and rebuilds it as real,
editable PowerPoint objects: text boxes (not pictures of slides), the
manuscript figures as pictures, the paper palette and the speaker notes.

    python build_pptx.py

Edit the deck in `from-mice-to-humans-lab-meeting.qmd`, re-render the HTML
with `quarto render from-mice-to-humans-lab-meeting.qmd`, then run this
script again — the text and figures are re-read from the HTML; only the
geometry below is fixed in code.
"""
from __future__ import annotations

import math
import pathlib
import re

from bs4 import BeautifulSoup, NavigableString, Tag
from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

HERE = pathlib.Path(__file__).parent
HTML = HERE / "from-mice-to-humans-lab-meeting-quarto.html"
OUT = HERE / "from-mice-to-humans-lab-meeting.pptx"

# ── paper palette ───────────────────────────────────────────────────────────
INK, BODY, MUTED = "000000", "1B2130", "5B6377"
CYAN, BLUE, PERI, RULE, BG = "4DBBD5", "4361EE", "A1B0F7", "D9DEEC", "FBFBFD"

SERIF, SANS, MONO = "Merriweather", "Arial", "Arial"

FOOTER = "Mouse2Human · Lab meeting · September 2026 · Genes and Immunity (under review)"

# ── geometry (inches) ───────────────────────────────────────────────────────
SW, SH = 13.333, 7.5
MX = 0.62                      # left/right margin
CW = SW - 2 * MX               # content width
COLW = (CW - 0.55) / 2         # column width
RX = MX + COLW + 0.55          # right column x
KICK_Y = 0.52                  # kicker baseline
HEAD_Y = 0.98                  # headline top
BODY_Y = 1.05                  # body top when there is no headline
FOOT_Y = 7.06


# ─────────────────────────────────────────────────────────────────────────────
# parsing
# ─────────────────────────────────────────────────────────────────────────────
def _normalise(soup: BeautifulSoup) -> None:
    """Pandoc writes `<p class="cap">` as an empty marker followed by the real
    paragraph, so fold the following paragraph into any empty classed one."""
    for p in soup.find_all("p"):
        attrs = getattr(p, "attrs", None)
        if not attrs or not attrs.get("class"):
            continue
        if p.find(["img", "br"]):
            continue
        if p.get_text(strip=True):
            continue
        nxt = p.find_next_sibling()
        while (nxt is not None and nxt.name == "p" and not nxt.get("class")
               and not nxt.get_text(strip=True) and not nxt.find("img")):
            nxt = nxt.find_next_sibling()
        if nxt is not None and nxt.name == "p" and not nxt.get("class"):
            for child in list(nxt.children):
                p.append(child.extract())
            nxt.decompose()


def runs_of(el: Tag) -> list[dict]:
    """Flatten an element into inline runs, keeping bold/italic/mono."""
    out: list[dict] = []

    def walk(node, bold=False, italic=False, mono=False):
        for ch in node.children:
            if isinstance(ch, NavigableString):
                text = re.sub(r"\s+", " ", str(ch))
                if text:
                    out.append({"t": text, "bold": bold, "italic": italic, "mono": mono})
            elif isinstance(ch, Tag):
                if ch.name in ("strong", "b"):
                    walk(ch, True, italic, mono)
                elif ch.name in ("em", "i"):
                    walk(ch, bold, True, mono)
                elif ch.name in ("code",) or ("mono" in (ch.get("class") or [])):
                    walk(ch, bold, italic, True)
                elif ch.name == "br":
                    out.append({"t": "\n", "bold": bold, "italic": italic, "mono": mono})
                else:
                    walk(ch, bold, italic, mono)

    walk(el)
    while out and not out[0]["t"].strip():
        out.pop(0)
    while out and not out[-1]["t"].strip():
        out.pop()
    if out:
        out[0]["t"] = out[0]["t"].lstrip()
        out[-1]["t"] = out[-1]["t"].rstrip()
    return out


def plain(el: Tag) -> str:
    return re.sub(r"\s+", " ", el.get_text(" ", strip=True))


def block_of(el: Tag) -> dict | None:
    cls = set(el.get("class") or [])
    if el.name == "p":
        txt = plain(el)
        if not txt:
            return None
        return {"type": "para", "runs": runs_of(el), "cls": cls}
    if el.name == "ul":
        items = []
        for li in el.find_all("li", recursive=False):
            sub = li.find("ul")
            subs = [plain(x) for x in sub.find_all("li", recursive=False)] if sub else []
            runs: list[dict] = []
            for ch in li.children:
                if isinstance(ch, Tag) and ch.name == "ul":
                    continue
                if isinstance(ch, Tag):
                    runs += runs_of(ch)
                elif isinstance(ch, NavigableString) and str(ch).strip():
                    runs.append({"t": re.sub(r"\s+", " ", str(ch)),
                                 "bold": False, "italic": False, "mono": False})
            items.append({"runs": runs, "sub": subs})
        return {"type": "ul", "items": items}
    if el.name == "div":
        if "head" in cls:
            return {"type": "head", "runs": runs_of(el)}
        if "stats" in cls:
            stats = []
            for st in el.find_all("div", class_="stat", recursive=False):
                num = st.find("span", class_="num")
                lab = st.find("span", class_="lab")
                stats.append({
                    "num": plain(num) if num else "",
                    "ink": num is not None and "ink" in (num.get("class") or []),
                    "lab": plain(lab) if lab else "",
                })
            return {"type": "stats", "stats": stats,
                    "stack": "column" in (el.get("style") or "")}
        if "panel" in cls:
            big = el.find("p", class_="big")
            ptitle = el.find("p", class_="ptitle")
            body, bullets = [], []
            for ch in el.find_all(recursive=False):
                c = set(ch.get("class") or [])
                if ch.name == "ul":
                    bullets = [plain(li) for li in ch.find_all("li", recursive=False)]
                elif ch.name == "p" and "ptitle" not in c and "big" not in c and plain(ch):
                    body.append(plain(ch))
            return {"type": "panel", "title": plain(ptitle) if ptitle else "",
                    "big": plain(big) if big else "", "strong": "strong" in cls,
                    "body": body, "bullets": bullets}
        if "fig" in cls:
            img = el.find("img")
            cap = el.find("p", class_="cap")
            return {"type": "fig",
                    "src": (img.get("data-src") or img.get("src")) if img else None,
                    "cap": plain(cap) if cap else ""}
        if "card" in cls:
            idx = el.find("span", class_="idx")
            ctitle = el.find("p", class_="ctitle")
            url = el.find("span", class_="url")
            body = [plain(p) for p in el.find_all("p", recursive=False)
                    if "ctitle" not in (p.get("class") or []) and plain(p)]
            return {"type": "card", "idx": plain(idx) if idx else "",
                    "title": plain(ctitle) if ctitle else "", "body": body,
                    "url": plain(url) if url else ""}
    return None


def blocks_of(container: Tag) -> list[dict]:
    out = []
    for el in container.find_all(recursive=False):
        if isinstance(el, Tag):
            b = block_of(el)
            if b:
                out.append(b)
    return out


def parse() -> list[dict]:
    soup = BeautifulSoup(HTML.read_text(encoding="utf-8"), "lxml")
    _normalise(soup)
    slides = []
    for sec in soup.select(".reveal .slides > section"):
        h2 = sec.find("h2")
        notes = sec.find("aside", class_="notes")
        if notes:
            for bad in notes.find_all(["style", "script"]):
                bad.decompose()
        slide = {
            "cls": set(sec.get("class") or []),
            "kicker": plain(h2) if h2 else "",
            "title": plain(h2) if h2 else "",
            "notes": plain(notes) if notes else "",
            "blocks": [],
            "columns": None,
        }
        for el in sec.find_all(recursive=False):
            if not isinstance(el, Tag) or el.name == "h2":
                continue
            cls = set(el.get("class") or [])
            if "notes" in cls:
                continue
            if el.name == "div" and "columns" in cls:
                cols = [blocks_of(c) for c in el.find_all("div", class_="column", recursive=False)]
                slide["columns"] = cols
            else:
                b = block_of(el)
                if b:
                    slide["blocks"].append(b)
        slides.append(slide)
    return slides


# ─────────────────────────────────────────────────────────────────────────────
# drawing helpers
# ─────────────────────────────────────────────────────────────────────────────
def box(slide, x, y, w, h):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    return tb, tf


def para(tf, first=False, align=PP_ALIGN.LEFT, spacing=1.12, after=0, before=0):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align
    p.line_spacing = spacing
    p.space_after = Pt(after)
    p.space_before = Pt(before)
    return p


def put(p, text, size=12, font=SANS, color=BODY, bold=False, italic=False, spc=None):
    r = p.add_run()
    r.text = text
    r.font.name = font
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.color.rgb = RGBColor.from_string(color)
    if spc is not None:                     # letter-spacing (kickers/labels)
        r.font._rPr.set("spc", str(int(spc * 100)))
    return r


def put_runs(p, runs, size=12, font=SANS, color=BODY, mono_size=None, mono_color=MUTED):
    for rr in runs:
        mono = rr.get("mono")
        put(p, rr["t"], size=(mono_size or size - 1) if mono else size,
            font=MONO if mono else font,
            color=mono_color if mono and not rr.get("bold") else color,
            bold=rr.get("bold"), italic=rr.get("italic"))


def est_lines(text: str, w: float, size: float, mono=False) -> int:
    cpl = max(8, int(w * 72 / (size * (0.68 if mono else 0.56))))
    return max(1, math.ceil(len(text) / cpl))


def bar(slide, x, y, w=0.10, h=0.055):
    """Three-segment gradient rule used as the deck's signature."""
    for i, col in enumerate((CYAN, BLUE, PERI)):
        s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x + i * w), Inches(y),
                                   Inches(w), Inches(h))
        s.fill.solid()
        s.fill.fore_color.rgb = RGBColor.from_string(col)
        s.line.fill.background()
        s.shadow.inherit = False


def hline(slide, x, y, w, color=INK, h=0.022):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = RGBColor.from_string(color)
    s.line.fill.background()
    s.shadow.inherit = False


def picture(slide, src, x, y, max_w, max_h):
    path = HERE / src
    with Image.open(path) as im:
        iw, ih = im.size
    ratio = iw / ih
    w = max_w
    h = w / ratio
    if h > max_h:
        h = max_h
        w = h * ratio
    left = x + (max_w - w) / 2
    slide.shapes.add_picture(str(path), Inches(left), Inches(y), Inches(w), Inches(h))
    return y + h


def chrome(slide, n, total):
    bar(slide, MX, 0.34)
    tb, tf = box(slide, MX, FOOT_Y, CW - 0.9, 0.3)
    p = para(tf, first=True, spacing=1.0)
    put(p, FOOTER, size=8.5, font=MONO, color=MUTED, spc=1.4)
    tb, tf = box(slide, MX + CW - 0.9, FOOT_Y, 0.9, 0.3)
    p = para(tf, first=True, align=PP_ALIGN.RIGHT, spacing=1.0)
    put(p, f"{n} / {total}", size=8.5, font=MONO, color=MUTED, spc=1.4)


def kicker(slide, text):
    tb, tf = box(slide, MX, KICK_Y, CW, 0.3)
    p = para(tf, first=True, spacing=1.0)
    put(p, text.upper(), size=10, font=MONO, color=MUTED, spc=1.6)


# ─────────────────────────────────────────────────────────────────────────────
# block renderers — each returns the y after the block
# ─────────────────────────────────────────────────────────────────────────────
def r_head(slide, b, x, y, w, size=25):
    txt = "".join(r["t"] for r in b["runs"])
    tb, tf = box(slide, x, y, w, 0.1)
    p = para(tf, first=True, spacing=1.06)
    for rr in b["runs"]:
        put(p, rr["t"], size=size, font=SERIF, color=INK,
            italic=rr.get("italic"), bold=rr.get("bold"))
    lines = est_lines(txt, w, size)
    return y + lines * size * 1.06 / 72 + 0.20


def r_para(slide, b, x, y, w, size=12, font=SANS, color=BODY, italic=False):
    runs = b["runs"]
    txt = "".join(r["t"] for r in runs)
    tb, tf = box(slide, x, y, w, 0.1)
    p = para(tf, first=True, spacing=1.22)
    for rr in runs:
        mono = rr.get("mono")
        put(p, rr["t"], size=(size - 1) if mono else size,
            font=MONO if mono else font,
            color=(MUTED if mono and not rr.get("bold") else color),
            bold=rr.get("bold"), italic=rr.get("italic") or italic)
    return y + est_lines(txt, w, size) * size * 1.22 / 72 + 0.13


def r_ul(slide, b, x, y, w, size=12, color=BODY):
    tb, tf = box(slide, x, y, w, 0.1)
    first = True
    for it in b["items"]:
        p = para(tf, first=first, spacing=1.2, after=5)
        first = False
        put(p, "•  ", size=size, font=SANS, color=PERI, bold=True)
        put_runs(p, it["runs"], size=size, color=color)
        for sub in it["sub"]:
            sp = para(tf, spacing=1.2, after=4)
            put(sp, "–  ", size=size - 1, font=SANS, color=PERI)
            put(sp, sub, size=size - 1, font=SANS, color=color)
    lines = sum(est_lines("".join(r["t"] for r in it["runs"]), w - 0.25, size) + len(it["sub"])
                for it in b["items"])
    return y + lines * size * 1.2 / 72 + (len(b["items"]) * 5 + 4) / 72 + 0.10


def r_stats(slide, b, x, y, w, big=False, stack=False):
    n = len(b["stats"])
    if stack:
        cy = y
        for st in b["stats"]:
            tb, tf = box(slide, x, cy, w, 0.1)
            p = para(tf, first=True, spacing=1.0)
            put(p, st["num"], size=40 if big else 32, font=SERIF,
                color=INK if st["ink"] else BLUE)
            cy += (40 if big else 32) * 1.06 / 72
            tb, tf = box(slide, x, cy, w, 0.1)
            p = para(tf, first=True, spacing=1.3)
            put(p, st["lab"].upper(), size=8.5, font=MONO, color=MUTED, spc=1.2)
            cy += est_lines(st["lab"], w, 8.5, True) * 8.5 * 1.3 / 72 + 0.30
        return cy
    cw = w / n
    cy = y
    for i, st in enumerate(b["stats"]):
        cx = x + i * cw
        tb, tf = box(slide, cx, cy, cw - 0.3, 0.1)
        p = para(tf, first=True, spacing=1.0)
        put(p, st["num"], size=48 if big else 34, font=SERIF,
            color=INK if st["ink"] else BLUE)
        nsize = 48 if big else 34
        tb, tf = box(slide, cx, cy + nsize * 1.04 / 72 + 0.06, cw - 0.3, 0.1)
        p = para(tf, first=True, spacing=1.3)
        put(p, st["lab"].upper(), size=(10 if big else 8.5), font=MONO, color=MUTED, spc=1.2)
    lab_h = max(est_lines(s["lab"], cw - 0.3, 10 if big else 8.5, True) for s in b["stats"])
    return cy + nsize * 1.04 / 72 + 0.06 + lab_h * 10 * 1.3 / 72 + 0.18


def r_panel(slide, b, x, y, w):
    hline(slide, x, y, w, BLUE if b["strong"] else PERI)
    cy = y + 0.14
    if b["title"]:
        tb, tf = box(slide, x, cy, w, 0.1)
        p = para(tf, first=True, spacing=1.0)
        put(p, b["title"].upper(), size=9, font=MONO, color=MUTED, spc=1.4)
        cy += 0.24
    if b["big"]:
        tb, tf = box(slide, x, cy, w, 0.1)
        p = para(tf, first=True, spacing=1.0)
        put(p, b["big"], size=26, font=SERIF,
            color="2E9DB7" if not b["strong"] else BLUE)
        cy += 0.44
    for txt in b["body"]:
        tb, tf = box(slide, x, cy, w, 0.1)
        p = para(tf, first=True, spacing=1.22)
        put(p, txt, size=11.5, font=SANS, color=BODY)
        cy += est_lines(txt, w, 11.5) * 11.5 * 1.22 / 72 + 0.10
    if b["bullets"]:
        tb, tf = box(slide, x, cy, w, 0.1)
        first = True
        for li in b["bullets"]:
            p = para(tf, first=first, spacing=1.2, after=5)
            first = False
            put(p, "•  ", size=11.5, font=SANS, color=PERI, bold=True)
            put(p, li, size=11.5, font=SANS, color=BODY)
        cy += sum(est_lines(li, w - 0.25, 11.5) for li in b["bullets"]) * 11.5 * 1.2 / 72
        cy += (len(b["bullets"]) * 5) / 72
    return cy + 0.12


def r_fig(slide, b, x, y, w, max_h):
    bottom = y
    if b["src"]:
        bottom = picture(slide, b["src"], x, y, w, max_h)
    if b["cap"]:
        tb, tf = box(slide, x, bottom + 0.12, w, 0.1)
        p = para(tf, first=True, spacing=1.35)
        put(p, b["cap"], size=8.5, font=MONO, color=MUTED)
        bottom += 0.12 + est_lines(b["cap"], w, 8.5, True) * 8.5 * 1.35 / 72
    return bottom


def r_card(slide, b, x, y, w, h):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = RGBColor.from_string("FFFFFF")
    s.line.color.rgb = RGBColor.from_string(RULE)
    s.line.width = Pt(0.75)
    s.shadow.inherit = False
    cy = y + 0.22
    pad = 0.20
    tb, tf = box(slide, x + pad, cy, w - 2 * pad, 0.1)
    p = para(tf, first=True, spacing=1.0)
    put(p, b["idx"].upper(), size=9, font=MONO, color=CYAN, spc=1.5)
    cy += 0.30
    tb, tf = box(slide, x + pad, cy, w - 2 * pad, 0.1)
    p = para(tf, first=True, spacing=1.0)
    put(p, b["title"], size=15, font=SERIF, color=INK)
    cy += 0.34
    for txt in b["body"]:
        tb, tf = box(slide, x + pad, cy, w - 2 * pad, 0.1)
        p = para(tf, first=True, spacing=1.25)
        parts = re.split(r"`([^`]+)`", txt)
        for i, part in enumerate(parts):
            if part:
                put(p, part, size=11, font=MONO if i % 2 else SANS,
                    color=BODY)
        cy += est_lines(txt, w - 2 * pad, 11) * 11 * 1.25 / 72 + 0.10
    if b["url"]:
        tb, tf = box(slide, x + pad, y + h - 0.42, w - 2 * pad, 0.3)
        p = para(tf, first=True, spacing=1.15)
        put(p, b["url"], size=9, font=MONO, color=BLUE)


# ─────────────────────────────────────────────────────────────────────────────
# slide layouts
# ─────────────────────────────────────────────────────────────────────────────
def render_title(slide, s):
    tb, tf = box(slide, MX, 1.35, COLW, 0.1)
    p = para(tf, first=True, spacing=1.04)
    put(p, s["title"], size=40, font=SERIF, color=INK)
    left = [b for b in s["blocks"] if b["type"] in ("para",)]
    cy = 2.35
    for b in left:
        cls = b["cls"]
        if "kicker" in cls:
            tb, tf = box(slide, MX, cy, COLW, 0.1)
            p = para(tf, first=True, spacing=1.25)
            put_runs(p, b["runs"], size=16, font=SANS, color=MUTED)
            cy += est_lines(plain_runs(b["runs"]), COLW, 16) * 16 * 1.25 / 72 + 0.30
        elif "byline" in cls:
            tb, tf = box(slide, MX, cy, COLW, 0.1)
            p = para(tf, first=True, spacing=1.35)
            put_runs(p, b["runs"], size=9, font=MONO, color=INK)
            cy += est_lines(plain_runs(b["runs"]), COLW, 9, True) * 9 * 1.35 / 72 + 0.22
        elif "affil" in cls:
            tb, tf = box(slide, MX, cy, COLW, 0.1)
            p = para(tf, first=True, spacing=1.35)
            put_runs(p, b["runs"], size=9, font=MONO, color=MUTED)
            cy += 0.5
    figs = [b for b in s["blocks"] if b["type"] == "fig"]
    if figs and figs[0]["src"]:
        picture(slide, figs[0]["src"], RX, 1.35, COLW, 4.7)


def plain_runs(runs):
    return "".join(r["t"] for r in runs)


def render_columns(slide, s):
    left, right = s["columns"][0], s["columns"][1]
    cy = BODY_Y
    for b in left:
        if b["type"] == "head":
            cy = r_head(slide, b, MX, cy, COLW, size=23)
        elif b["type"] == "para":
            cy = r_para(slide, b, MX, cy, COLW)
        elif b["type"] == "ul":
            cy = r_ul(slide, b, MX, cy, COLW)
        elif b["type"] == "stats":
            cy = r_stats(slide, b, MX, cy, COLW)
        elif b["type"] == "panel":
            cy = r_panel(slide, b, MX, cy, COLW)
    ry = BODY_Y
    for b in right:
        if b["type"] == "fig":
            ry = r_fig(slide, b, RX, BODY_Y, COLW, 4.95)
        elif b["type"] == "para":
            ry = r_para(slide, b, RX, ry, COLW)
        elif b["type"] == "ul":
            ry = r_ul(slide, b, RX, ry, COLW)


def render_panels(slide, s):
    cy = BODY_Y
    for b in s["blocks"]:
        if b["type"] == "head":
            cy = r_head(slide, b, MX, 0.92, CW, size=26)
    cols = s["columns"]
    y0 = cy + 0.05
    bottom = y0
    for i, col in enumerate(cols):
        x = MX + i * (COLW + 0.55)
        cy = y0
        for b in col:
            if b["type"] == "panel":
                cy = r_panel(slide, b, x, cy, COLW)
            elif b["type"] == "para":
                cy = r_para(slide, b, x, cy, COLW)
        bottom = max(bottom, cy)
    for b in s["blocks"]:
        if b["type"] == "para":
            tb, tf = box(slide, MX, bottom + 0.12, CW, 0.1)
            p = para(tf, first=True, spacing=1.25)
            put_runs(p, b["runs"], size=11, font=MONO, color=MUTED)


def render_full(slide, s):
    cy = BODY_Y
    for b in s["blocks"]:
        if b["type"] == "head":
            cy = r_head(slide, b, MX, 0.92, CW, size=26)
        elif b["type"] == "para":
            cy = r_para(slide, b, MX, cy, CW)
        elif b["type"] == "ul":
            cy = r_ul(slide, b, MX, cy, CW)
        elif b["type"] == "stats":
            cy = r_stats(slide, b, MX, cy, CW, big="bigstats" in s["cls"])
    if "columns" in s and s["columns"] is None:
        return
    if s["columns"]:
        for i, col in enumerate(s["columns"]):
            x = MX + i * (COLW + 0.55)
            ccy = cy + 0.10
            for b in col:
                if b["type"] == "panel":
                    ccy = r_panel(slide, b, x, ccy, COLW)
                elif b["type"] == "ul":
                    ccy = r_ul(slide, b, x, ccy, COLW)
                elif b["type"] == "para":
                    ccy = r_para(slide, b, x, ccy, COLW)


def render_cards(slide, s):
    cy = BODY_Y
    for b in s["blocks"]:
        if b["type"] == "head":
            cy = r_head(slide, b, MX, 0.92, CW, size=26)
    cards = []
    for col in (s["columns"] or []):
        cards += [b for b in col if b["type"] == "card"]
    if cards:
        gap = 0.30
        w = (CW - gap * (len(cards) - 1)) / len(cards)
        ch = 3.1
        for i, c in enumerate(cards):
            r_card(slide, c, MX + i * (w + gap), cy + 0.15, w, ch)
    for b in s["blocks"]:
        if b["type"] == "para" and "thanks" in b["cls"]:
            tb, tf = box(slide, MX, cy + 0.15 + 3.1 + 0.55, CW, 0.6)
            p = para(tf, first=True, spacing=1.0)
            put_runs(p, b["runs"], size=21, font=SERIF, color=INK)


# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    slides = parse()
    total = len(slides)

    prs = Presentation()
    prs.slide_width = Inches(SW)
    prs.slide_height = Inches(SH)
    blank = prs.slide_layouts[6]

    for i, s in enumerate(slides, 1):
        slide = prs.slides.add_slide(blank)
        try:
            slide.background.fill.solid()
            slide.background.fill.fore_color.rgb = RGBColor.from_string(BG)
        except Exception:
            pass
        chrome(slide, i, total)

        if "titleslide" in s["cls"]:
            render_title(slide, s)
        elif any(b["type"] == "card" for col in (s["columns"] or []) for b in col):
            render_cards(slide, s)
        elif s["columns"] and any(b["type"] == "fig" for col in s["columns"] for b in col):
            kicker(slide, s["kicker"])
            render_columns(slide, s)
        elif s["columns"]:
            kicker(slide, s["kicker"])
            render_panels(slide, s)
        else:
            kicker(slide, s["kicker"])
            render_full(slide, s)

        if s["notes"]:
            slide.notes_slide.notes_text_frame.text = s["notes"]

    prs.core_properties.title = "From mice to humans — project overview"
    prs.core_properties.author = "Wasim Aluísio Prates-Syed · Cabral-Miranda Lab"
    prs.core_properties.subject = ("Multi-omic predictive framework for translational "
                                   "immunology — lab meeting")
    prs.core_properties.comments = ("Editable PowerPoint built from the deck "
                                    "(build_pptx.py).")
    prs.save(OUT)
    print(f"wrote {OUT.name}: {total} slides")


if __name__ == "__main__":
    main()
