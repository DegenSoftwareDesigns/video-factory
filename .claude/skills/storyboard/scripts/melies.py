#!/usr/bin/env python3
"""Look up shots in the Melies Cinematic Techniques library (https://melies.co/cinematic-techniques).

Usage:
  melies.py categories                 # category slugs and names
  melies.py list <category>            # techniques in one category
  melies.py search <text> [<text>...]  # find techniques by name across all categories
  melies.py shot <category>/<slug> [--prompt]
                                       # JSON with name, url, definition and preview media;
                                       # --prompt adds the reusable generation prompt

The technique index is cached for 7 days in ../.cache/index.json. Technique pages are fetched
on demand and never stored: the storyboard links to Melies media instead of copying it.
"""
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://melies.co/cinematic-techniques"
CACHE = Path(__file__).resolve().parent.parent / ".cache" / "index.json"
CACHE_TTL = 7 * 24 * 3600
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
SKIP_CATEGORIES = {"bookmarked"}


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def text(fragment):
    fragment = re.sub(r"<!--.*?-->", "", fragment, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def categories():
    page = fetch(BASE)
    slugs = sorted(set(re.findall(r'href="/cinematic-techniques/([a-z0-9-]+)"', page)) - SKIP_CATEGORIES)
    return slugs


def list_category(category):
    page = fetch(f"{BASE}/{category}")
    pattern = rf'<a href="/cinematic-techniques/{re.escape(category)}/([a-z0-9-]+)"[^>]*class="cinematic-lib__shot"[^>]*>(.*?)</a>'
    seen, shots = set(), []
    for slug, name in re.findall(pattern, page, flags=re.S):
        if slug not in seen:
            seen.add(slug)
            shots.append({"category": category, "slug": slug, "name": text(name)})
    return shots


def load_index():
    if CACHE.exists() and time.time() - CACHE.stat().st_mtime < CACHE_TTL:
        return json.loads(CACHE.read_text(encoding="utf-8"))
    index = []
    for category in categories():
        index.extend(list_category(category))
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    return index


def shot(ref, with_prompt=False):
    category, slug = ref.strip("/").split("/", 1)
    url = f"{BASE}/{category}/{slug}"
    page = fetch(url)

    info = {"category": category, "slug": slug, "url": url, "name": slug.replace("-", " ").title()}
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, flags=re.S):
        try:
            data = json.loads(block)
        except json.JSONDecodeError:
            continue
        for item in data if isinstance(data, list) else [data]:
            if item.get("@type") == "DefinedTerm":
                info["name"] = item.get("name", info["name"])
                info["definition"] = item.get("description", "")

    # The technique's own preview is the first video in the shot header; later videos are related shots.
    own = re.search(r'<video[^>]*class="cinematic-shot__[^"]*"[^>]*>', page) or re.search(r"<video[^>]*>", page)
    if own:
        src = re.search(r'src="([^"]+)"', own.group(0))
        info["preview"] = src.group(1) if src else None
    still = re.search(rf'https://asset\.melies\.co/cinematic-techniques/still/{re.escape(slug)}/hero\.[a-z]+', page)
    info["still"] = still.group(0) if still else None
    strip = re.search(r'https://asset\.melies\.co/cinematic-techniques/strips/[^"\s]+', page)
    info["strip"] = strip.group(0) if strip else None
    # The page also embeds the whole library nav, so only read links inside "Related techniques".
    related_at = page.find("Related techniques")
    related = re.findall(r'href="/cinematic-techniques/([a-z0-9-]+/[a-z0-9-]+)"', page[related_at:related_at + 6000]) if related_at >= 0 else []
    info["related"] = list(dict.fromkeys(r for r in related if r != f"{category}/{slug}"))

    if with_prompt:
        # Template with a [Subject] placeholder: the base for our own generation prompts.
        section = re.search(r"Prompt it\s*</h2>(.*?)<div class=\"cinematic-prompt\"", page, flags=re.S)
        if section:
            paragraphs = [text(p) for p in re.findall(r"<p[^>]*>(.*?)</p>", section.group(1), flags=re.S)]
            info["prompt_template"] = " ".join(p for p in paragraphs if p)
        # Worked example Melies preloads into its generator (a concrete scene using the technique).
        link = re.search(r'href="/ai-video-generator\?prompt=([^"&]+)', page)
        if link:
            info["example_prompt"] = urllib.parse.unquote_plus(html.unescape(link.group(1)))
    return info


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 1
    cmd, args = argv[1], argv[2:]
    if cmd == "categories":
        for slug in categories():
            print(slug)
    elif cmd == "list" and args:
        for s in list_category(args[0]):
            print(f"{s['category']}/{s['slug']}\t{s['name']}")
    elif cmd == "search" and args:
        terms = [t.lower() for t in args]
        for s in load_index():
            hay = f"{s['name']} {s['slug']} {s['category']}".lower()
            if all(t in hay for t in terms):
                print(f"{s['category']}/{s['slug']}\t{s['name']}")
    elif cmd == "index":
        print(json.dumps(load_index(), ensure_ascii=False))
    elif cmd == "shot" and args:
        print(json.dumps(shot(args[0], "--prompt" in args), ensure_ascii=False, indent=2))
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
