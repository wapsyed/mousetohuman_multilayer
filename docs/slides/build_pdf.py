#!/usr/bin/env python3
"""Render an HTML deck or poster to PDF with headless Chrome.

Reveal.js decks are printed in `?print-pdf` mode (one slide per page).
Chrome sometimes emits a stray page that contains nothing but the footer —
those pages are dropped automatically.

    python build_pdf.py <input.html> <output.pdf> [--footer "text"] [--plain]

--footer  footer string used to recognise stray pages (decks)
--plain   do not append `?print-pdf` (posters / single-page documents)
"""
from __future__ import annotations

import argparse
import pathlib
import re
import shutil
import subprocess
import tempfile

CHROME = "google-chrome"


def text_of(pdf: pathlib.Path) -> str:
    try:
        return subprocess.run(["pdftotext", "-layout", str(pdf), "-"],
                              capture_output=True, text=True, check=True).stdout
    except Exception:
        return ""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("out")
    ap.add_argument("--footer", default="")
    ap.add_argument("--plain", action="store_true")
    a = ap.parse_args()

    html = pathlib.Path(a.html).resolve()
    out = pathlib.Path(a.out).resolve()
    url = html.as_uri() + ("" if a.plain else "?print-pdf")

    tmp = pathlib.Path(tempfile.mkdtemp(prefix="pdf-"))
    raw = tmp / "raw.pdf"
    profile = tmp / "chrome"
    profile.mkdir()
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                    f"--user-data-dir={profile}",
                    "--no-pdf-header-footer", "--virtual-time-budget=15000",
                    f"--print-to-pdf={raw}", url],
                   capture_output=True, check=True)

    subprocess.run(["pdfseparate", str(raw), str(tmp / "pg-%03d.pdf")], check=True)
    pages = sorted(tmp.glob("pg-*.pdf"))

    keep = []
    for pg in pages:
        body = re.sub(r"\s+", " ", text_of(pg)).strip()
        if not body:
            continue
        if a.footer:
            stripped = body.replace(re.sub(r"\s+", " ", a.footer).strip(), "")
            stripped = re.sub(r"[\s·/\d]+", "", stripped)
            if not stripped:
                continue                      # footer-only page
        keep.append(str(pg))

    if not keep:
        keep = [str(p) for p in pages]
    subprocess.run(["pdfunite", *keep, str(out)], check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"{out.name}: {len(keep)} pages")


if __name__ == "__main__":
    main()
