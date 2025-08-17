from __future__ import annotations

import re
import sys
from typing import List

import requests
from bs4 import BeautifulSoup  # type: ignore


def find_download_links(landing_url: str) -> List[str]:
    links: List[str] = []
    try:
        resp = requests.get(landing_url, timeout=30)
        print(f"STATUS {resp.status_code} for {landing_url}")
        if resp.status_code != 200:
            return links
        soup = BeautifulSoup(resp.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if not href:
                continue
            if href.startswith("/"):
                m = re.match(r"^(https?://[^/]+)", landing_url)
                base = m.group(1) if m else ""
                href = base.rstrip("/") + href
            if any(href.lower().endswith(ext) for ext in (".csv", ".json", ".zip", ".xlsx")) or "download" in href.lower() or "@@download" in href:
                links.append(href)
    except Exception as e:
        print(f"ERROR: {e}")
    # de-dup
    seen = set()
    uniq: List[str] = []
    for l in links:
        if l not in seen:
            uniq.append(l)
            seen.add(l)
    return uniq


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/probe_page.py <URL>")
        sys.exit(1)
    url = sys.argv[1]
    links = find_download_links(url)
    print("Found links:")
    for l in links:
        print(l)


if __name__ == "__main__":
    main()
