import sys
import json
import requests


CKAN_API = "https://sdi.eea.europa.eu/catalogue/api/3/action/package_search"


def search_ckan(query: str, rows: int = 10):
    try:
        r = requests.get(CKAN_API, params={"q": query, "rows": rows}, timeout=30)
        r.raise_for_status()
        data = r.json()
        return data.get("result", {}).get("results", [])
    except Exception as e:
        print(f"ERR search '{query}': {e}")
        return []


def main():
    queries = [
        "air emission",  # generic
        "NEC emissions",  # National Emission Ceilings
        "CLRTAP emission",  # UNECE convention inventory
        "greenhouse gas country",  # GHG
        "emission inventory",
    ]
    if len(sys.argv) > 1:
        queries = [" ".join(sys.argv[1:])]

    for q in queries:
        print("\n=== Query:", q, "===")
        results = search_ckan(q, rows=15)
        if not results:
            print("No results")
            continue
        for pkg in results:
            title = pkg.get("title") or pkg.get("name")
            name = pkg.get("name")
            org = (pkg.get("organization") or {}).get("title") or ""
            print(f"- {title} [{name}] :: {org}")
            resources = pkg.get("resources", [])
            for res in resources:
                fmt = (res.get("format") or res.get("mimetype") or "").upper()
                url = res.get("url") or ""
                if not url:
                    continue
                # Filter to likely direct downloads or API endpoints we can consume
                if any(url.lower().endswith(ext) for ext in (".csv", ".json")) or \
                   "datastore" in url.lower() or "download" in url.lower():
                    name = res.get("name") or res.get("id")
                    print(f"    * [{fmt}] {name}: {url}")


if __name__ == "__main__":
    main()
