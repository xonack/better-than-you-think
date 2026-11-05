#!/usr/bin/env python3
"""Build site/<lang>/index.html from the English master site/index.html.

Each i18n/<lang>.json maps exact English substrings to translations. Every key
must occur in the master, or the build fails, so a master edit cannot silently
leave English text in a translation. Measurement values (OUTLOOK) stay English.
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MASTER = ROOT / "site" / "index.html"
NAMES = {"en": "English", "es": "Español", "pt": "Português", "fr": "Français",
         "de": "Deutsch", "hi": "हिन्दी", "zh": "中文"}
BASE = "https://better-than-you-think.vercel.app"

def nav(cur, langs):
    links = []
    for l in ["en"] + langs:
        href = "/" if l == "en" else f"/{l}/"
        attr = ' aria-current="page"' if l == cur else ""
        links.append(f'<a href="{href}" hreflang="{l}"{attr}>{NAMES[l]}</a>')
    return "<!--LANGS-->" + "".join(links) + "<!--/LANGS-->"

def set_nav(s, cur, langs):
    s = re.sub(r"<!--LANGS-->.*?<!--/LANGS-->", lambda m: nav(cur, langs), s, flags=re.S)
    return re.sub(r"<!--ALT-->.*?<!--/ALT-->", lambda m: alts(cur, langs), s, flags=re.S)

def alts(cur, langs):
    url = lambda l: f"{BASE}/" if l == "en" else f"{BASE}/{l}/"
    out = [f'<link rel="canonical" href="{url(cur)}">']
    out += [f'<link rel="alternate" hreflang="{l}" href="{url(l)}">' for l in ["en"] + langs]
    out.append(f'<link rel="alternate" hreflang="x-default" href="{BASE}/">')
    return "<!--ALT-->" + "\n".join(out) + "<!--/ALT-->"

def main():
    langs = sorted(p.stem for p in (ROOT / "i18n").glob("*.json"))
    master = MASTER.read_text()
    MASTER.write_text(set_nav(master, "en", langs))
    for lang in langs:
        tr = json.loads((ROOT / "i18n" / f"{lang}.json").read_text())
        s = master
        missing = [k for k in tr if k not in s]
        if missing:
            sys.exit(f"{lang}: keys not in master: {missing[:3]}")
        for k in sorted(tr, key=len, reverse=True):
            s = s.replace(k, tr[k])
        s = s.replace('<html lang="en">', f'<html lang="{lang}">', 1)
        s = s.replace(f'content="{BASE}/"', f'content="{BASE}/{lang}/"', 1)
        s = s.replace(f'{BASE}/?ref=share', f'{BASE}/{lang}/?ref=share-{lang}')
        s = set_nav(s, lang, langs)
        out = ROOT / "site" / lang / "index.html"
        out.parent.mkdir(exist_ok=True)
        out.write_text(s)
        print(f"built {out.relative_to(ROOT)} ({len(tr)} strings)")

main()
