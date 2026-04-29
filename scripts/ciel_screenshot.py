#!/usr/bin/env python3
"""Robi screenshot strony CIEL i zapisuje do ~/.claude/ciel_site/screenshot.png

Użycie:
  python3 scripts/ciel_screenshot.py                    # domyślna strona CIEL
  python3 scripts/ciel_screenshot.py file:///path.html  # własny URL
  python3 scripts/ciel_screenshot.py <url> <out.png>    # własny URL i output

Wymaga: playwright + chromium
  pip install playwright
  playwright install chromium --with-deps
"""
import sys
from pathlib import Path


def screenshot(url_or_path: str = None, out: str = None) -> str:
    from playwright.sync_api import sync_playwright

    site = Path.home() / ".claude/ciel_site/index.html"
    target = url_or_path or f"file://{site}"
    output = Path(out) if out else site.parent / "screenshot.png"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        page.goto(target, wait_until="networkidle")
        page.screenshot(path=str(output), full_page=True)
        browser.close()

    print(f"Screenshot: {output}")
    return str(output)


if __name__ == "__main__":
    args = sys.argv[1:]
    screenshot(*args[:2])
