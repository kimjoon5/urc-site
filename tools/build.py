#!/usr/bin/env python3
"""Build every page from data/*.json.

Usage:  python3 tools/build.py
Pages:  index.html (Home), about-us/, curriculum/, research/, network/, join-us/
Each page is a stack of full-screen sections (.sec); the first is the hero, the last is Contact.
Edit the JSON in data/ and re-run. Only Python 3 is required.
"""
import json
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data"


def load(name):
    return json.loads((D / f"{name}.json").read_text(encoding="utf-8"))


SITE = load("site")


def esc(s):
    return html.escape(s or "", quote=True)


def linkify(text):
    out = esc(text)
    return re.sub(r"(https?://[^\s<]+)", r'<a href="\1" target="_blank" rel="noopener">\1</a>', out)


def img(src, base, alt="", w=None, h=None):
    dims = f' width="{w}" height="{h}"' if w and h else ""
    return f'<img src="{base}{esc(src)}" alt="{esc(alt)}"{dims} loading="lazy" decoding="async">'


# ─────────────────────────────────────────────────────────────
# shell
# ─────────────────────────────────────────────────────────────
def nav_links(base, current, numbered=False):
    out = []
    for i, n in enumerate(SITE["nav"], 1):
        href = base + n["path"] if n["path"] else (base or "./")
        cur = ' aria-current="page"' if n["label"] == current else ""
        num = f'<span class="n">{i:02d}</span>' if numbered else ""
        out.append(f'<li><a href="{esc(href)}"{cur}>{num}{esc(n["label"])}</a></li>')
    return "\n".join(out)


def contacts():
    rows = []
    for c in SITE["footer"]["contacts"]:
        val = c["value"]
        v = f'<a href="mailto:{esc(val)}">{esc(val)}</a>' if "@" in val else f'<a href="tel:{esc(val.replace("-", ""))}">{esc(val)}</a>'
        name = f'<dd class="nm">{esc(c["name"])}</dd>' if c.get("name") else '<dd class="nm"></dd>'
        rows.append(f'<dt>{esc(c["role"])}</dt>{name}<dd>{v}</dd>')
    return "\n".join(rows)


class Page:
    """Collects sections so the dots nav and section indices can be generated."""

    def __init__(self, base, current):
        self.base = base
        self.current = current
        self.secs = []  # (id, label, html)

    def add(self, id_, label, inner, cls=""):
        self.secs.append((id_, label, inner, cls))

    def render(self):
        n = len(self.secs)
        out = []
        for i, (id_, label, inner, cls) in enumerate(self.secs):
            idx = "" if i == 0 else f'<div class="sec-index"><b>{i:02d}</b> / {n - 1:02d}</div>'
            bg = "" if i == 0 else f"bg-{(i - 1) % 4 + 1}"
            out.append(f'''
    <section class="sec {cls} {bg}" id="{esc(id_)}" data-label="{esc(label)}">
{idx}
      <div class="sec-inner">
{inner}
      </div>
    </section>''')
        return "\n".join(out)

    def dots(self):
        return "\n".join(f'<button type="button" aria-label="{esc(l)}"><span>{esc(l)}</span></button>' for _, l, _, _ in self.secs)


def footer_html(page):
    foot = SITE["footer"]
    return f'''
  <footer class="foot">
    <div class="foot-inner">
      <div class="foot-grid">
        <div>
          <p class="foot-org">{esc(foot["org"])}</p>
          <p class="foot-meta">{esc(foot["address"])}<br>{esc(foot["copyright"])}</p>
        </div>
        <div class="foot-contact">
          <p class="eyebrow-sm">{esc(foot["contact_title"])}</p>
          <dl>
{contacts()}
          </dl>
        </div>
      </div>
    </div>
  </footer>'''


def shell(page, *, title, description, body_class=""):
    base = page.base
    return f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<meta name="theme-color" content="#ffffff">
<link rel="icon" href="{base}assets/img/urc-logo.png" type="image/png">
<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.min.css">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,400;1,500&display=swap">
<link rel="stylesheet" href="{base}assets/css/style.css">
</head>
<body class="{body_class}">
  <div id="bg" aria-hidden="true"></div>

  <header class="nav">
    <a class="brand" href="{base or './'}" aria-label="{esc(SITE["org"])}">
      <img src="{base}assets/img/urc-logo.png" alt="" width="36" height="36">
      <span class="brand-wordmark" aria-hidden="true"><span>Yonsei Univ.</span><span>Urban Real-estate Club</span></span>
    </a>
    <nav class="nav-links" aria-label="주 메뉴"><ul>
{nav_links(base, page.current)}
    </ul></nav>
    <button class="burger" aria-label="메뉴 열기" aria-expanded="false" aria-controls="menu"><span></span><span></span><span></span></button>
  </header>
  <div class="menu" id="menu" aria-hidden="true">
    <nav aria-label="모바일 메뉴">
      <ul>
{nav_links(base, page.current, numbered=True)}
      </ul>
      <p class="menu-tag">{esc(SITE["org"])}</p>
    </nav>
  </div>

{('<nav class="dots" aria-label="섹션">' + chr(10) + page.dots() + chr(10) + '  </nav>') if len(page.secs) > 1 else ''}

  <main>
{page.render()}
  </main>
{footer_html(page)}

  <script src="{base}assets/js/main.js" defer></script>
</body>
</html>
'''


def hero(title, pills=None, extra="", photo=None):
    pill_html = ""
    if pills:
        pill_html = '<div class="pills" data-reveal style="--d:240ms">' + "".join(
            f'<a class="pill" href="#{esc(k)}"><span class="n">{i + 1:02d}</span>{esc(l)}</a>' for i, (k, l) in enumerate(pills)
        ) + "</div>"
    photo_html = f'<div class="hero-photo" aria-hidden="true"><img src="{photo}" alt="" width="1920" height="1280" fetchpriority="high"></div>' if photo else '<div class="hero-glow a"></div><div class="hero-glow b"></div>'
    return f'''
        {photo_html}
        <p class="eyebrow" data-reveal>URC · {esc(title)}</p>
        <h1 data-reveal style="--d:80ms">{esc(title)}<span class="dot">.</span></h1>
        <p class="hero-sub" data-reveal style="--d:160ms">{esc(SITE["org"])}</p>
{pill_html}{extra}'''


def head(eyebrow, h2=None, sub=None):
    h = f'<h2 data-reveal style="--d:80ms">{esc(h2)}</h2>' if h2 else ""
    s = f'<p class="sub" data-reveal style="--d:160ms">{esc(sub)}</p>' if sub else ""
    return f'<div class="sec-head"><p class="eyebrow" data-reveal>{esc(eyebrow)}</p>{h}{s}</div>'


# ─────────────────────────────────────────────────────────────
# pages
# ─────────────────────────────────────────────────────────────
def build_home():
    d = load("home")
    h = d["hero"]
    pg = Page("", "Home")
    pg.add("hero", "Home", f'''
        <div class="hero-photo" aria-hidden="true"><img src="{esc(h["photo"])}" alt="" width="2000" height="1230" fetchpriority="high"></div>
        <p class="eyebrow" data-reveal>{esc(SITE["org"])}</p>
        <h1 data-reveal style="--d:90ms"><span class="only-desktop">{esc(h["title"])}</span><span class="only-mobile">{esc(h["title_mobile"]).replace(chr(10), "<br>")}</span></h1>
        <p class="home-tagline" data-reveal style="--d:180ms">{esc(h["tagline"])}</p>
        <div class="btn-row" data-reveal style="--d:270ms">
          <a class="btn btn-primary" href="about-us/">About us</a>
          <a class="btn btn-ghost" href="join-us/">Join us</a>
        </div>''', cls="hero hero-home")
    return shell(pg, title=f"URC | {SITE['org_short']}", description=f"{h['title']} — {h['tagline']}", body_class="is-home scroll-natural")


def build_about():
    d = load("about")
    base = "../"
    pg = Page(base, "About us")
    it, g = d["intro"], d["greetings"]
    pg.add("hero", "About us", hero(d["title"], [("introduction", d["tabs"][0]), ("greetings", d["tabs"][1])], photo=base + "assets/img/hero-about.jpg"), cls="hero has-photo")
    paras = "".join(f"<p>{esc(p)}</p>" for p in it["paras"])
    pg.add("introduction", d["tabs"][0], f'''
        {head(d["tabs"][0], it["heading"])}
        <div class="lead-block narrow" data-reveal style="--d:160ms">{paras}</div>''', cls="sec-alt")
    pillars = "\n".join(
        f'''<div class="card pillar" data-reveal style="--d:{i * 90}ms">
            <div class="pillar-icon"><img src="{base}{esc(p["icon"])}" alt="" width="48" height="48"></div>
            <h3>{esc(p["title"])}</h3>
            <p>{esc(p["text"])}</p>
          </div>''' for i, p in enumerate(it["pillars"])
    )
    values = "\n".join(
        f'''<article class="card value" data-reveal style="--d:{300 + i * 90}ms">
            <p class="n">{i + 1:02d}</p>
            <h3>{esc(v["title"])}</h3>
            <p>{esc(v["text"])}</p>
          </article>''' for i, v in enumerate(it["values"])
    )
    pg.add("values", d["tabs"][0], f'''
        {head(d["tabs"][0])}
        <div class="pillars">
{pillars}
        </div>
        <div class="split-2 values">
{values}
        </div>''')
    gparas = "".join(f"<p>{esc(p)}</p>" for p in g["paras"])
    pg.add("greetings", d["tabs"][1], f'''
        {head(d["tabs"][1])}
        <article class="split" data-reveal style="--d:120ms">
          <div>
            <div class="photo portrait">{img(g["photo"], base, g["name"], 453, 545)}</div>
          </div>
          <div class="greeting-person">
            <p class="greeting-role">{esc(g["role"])}</p>
            <h2 class="greeting-name">{esc(g["name"])}</h2>
            <div class="lead-block letter">{gparas}</div>
          </div>
        </article>''')
    return shell(pg, title=f"About us – URC | {SITE['org_short']}", description=it["paras"][0][:150])


def build_curriculum():
    d = load("curriculum")
    base = "../"
    pg = Page(base, "Curriculum")
    pg.add("hero", "Curriculum", hero(d["title"], [("sessions", d["tabs"][0]), ("external", d["tabs"][1]), ("networking", d["tabs"][2])], photo=base + "assets/img/hero-curriculum.jpg"), cls="hero has-photo")
    total = len(d["sessions"])
    for i, s in enumerate(d["sessions"]):
        pg.add("sessions" if i == 0 else f"session-{s['key']}", s["title"], f'''
        <div class="step-bar" data-reveal><span class="n">Session {i + 1:02d} / {total:02d}</span><div class="track"><span style="--w:{round((i + 1) / total * 100)}%"></span></div></div>
        <article class="split">
          <div>
            <p class="eyebrow-sm" data-reveal style="--d:60ms">{esc(d["tabs"][0])}</p>
            <h2 data-reveal style="--d:120ms">{esc(s["title"])}</h2>
          </div>
          <div>
            <p class="lead" data-reveal style="--d:180ms">{esc(s["text"])}</p>
            <div class="gallery">
              <figure class="photo frame" data-reveal style="--d:260ms">{img(s["images"][0], base, s["title"], 1200, 905)}</figure>
              <figure class="photo frame" data-reveal style="--d:340ms">{img(s["images"][1], base, s["title"], 1200, 900)}</figure>
            </div>
          </div>
        </article>''')
    ext = "\n".join(
        f'''<div class="card ext-card" data-reveal style="--d:{i * 70}ms">
            <div class="ext-logo{(' ' + esc(e['logo_class'])) if e.get('logo_class') else ''}">{img(e["logo"], base, e["title"], 900, 500)}</div>
            <h3><span class="n">{i + 1:02d}</span>{esc(e["title"])}</h3>
          </div>''' for i, e in enumerate(d["external"])
    )
    pg.add("external", d["tabs"][1], f'''
        {head(d["tabs"][1])}
        <div class="ext-grid">
{ext}
        </div>''')
    n = d["networking"]
    pg.add("networking", d["tabs"][2], f'''
        {head(d["tabs"][2], n["heading"])}
        <p class="lead narrow" data-reveal style="--d:160ms">{esc(n["text"])}</p>
        <div class="duo">
          <div class="photo frame" data-reveal style="--d:240ms">{img(n["images"][0], base, "", 1200, 903)}</div>
          <div class="photo frame" data-reveal style="--d:320ms">{img(n["images"][1], base, "", 1200, 900)}</div>
        </div>''')
    return shell(pg, title=f"Curriculum – URC | {SITE['org_short']}", description=d["sessions"][0]["text"][:150])


def build_research():
    d = load("research")
    base = "../"
    pg = Page(base, d["title"])
    keys = ["market", "issue", "im-project"]
    pg.add("hero", d["title"], hero(d["title"], list(zip(keys, d["tabs"])), photo=base + "assets/img/hero-research.jpg"), cls="hero has-photo")
    for k, g, label in zip(keys, d["groups"], d["tabs"]):
        if g.get("image"):
            content = f'''<article class="archive-feature">
          <figure class="photo archive-cover" data-reveal style="--d:140ms">{img(g["image"], base, g["heading"], 1040, 720)}</figure>
          <p class="lead archive-copy" data-reveal style="--d:220ms">{esc(g["description"])}</p>
        </article>'''
            pg.add(k, label, f'''\n        {head(d["title"], g["heading"])}\n        {content}''')
            continue
        tiles = []
        for j, it in enumerate(g["items"]):
            inner = f'''<span class="doc-icon" aria-hidden="true"><svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4"><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5"/></svg></span><span class="doc-n">{j + 1:02d}</span>'''
            if it.get("href"):
                tiles.append(f'<a class="card doc" href="{esc(it["href"])}" target="_blank" rel="noopener" data-reveal style="--d:{j * 70}ms">{inner}<span class="doc-tag">PDF</span></a>')
            else:
                tiles.append(f'<div class="card doc is-empty" data-reveal style="--d:{j * 70}ms">{inner}</div>')
        pg.add(k, label, f'''
        {head(d["title"], g["heading"])}
        <div class="doc-grid">
{chr(10).join(tiles)}
        </div>''')
    return shell(pg, title=f"{d['title']} – URC | {SITE['org_short']}", description=" · ".join(d["tabs"]))


def build_network():
    d = load("network")
    base = "../"
    pg = Page(base, "Network")
    pg.add("hero", "Network", hero(d["title"], [("advisors", d["tabs"][0]), ("members", d["tabs"][1]), ("network", d["tabs"][2])], photo=base + "assets/img/hero-network.jpg"), cls="hero has-photo")
    advisors = "\n".join(
        f'''<article class="card advisor" data-reveal style="--d:{i * 120}ms">
            <div class="photo portrait">{img(a["photo"], base, a["name"], 453, 566)}</div>
            <div>
              <p class="eyebrow-sm">{esc(a["group"])}</p>
              <h3>{esc(a["name"])}</h3>
              <ul class="dash-list">{"".join(f"<li>{esc(l)}</li>" for l in a["lines"])}</ul>
            </div>
          </article>''' for i, a in enumerate(d["advisors"])
    )
    pg.add("advisors", d["tabs"][0], f'''
        {head(d["tabs"][0])}
        <div class="split-2">
{advisors}
        </div>''')
    strip = "\n".join(
        f'''<button class="gen" role="tab" id="gen-{esc(g["slug"])}" data-gen="{esc(g["slug"])}" aria-selected="{'true' if i == 0 else 'false'}" aria-controls="genpanel-{esc(g["slug"])}" tabindex="{0 if i == 0 else -1}">
            <div class="gen-bar"><span style="--d:{i * 140}ms"></span></div>
            <div class="gen-txt" style="--d:{i * 140 + 200}ms"><p class="gen-n">{i:02d}</p><p class="gen-l">{esc(g["gen"])}</p></div>
          </button>''' for i, g in enumerate(d["members"])
    )

    def card(m, j):
        role = f'<span class="role">{esc(m["role"])}</span>' if m.get("role") else ""
        careers = ('<ul class="mcard-careers">' + "".join(f"<li><span>{esc(c)}</span></li>" for c in m["careers"]) + "</ul>") if m.get("careers") else ""
        return f'''<li class="card mcard" data-reveal style="--d:{min(j, 11) * 55}ms">
              <div class="mcard-photo">{img(m["photo"], base, m["name"], 453, 545)}</div>
              <div class="mcard-body"><h4 class="mcard-name"><span>{esc(m["name"])}</span>{role}</h4><p class="mcard-dept">{esc(m["dept"])}</p>{careers}</div>
            </li>'''

    gpanels = "\n".join(
        f'''<div class="gen-panel" id="genpanel-{esc(g["slug"])}" role="tabpanel" aria-labelledby="gen-{esc(g["slug"])}" data-gen="{esc(g["slug"])}"{'' if i == 0 else ' hidden'}>
            <ul class="members">{"".join(card(m, j) for j, m in enumerate(g["members"]))}</ul>
          </div>''' for i, g in enumerate(d["members"])
    )
    pg.add("members", d["tabs"][1], f'''
        {head(d["tabs"][1])}
        <div class="gens"><div class="gen-strip" role="tablist" aria-label="기수">
{strip}
        </div></div>
{gpanels}''', cls="sec-members")
    n = d["network"]
    pg.add("network", d["tabs"][2], f'''
        {head(d["tabs"][2])}
        <div class="net">
          <p class="net-text" data-reveal style="--d:120ms">{esc(n["text"])}</p>
          <div class="photo" data-reveal style="--d:220ms">{img(n["photo"], base, "", 1024, 673)}</div>
        </div>''')
    return shell(pg, title=f"Network – URC | {SITE['org_short']}", description=n["text"][:150])


def build_join():
    d = load("join")
    base = "../"
    pg = Page(base, "Join us")
    pg.add("hero", "Join us", hero(d["title"], [("recruitment", d["tabs"][0]), ("faq", d["tabs"][1])], photo=base + "assets/img/hero-join.jpg"), cls="hero has-photo")
    blocks = {}
    for i, b in enumerate(d["recruit"]):
        h = b["heading"]
        if h == "지원일정":
            rows = []
            for j, it in enumerate(b["items"]):
                lab, val = (it.split(":", 1) + [""])[:2]
                rows.append(f'<li><span class="n">{j + 1:02d}</span><span class="sched-label">{esc(lab.strip())}</span><span class="sched-val">{esc(val.strip())}</span></li>')
            inner = '<ol class="sched">' + "".join(rows) + "</ol>"
        elif h == "지원문의":
            rows = []
            for it in b["items"]:
                m = re.match(r"^(.*?)\s*\((0\d{1,2}-\d{3,4}-\d{4})\)\s*$", it)
                rows.append(f'<li><span>{esc(m.group(1))}</span><a href="tel:{m.group(2).replace("-", "")}">{esc(m.group(2))}</a></li>' if m else f"<li><span>{esc(it)}</span></li>")
            inner = '<ul class="rows">' + "".join(rows) + "</ul>"
        elif h == "지원방법":
            form = next((re.search(r"https?://\S+", it).group(0) for it in b["items"] if re.search(r"https?://\S+", it)), None)
            inner = '<ul class="dash-list">' + "".join(f"<li>{linkify(x)}</li>" for x in b["items"]) + "</ul>"
            if form:
                inner += f'<div class="btn-row"><a class="btn btn-primary" href="{esc(form)}" target="_blank" rel="noopener">{esc(b["items"][0].split(":")[0])}</a></div>'
        else:
            inner = '<ul class="rows">' + "".join(f"<li><span>{esc(it)}</span></li>" for it in b["items"]) + "</ul>"
        blocks[h] = f'''<div data-reveal style="--d:{(i % 2) * 120 + 120}ms">
            <p class="n">{i + 1:02d}</p>
            <h3 class="h-mid">{esc(h)}</h3>
            {inner}
          </div>'''
    pg.add("recruitment", d["tabs"][0], f'''
        {head(d["tabs"][0])}
        <div class="split-2 recruit">
{blocks["지원자격"]}
{blocks["지원일정"]}
        </div>''')
    pg.add("apply", d["tabs"][0], f'''
        {head(d["tabs"][0])}
        <div class="split-2 recruit">
{blocks["지원방법"]}
{blocks["지원문의"]}
        </div>''')
    faq = "\n".join(
        f'''<details class="card faq" data-reveal style="--d:{i * 70}ms"{" open" if i == 0 else ""}>
            <summary><span class="n">{i + 1:02d}</span><span class="faq-q">{esc(f["q"])}</span><span class="faq-plus" aria-hidden="true"></span></summary>
            <div class="faq-a">{"".join(f"<p>{esc(p)}</p>" for p in f["a"])}</div>
          </details>''' for i, f in enumerate(d["faq"])
    )
    pg.add("faq", d["tabs"][1], f'''
        {head(d["tabs"][1])}
        <div class="faq-list">
{faq}
        </div>''')
    return shell(pg, title=f"Join us – URC | {SITE['org_short']}", description=" / ".join(d["recruit"][0]["items"])[:150])


PAGES = {
    "index.html": build_home,
    "about-us/index.html": build_about,
    "curriculum/index.html": build_curriculum,
    "research/index.html": build_research,
    "network/index.html": build_network,
    "join-us/index.html": build_join,
}

for rel, fn in PAGES.items():
    out = ROOT / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    page = fn()
    out.write_text(page, encoding="utf-8")
    print(f"wrote {rel} ({len(page):,} bytes)")
