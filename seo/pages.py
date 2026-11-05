#!/usr/bin/env python3
"""Generate sourced answer pages, homepage answer links, robots.txt, sitemap.xml, IndexNow key.

Run order: python3 seo/pages.py  (it runs i18n/build.py itself, then writes the sitemap).
Every number here was verified against its named source on 2026-11-04.
"""
import html, json, pathlib, re, subprocess, sys, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
BASE = "https://better-than-you-think.vercel.app"
INDEXNOW_KEY = "b7e1c4f09a2d4e6f8c3b5a7d9e1f2a4c"

SRC = {
  "pip": ("Our World in Data, World Bank Poverty and Inequality Platform", "https://ourworldindata.org/tracking-how-many-people-live-on-less-than-3-10-or-30-a-day"),
  "igme": ("UN IGME, Levels and Trends in Child Mortality 2024", "https://data.unicef.org/resources/levels-and-trends-in-child-mortality-2024/"),
  "igme20": ("UN IGME, Child Mortality Report 2020 (1990 baseline)", "https://www.un.org/development/desa/pd/sites/www.un.org.development.desa.pd/files/un-igme-child-mortality-report-2020.pdf.pdf"),
  "le": ("Our World in Data, UN World Population Prospects 2024", "https://ourworldindata.org/grapher/life-expectancy"),
  "lit": ("Our World in Data, Literacy", "https://ourworldindata.org/literacy"),
  "irena": ("IRENA, Renewable Power Generation Costs in 2024", "https://www.irena.org/Publications"),
  "gap": ("Gapminder, extreme poverty question", "https://www.gapminder.org/video/poverty/"),
}

PAGES = [
 dict(slug="is-extreme-poverty-increasing", ref="seo-poverty",
  q="Is extreme poverty increasing?",
  a="No. The share of people in extreme poverty (less than $3 a day) fell from 36% in 2000 to 10% in 2024.",
  body=["Extreme poverty is measured by the World Bank against a line of $3 a day in 2021 prices. On that line, more than a third of humanity was extremely poor in 2000. By 2024 it was one in ten.",
        "Most people do not know this. In Gapminder surveys across 14 countries, only about 9% of respondents knew that extreme poverty had almost halved in 20 years. Random guessing scores 33%."],
  rows=[("2000", "36%"), ("2024", "10%")], src=["pip", "gap"],
  still="About 847 million people still live on less than $3 a day."),
 dict(slug="is-child-mortality-going-down", ref="seo-childmort",
  q="Is child mortality going down?",
  a="Yes. Deaths before age 5 fell from 93 per 1,000 births in 1990 to 37 per 1,000 in 2023, a drop of about 60%.",
  body=["In 1990, about 12.5 million children died before their fifth birthday. In 2023, about 4.8 million did, while the number of births stayed large.",
        "Nearly half of the deaths that remain happen in the first 28 days of life, so newborn care is now where most lives can be saved."],
  rows=[("1990", "93 per 1,000"), ("2023", "37 per 1,000")], src=["igme", "igme20"],
  still="4.8 million children still died before age 5 in 2023, and since 2015 the rate of decline has slowed by 42% compared with 2000 to 2015."),
 dict(slug="is-life-expectancy-increasing", ref="seo-lifeexp",
  q="Is life expectancy increasing?",
  a="Yes. Average life expectancy for the whole world rose from about 46.5 years in 1950 to 73 years in 2023.",
  body=["In 1900 the global average was about 32 years. It has more than doubled since then. A large part of the gain comes from fewer children dying young."],
  rows=[("1950", "46.5 years"), ("2023", "73 years")], src=["le"],
  still="The gap between the countries with the longest and shortest lives is still more than 20 years."),
 dict(slug="is-literacy-increasing", ref="seo-literacy",
  q="Is literacy increasing worldwide?",
  a="Yes. In 1820 about 12% of adults could read and write. Today about 87% can.",
  body=["Most of the rise came after 1950, when basic schooling spread. World literacy was about 42% in 1960 and about 70% in 1983."],
  rows=[("1820", "12%"), ("Today", "87%")], src=["lit"],
  still="In some countries of sub-Saharan Africa, fewer than 1 in 3 adults can read and write."),
 dict(slug="is-solar-power-getting-cheaper", ref="seo-solar",
  q="Is solar power getting cheaper?",
  a="Yes. Electricity from new large solar plants fell from $0.417 per kWh in 2010 to $0.043 per kWh in 2024, about 90% cheaper.",
  body=["The total cost to install a large solar plant fell from $5,283 per kW in 2010 to $691 per kW in 2024. In 2024, new solar was on average cheaper than new fossil-fuel power."],
  rows=[("2010", "$0.417 / kWh"), ("2024", "$0.043 / kWh")], src=["irena"],
  still="Cheap power is not yet clean power everywhere. Grids, storage and financing still limit how fast it is built."),
]
WORLD = dict(slug="is-the-world-getting-worse", ref="seo-world",
  q="Is the world getting worse?",
  a="On the long-run measures of human welfare, no. Poverty, child deaths, life expectancy, literacy and clean-energy cost have all improved for decades. Progress is not finished, and some of it has slowed.",
  body=["The news reports events, and slow improvement is not an event. That is one reason most people answer questions about global trends worse than random guessing.",
        "Each answer below gives the data, its source, and what is still unsolved."],
  rows=[], src=["gap"], still="Child-mortality progress has slowed since 2015, and hundreds of millions of people are still extremely poor.")

CSS = """:root{--ground:#f5f8f7;--card:#fff;--ink:#0f1f24;--soft:#55666b;--line:#d3dedb;--rise:#0a7a58}
@media (prefers-color-scheme: dark){:root{--ground:#0c1517;--card:#132024;--ink:#e5efec;--soft:#9db0ad;--line:#26383c;--rise:#4fd1a1;color-scheme:dark}}
body{margin:0;background:var(--ground);color:var(--ink);font:17px/1.6 "Atkinson Hyperlegible",system-ui,-apple-system,sans-serif}
.wrap{max-width:680px;margin:0 auto;padding:40px max(16px,env(safe-area-inset-right,0px)) 64px max(16px,env(safe-area-inset-left,0px));display:grid;gap:20px}
h1{font:800 clamp(32px,7vw,48px)/1.05 "Bricolage Grotesque","Avenir Next",sans-serif;margin:0}
h2{font:700 20px/1.3 "Bricolage Grotesque","Avenir Next",sans-serif;margin:0}
p{margin:0}.answer{font-size:20px}a{color:var(--rise)}
table{border-collapse:collapse;font-variant-numeric:tabular-nums;background:var(--card);border:1px solid var(--line)}
td{padding:8px 16px;border-bottom:1px solid var(--line)}tr:last-child td{border-bottom:0}
.still{border-left:3px solid var(--soft);padding-left:12px;color:var(--soft)}
.cta{display:inline-block;background:var(--rise);color:var(--ground);font-weight:700;padding:12px 18px;border-radius:8px;text-decoration:none}
ul{margin:0;padding-left:20px}.small{font-size:14px;color:var(--soft)}"""

def esc(t): return html.escape(t, quote=True)

def page(p, others):
    url = f"{BASE}/{p['slug']}/"
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{
        "@type": "Question", "name": p["q"],
        "acceptedAnswer": {"@type": "Answer", "text": p["a"] + " " + p["still"]}}]}
    rows = "".join(f"<tr><td>{esc(a)}</td><td>{esc(b)}</td></tr>" for a, b in p["rows"])
    srcs = "".join(f'<li><a href="{SRC[k][1]}" rel="noopener">{esc(SRC[k][0])}</a></li>' for k in p["src"])
    links = "".join(f'<li><a href="/{o["slug"]}/">{esc(o["q"])}</a></li>' for o in others)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(p['q'])} The data | Better Than You Think</title>
<meta name="description" content="{esc(p['a'])}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{esc(p['q'])}">
<meta property="og:description" content="{esc(p['a'])}">
<meta property="og:image" content="{BASE}/og.png">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,700;12..96,800&family=Atkinson+Hyperlegible:wght@400;700&display=swap">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>{CSS}</style>
</head>
<body>
<main class="wrap">
  <p class="small"><a href="/">Better Than You Think</a></p>
  <h1>{esc(p['q'])}</h1>
  <p class="answer"><b>{esc(p['a'])}</b></p>
  {"<table>" + rows + "</table>" if rows else ""}
  {"".join(f"<p>{esc(b)}</p>" for b in p['body'])}
  <p class="still"><b>Still unsolved:</b> {esc(p['still'])}</p>
  <p><a class="cta" href="/?ref={p['ref']}">Test yourself: the 2-minute quiz</a></p>
  <section><h2>Sources</h2><ul>{srcs}</ul></section>
  <section><h2>More answers</h2><ul>{links}</ul></section>
</main>
</body>
</html>
"""

def main():
    allp = [WORLD] + PAGES
    for p in allp:
        others = [o for o in allp if o is not p]
        out = SITE / p["slug"] / "index.html"
        out.parent.mkdir(exist_ok=True)
        out.write_text(page(p, others))
    # Homepage answer links (inherited by translations).
    m = (SITE / "index.html").read_text()
    links = "".join(f'<a href="/{p["slug"]}/">{esc(p["q"])}</a>' for p in allp)
    m = re.sub(r"<!--ANSWERS-->.*?<!--/ANSWERS-->", lambda _: "<!--ANSWERS-->" + links + "<!--/ANSWERS-->", m, flags=re.S)
    (SITE / "index.html").write_text(m)
    subprocess.run([sys.executable, str(ROOT / "i18n" / "build.py")], check=True)
    # Sitemap with hreflang alternates for the quiz.
    langs = sorted(x.stem for x in (ROOT / "i18n").glob("*.json"))
    today = datetime.date.today().isoformat()
    qurl = lambda l: f"{BASE}/" if l == "en" else f"{BASE}/{l}/"
    alt = "".join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{qurl(l)}"/>' for l in ["en"] + langs)
    urls = [f"<url><loc>{qurl(l)}</loc><lastmod>{today}</lastmod>{alt}</url>" for l in ["en"] + langs]
    urls += [f"<url><loc>{BASE}/{p['slug']}/</loc><lastmod>{today}</lastmod></url>" for p in allp]
    urls.append(f"<url><loc>{BASE}/partners.html</loc><lastmod>{today}</lastmod></url>")
    (SITE / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(urls) + "\n</urlset>\n")
    (SITE / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /api/\n\nSitemap: {BASE}/sitemap.xml\n")
    (SITE / f"{INDEXNOW_KEY}.txt").write_text(INDEXNOW_KEY)
    print(f"answer pages: {len(allp)}, sitemap urls: {len(urls)}")

main()
