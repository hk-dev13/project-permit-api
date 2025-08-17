from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Tuple

import requests
from bs4 import BeautifulSoup  # type: ignore

CATALOG_URL = "https://www.eea.europa.eu/code/api/data/daviz.json"


def looks_like_url(val: Any) -> bool:
    return isinstance(val, str) and val.startswith(("http://", "https://"))


def extract_url_fields(item: Dict[str, Any]) -> List[Tuple[str, str]]:
    urls: List[Tuple[str, str]] = []
    for k, v in item.items():
        if looks_like_url(v):
            urls.append((k, v))
    return urls


def find_download_links(landing_url: str) -> List[str]:
    links: List[str] = []
    try:
        landing_url = landing_url.replace("http://", "https://")
        resp = requests.get(landing_url, timeout=30)
        if resp.status_code != 200:
            return links
        soup = BeautifulSoup(resp.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if not href:
                continue
            if href.startswith("/"):
                # make absolute
                m = re.match(r"^(https?://[^/]+)", landing_url)
                base = m.group(1) if m else ""
                href = base.rstrip("/") + href
            # heuristics: csv/json/zip or download endpoints typical in EEA (Plone)
            if any(href.lower().endswith(ext) for ext in (".csv", ".json", ".zip", ".xlsx")) or "download" in href.lower() or "@@download" in href:
                links.append(href)
        # also scan script tags for embedded URLs
        for script in soup.find_all("script"):
            txt = script.string or script.text or ""
            if not txt:
                continue
            if any(marker in txt.lower() for marker in ("download", ".csv", ".json", ".xlsx")):
                for m in re.finditer(r"https?://[^\s'\"]+", txt):
                    url = m.group(0)
                    if any(url.lower().endswith(ext) for ext in (".csv", ".json", ".zip", ".xlsx")) or "download" in url.lower() or "@@download" in url:
                        links.append(url)
    except Exception:
        pass
    # de-dup while preserving order
    seen = set()
    uniq: List[str] = []
    for l in links:
        if l not in seen:
            uniq.append(l)
            seen.add(l)
    return uniq[:10]


def main() -> None:
    print(f"Fetching catalog: {CATALOG_URL}")
    r = requests.get(CATALOG_URL, timeout=60)
    r.raise_for_status()
    data = r.json()
    keys = list(data.keys())
    items = data.get("items", []) if isinstance(data, dict) else []
    print(f"Top-level keys: {keys}")
    print(f"Items count: {len(items)}")

    if not items:
        return

    # Inspect first item structure
    sample = items[0]
    print("\n--- Sample item keys ---")
    print(sorted(sample.keys()))

    print("\n--- Sample item URL-like fields ---")
    print(extract_url_fields(sample))

    # Scan first 20 items for URL-looking fields and flag potential data links
    print("\n--- First 20 items: potential URLs ---")
    for i, it in enumerate(items[:20]):
        title = it.get("title") or it.get("name") or "(no title)"
        urls = extract_url_fields(it)
        if not urls:
            continue
        csvish = [u for k, u in urls if any(u.lower().endswith(ext) for ext in (".csv", ".json", ".zip", ".xlsx"))]
        print(f"[{i}] {title}")
        for k, u in urls:
            print(f"    {k}: {u}")
        if csvish:
            print(f"    -> data-like: {csvish}")

    # Follow landing pages of first 30 items to discover download links
    print("\n--- Following landing pages (first 30 items) for download links ---")
    for i, it in enumerate(items[:30]):
        landing = it.get("uri") or it.get("@id") or it.get("url")
        if not looks_like_url(landing):
            continue
        title = it.get("title") or "(no title)"
        links = find_download_links(str(landing))
        print(f"[{i}] {title}")
        print(f"    {landing}")
        for l in links[:10]:
            print(f"    link: {l}")


if __name__ == "__main__":
    main()
