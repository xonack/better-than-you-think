#!/usr/bin/env bash
# Build, deploy (personal scope), verify every sitemap URL, submit to IndexNow, commit and push.
# Usage: bash seo/ship.sh "commit message"
set -euo pipefail
cd "$(dirname "$0")/.."
B=https://better-than-you-think.vercel.app
KEY=$(grep -oE 'INDEXNOW_KEY = "[a-f0-9]+"' seo/pages.py | cut -d'"' -f2)
python3 seo/pages.py | tail -1
python3 -c "import xml.dom.minidom as m; m.parse('site/sitemap.xml')"
vercel deploy --prod --yes --scope jens-2316s-projects 2>&1 | grep -E "Aliased|Error"
sleep 5
fail=0
for u in $(grep -oE '<loc>[^<]+</loc>' site/sitemap.xml | sed 's/<[^>]*>//g'); do
  c=$(curl -s -o /dev/null -w '%{http_code}' "$u?t=$RANDOM"); [ "$c" = 200 ] || { echo "FAIL $c $u"; fail=1; }
done
echo "sitemap urls=$(grep -c '<loc>' site/sitemap.xml) fail=$fail"
[ "$fail" = 0 ] || exit 1
URLS=$(grep -oE '<loc>[^<]+</loc>' site/sitemap.xml | sed 's/<[^>]*>//g' | python3 -c 'import sys,json;print(json.dumps([l.strip() for l in sys.stdin if l.strip()]))')
curl -s -o /dev/null -w "IndexNow HTTP %{http_code}\n" -X POST https://api.indexnow.org/indexnow \
  -H 'content-type: application/json; charset=utf-8' \
  -d "{\"host\":\"better-than-you-think.vercel.app\",\"key\":\"$KEY\",\"keyLocation\":\"$B/$KEY.txt\",\"urlList\":$URLS}"
git add -A
git commit -qm "$1

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" && git push -q && echo PUSHED
