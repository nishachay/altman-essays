"""Build altman.epub from the curated list in posts.txt (one URL per line)."""
import requests, datetime, subprocess, re, pathlib
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
S=requests.Session(); S.headers['User-Agent']='altman-essays (github.com/nishachay/altman-essays)'
urls=[l.strip() for l in open('posts.txt') if l.strip() and not l.startswith('#')]
def fetch(u):
    s=BeautifulSoup(S.get(u,timeout=30).text,'html.parser')
    title=s.select_one('.post-title').get_text(strip=True)
    d=s.select_one('.posthaven-formatted-date')
    ts=int(d['data-unix-time']) if d and d.get('data-unix-time') else 0
    body=s.select_one('.posthaven-post-body')
    return ts,title,u,str(body)
with ThreadPoolExecutor(8) as ex: posts=list(ex.map(fetch,urls))
posts.sort(key=lambda p:p[0], reverse=True)
html=['<html><head><meta charset="utf-8"><title>Sam Altman Essays</title></head><body>']
for ts,title,u,body in posts:
    date=datetime.datetime.fromtimestamp(ts,datetime.UTC).strftime('%B %Y') if ts else ''
    html.append(f'<h1>{title}</h1><p><em>{date} · <a href="{u}">{u}</a></em></p>{body}')
html.append('</body></html>')
pathlib.Path('dist').mkdir(exist_ok=True)
open('dist/altman.html','w').write('\n'.join(html))
subprocess.run(['pandoc','dist/altman.html','-o','dist/altman.epub','--toc','--toc-depth=1',
  '--metadata','title=Sam Altman Essays','--metadata','author=Sam Altman','--metadata','lang=en'],check=True)
print(f'built {len(posts)} essays')
