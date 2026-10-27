"""Find blog posts that are in neither posts.txt nor skipped.txt and open one GitHub issue per new post."""
import os, requests, json, subprocess
from bs4 import BeautifulSoup
S=requests.Session(); S.headers['User-Agent']='altman-essays (github.com/nishachay/altman-essays)'
from requests.adapters import HTTPAdapter; from urllib3.util.retry import Retry
S.mount('https://',HTTPAdapter(max_retries=Retry(total=5,connect=5,read=5,backoff_factor=2,status_forcelist=[429,500,502,503,504],allowed_methods=['GET'])))  # retry slow/flaky pages instead of failing the build
known=set()
for f in ('posts.txt','skipped.txt'):
    known|={l.strip() for l in open(f) if l.strip() and not l.startswith('#')}
s=BeautifulSoup(S.get('https://blog.samaltman.com/?page=1',timeout=30).text,'html.parser')
for a in s.select('article.post .post-title a'):
    url,title=a['href'],a.get_text(strip=True)
    if url in known: continue
    existing=subprocess.run(['gh','issue','list','--state','all','--search',url,'--json','number'],capture_output=True,text=True).stdout
    if json.loads(existing or '[]'): continue
    subprocess.run(['gh','issue','create','--title',f'New post: {title}','--body',
      f'{url}\n\nInclude it? Add the URL to `posts.txt` (it goes in the book) or `skipped.txt` (leave it out), then close this issue.'],check=True)
    print('opened issue for',url)
