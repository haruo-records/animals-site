#!/usr/bin/env python3
"""
animals の作品を、検索エンジンや SNS から見える静的ページとして書き出す。

入力:
  animals/test-tube/index.json      organize_animals.py の出力（作品一覧）
  animals/test-tube/overrides.json  手書きの補足（別名 aka / 画像説明 alt / 一文 note）

出力:
  works/index.html                  全作品の一覧（年代順）
  works/<slug>/index.html           作品ごとのページ（画像・alt・OGP・構造化データ）
  sitemap.xml                       画像付きサイトマップ

使い方（リポジトリ直下で）:
  python3 tools/build_static.py

新作を追加したら organize_animals.py の後にこれを実行して、まとめてコミットする。
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://haruo-records.github.io/animals-site/"
TT = ROOT / "animals" / "test-tube"
OUT = ROOT / "works"
GTM_ID = "GTM-54F4NP2W"
SITE_DESC_JA = "HARUO（1998年〜）による創作生物のアーカイブ「animals」"

# サイトマップに載せる既存ページ（works 以外）
STATIC_PAGES = [
    ("", "monthly", "1.0"),
    ("archive/", "weekly", "0.9"),
    ("works/", "weekly", "0.9"),
    ("phantom-graph/", "monthly", "0.6"),
    ("slow-watching/", "monthly", "0.6"),
    ("profile/", "monthly", "0.6"),
    ("support/", "monthly", "0.5"),
]

esc = lambda s: html.escape(str(s), quote=True)


def url_slug(slug: str) -> str:
    """URL 用: 小文字・英数とハイフンのみ（GitHub Pages は大文字小文字を区別するため統一）"""
    s = re.sub(r"[^a-z0-9]+", "-", slug.lower()).strip("-")
    return s or "untitled"


def load_works():
    items = json.loads((TT / "index.json").read_text(encoding="utf-8"))
    ov_path = TT / "overrides.json"
    overrides = json.loads(ov_path.read_text(encoding="utf-8")) if ov_path.exists() else {}
    works = []
    for it in items:
        slug = it["slug"]
        folder = it.get("folder") or f"items/{slug}"
        ov = overrides.get(slug, {})
        works.append({
            "slug": slug,
            "path": url_slug(slug),
            "title": it.get("title") or slug,
            "aka": ov.get("aka", ""),
            "alt": ov.get("alt", ""),
            "note": ov.get("note", ""),
            "date": it.get("date", ""),
            "year": it.get("year", ""),
            "tags": it.get("tags") or {},
            "images": [f"animals/test-tube/{folder}/{f}" for f in it.get("sourceFiles", [])],
        })
    works.sort(key=lambda w: (w["date"], w["title"].lower()))
    paths = [w["path"] for w in works]
    dupes = {p for p in paths if paths.count(p) > 1}
    if dupes:
        raise SystemExit(f"URL slug が重複しています: {sorted(dupes)}")
    return works


def display_name(w):
    return f'{w["title"]} ({w["aka"]})' if w["aka"] else w["title"]


def tag_phrase(w):
    t = w["tags"]
    return ", ".join(v for v in (t.get("form"), t.get("motion"), t.get("state")) if v)


def alt_text(w, i, n):
    if w["alt"]:
        base = w["alt"]
    else:
        tp = tag_phrase(w)
        base = f'{display_name(w)} — a hand-drawn creature from animals by HARUO, {w["year"]}'
        if tp:
            base += f" ({tp})"
    return f"{base} [{i}/{n}]" if n > 1 else base


def description(w):
    lead = w["note"] or f'{display_name(w)} — a speculative organism observed in {w["date"]}.'
    return f"{lead} From animals, field notes on unknown forms by HARUO. {SITE_DESC_JA}より。"


def head(title, desc, canonical, og_image, depth, og_type="website", extra=""):
    up = "../" * depth
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <!-- Google Tag Manager -->
  <script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':
  new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],
  j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
  'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
  }})(window,document,'script','dataLayer','{GTM_ID}');</script>
  <!-- End Google Tag Manager -->
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}">
  <link rel="canonical" href="{esc(canonical)}">
  <meta property="og:type"        content="{og_type}">
  <meta property="og:url"         content="{esc(canonical)}">
  <meta property="og:title"       content="{esc(title)}">
  <meta property="og:description" content="{esc(desc)}">
  <meta property="og:image"       content="{esc(og_image)}">
  <meta property="og:site_name"   content="HARUO">
  <meta name="twitter:card"        content="summary_large_image">
  <meta name="twitter:title"       content="{esc(title)}">
  <meta name="twitter:description" content="{esc(desc)}">
  <meta name="twitter:image"       content="{esc(og_image)}">
  <link rel="stylesheet" href="{up}assets/style.css">
  <style>
    .sw-meta {{ color: var(--sub); font-size: .8125rem; letter-spacing: .04em; margin: 6px 0 28px; }}
    .sw-tags {{ display: flex; flex-wrap: wrap; gap: 6px 14px; color: var(--faint); font-size: .75rem; margin-bottom: 32px; }}
    .sw-figure {{ margin: 0 0 28px; }}
    .sw-figure img {{ display: block; max-width: 100%; height: auto; margin: 0 auto; }}
    .sw-pager {{ display: flex; justify-content: space-between; gap: 16px; border-top: 1px solid var(--border); padding-top: 18px; margin-top: 12px; font-size: .8125rem; }}
    .sw-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 28px 20px; }}
    .sw-card {{ display: block; color: inherit; text-decoration: none; }}
    .sw-card__thumb {{ aspect-ratio: 1; background: var(--white); display: flex; align-items: center; justify-content: center; overflow: hidden; }}
    .sw-card__thumb img {{ max-width: 100%; max-height: 100%; object-fit: contain; }}
    .sw-card__name {{ font-size: .8125rem; margin-top: 8px; }}
    .sw-card__date {{ font-size: .6875rem; color: var(--faint); }}
    .sw-lead {{ color: var(--sub); font-size: .875rem; margin: 6px 0 32px; }}
  </style>
{extra}</head>
<body>
  <noscript><iframe src="https://www.googletagmanager.com/ns.html?id={GTM_ID}"
  height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<div class="wrap">
  <header class="site-header">
    <div class="site-header__bar">
      <p class="site-logo"><a href="{up}">HARUO</a></p>
      <nav class="site-nav"><a href="{up}archive/">animals archive</a></nav>
    </div>
  </header>
  <main>
"""


def foot(depth):
    up = "../" * depth
    return f"""  </main>
  <footer class="site-footer">
    <div class="footer-inner">
      <div class="footer-links">
        <div class="footer-group">
          <p class="footer-group__name">animals - <span style="font-size:0.8em;">Living Form : 生きるカタチ</span></p>
          <ul>
            <li><a href="{up}archive/">archive</a></li>
            <li><a href="{up}works/">all works</a></li>
            <li><a href="{up}profile/">observer</a></li>
            <li><a href="{up}support/">support</a></li>
          </ul>
        </div>
      </div>
      <p class="footer-copy">&copy; HARUO 1998 &#8211; ongoing &nbsp;·&nbsp; Observed</p>
    </div>
  </footer>
</div>
</body>
</html>
"""


def jsonld(obj):
    s = json.dumps(obj, ensure_ascii=False, indent=2).replace("</", "<\\/")
    return f'  <script type="application/ld+json">\n{s}\n  </script>\n'


def work_page(w, prev_w, next_w):
    depth = 2
    up = "../" * depth
    url = f'{BASE}works/{w["path"]}/'
    imgs_abs = [BASE + p for p in w["images"]]
    title = f'{display_name(w)} — animals by HARUO'
    desc = description(w)
    ld = {
        "@context": "https://schema.org",
        "@type": "VisualArtwork",
        "name": w["title"],
        "url": url,
        "image": imgs_abs,
        "dateCreated": w["date"],
        "creator": {"@type": "Person", "name": "HARUO", "alternateName": "casiomasasi"},
        "isPartOf": {"@type": "CollectionPage", "name": "animals — Field Notes on Unknown Forms", "url": BASE + "works/"},
        "keywords": ", ".join(v for v in w["tags"].values() if v),
    }
    if w["aka"]:
        ld["alternateName"] = w["aka"]
    out = [head(title, desc, url, imgs_abs[0] if imgs_abs else BASE + "img/og-animals.png", depth, "article", jsonld(ld))]
    out.append(f'    <h1 class="page-title">{esc(w["title"])}</h1>\n')
    meta = f'observed {esc(w["date"])}'
    if w["aka"]:
        meta = f'{esc(w["aka"])} &nbsp;·&nbsp; ' + meta
    out.append(f'    <p class="sw-meta">{meta}</p>\n')
    if w["note"]:
        out.append(f'    <p class="sw-lead">{esc(w["note"])}</p>\n')
    n = len(w["images"])
    for i, p in enumerate(w["images"], 1):
        lazy = "" if i == 1 else ' loading="lazy"'
        out.append(f'    <figure class="sw-figure"><img src="{up}{esc(p)}" alt="{esc(alt_text(w, i, n))}"{lazy}></figure>\n')
    tags = "".join(f'<span>{esc(k)}: {esc(v)}</span>' for k, v in w["tags"].items() if v)
    out.append(f'    <p class="sw-tags">{tags}</p>\n')
    prev_a = f'<a href="{up}works/{prev_w["path"]}/" rel="prev">← {esc(prev_w["title"])}</a>' if prev_w else "<span></span>"
    next_a = f'<a href="{up}works/{next_w["path"]}/" rel="next">{esc(next_w["title"])} →</a>' if next_w else "<span></span>"
    out.append(f'    <nav class="sw-pager">{prev_a}<a href="{up}works/">all works</a>{next_a}</nav>\n')
    out.append(foot(depth))
    return "".join(out)


def index_page(works):
    depth = 1
    url = BASE + "works/"
    title = "All works — animals by HARUO"
    desc = (f"All {len(works)} organisms in animals, field notes on unknown forms by HARUO (1998 – ongoing). "
            f"{SITE_DESC_JA}。全作品一覧。")
    ld = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "animals — Field Notes on Unknown Forms",
        "url": url,
        "creator": {"@type": "Person", "name": "HARUO"},
        "hasPart": [{"@type": "VisualArtwork", "name": w["title"], "url": f'{url}{w["path"]}/'} for w in works],
    }
    out = [head(title, desc, url, BASE + "img/og-animals.png", depth, extra=jsonld(ld))]
    out.append('    <h1 class="page-title">animals</h1>\n')
    out.append(f'    <p class="sw-lead">Field notes on unknown forms. {len(works)} organisms, 1998 – ongoing.</p>\n')
    out.append('    <div class="sw-grid">\n')
    for w in works:
        thumb = f'<img src="../{esc(w["images"][0])}" alt="{esc(alt_text(w, 1, 1))}" loading="lazy">' if w["images"] else "—"
        out.append(
            f'      <a class="sw-card" href="{w["path"]}/"><div class="sw-card__thumb">{thumb}</div>'
            f'<p class="sw-card__name">{esc(display_name(w))}</p><p class="sw-card__date">{esc(w["date"])}</p></a>\n'
        )
    out.append('    </div>\n')
    out.append(foot(depth))
    return "".join(out)


def sitemap(works):
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
             '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">']
    for path, freq, pri in STATIC_PAGES:
        lines += ["  <url>", f"    <loc>{BASE}{path}</loc>", f"    <changefreq>{freq}</changefreq>",
                  f"    <priority>{pri}</priority>", "  </url>"]
    for w in works:
        lines += ["  <url>", f'    <loc>{BASE}works/{w["path"]}/</loc>', "    <priority>0.7</priority>"]
        for p in w["images"]:
            lines.append(f"    <image:image><image:loc>{esc(BASE + p)}</image:loc></image:image>")
        lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def main():
    works = load_works()
    OUT.mkdir(exist_ok=True)
    # 前回生成分のうち、作品が消えたフォルダを掃除
    keep = {w["path"] for w in works}
    for d in OUT.iterdir():
        if d.is_dir() and d.name not in keep and (d / "index.html").exists():
            (d / "index.html").unlink()
            d.rmdir()
    for i, w in enumerate(works):
        prev_w = works[i - 1] if i > 0 else None
        next_w = works[i + 1] if i + 1 < len(works) else None
        d = OUT / w["path"]
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(work_page(w, prev_w, next_w), encoding="utf-8")
    (OUT / "index.html").write_text(index_page(works), encoding="utf-8")
    (ROOT / "sitemap.xml").write_text(sitemap(works), encoding="utf-8")
    print(f"{len(works)} works → works/, sitemap.xml updated")


if __name__ == "__main__":
    main()
