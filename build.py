"""Fetch the essays in posts.txt (and the guide in guide.txt) and build the EPUB, PDF and Markdown ZIP."""
import requests, datetime, subprocess, re, pathlib, json, zipfile, html as H
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
S=requests.Session(); S.headers['User-Agent']='altman-essays (github.com/nishachay/altman-essays)'
from requests.adapters import HTTPAdapter; from urllib3.util.retry import Retry
S.mount('https://',HTTPAdapter(max_retries=Retry(total=5,connect=5,read=5,backoff_factor=2,status_forcelist=[429,500,502,503,504],allowed_methods=['GET'])))  # retry slow/flaky pages instead of failing the build
urls=[l.strip() for l in open('posts.txt') if l.strip() and not l.startswith('#')]
def generic(s):
    """Body of a standalone essay site: climb from the h1 to the block holding most of the text."""
    h1=s.find('h1'); total=len(s.body.get_text(' ').split()); el=h1
    while el.parent and len(el.get_text(' ').split())<0.8*total: el=el.parent
    for t in el.find_all(['script','style','nav','header','footer']): t.decompose()
    if el.find('h1'): el.find('h1').decompose()
    return el
def slug_of(u,title):
    return u.rstrip('/').rsplit('/',1)[1] if 'blog.samaltman' in u else re.sub(r'[^a-z0-9]+','-',title.lower()).strip('-')
URL=re.compile(r'https?://[^\s<>"]+[^\s<>".,;:)\]]')
def tidy(body, slug):
    """Link bare URLs, and make [1]-style footnote markers jump to their note and back."""
    from bs4 import NavigableString
    for t in list(body.find_all(string=URL)):
        if t.find_parent('a'): continue
        parts=URL.split(t); urls=URL.findall(t); new=[]
        for i,txt in enumerate(parts):
            if txt: new.append(NavigableString(txt))
            if i<len(urls):
                a=body.new_tag('a',href=urls[i]); a.string=urls[i]; new.append(a)
        t.replace_with(*new)
    notes={}
    for p in body.find_all('p'):
        m=re.match(r'\s*\[(\d+)\]',p.get_text())
        if m: notes[m.group(1)]=p
    if not notes: return
    for n,p in notes.items():
        first=p.find(string=re.compile(r'\['+n+r'\]'))
        if first is None: continue
        pre,_,post=first.partition('['+n+']')
        a=body.new_tag('a',href=f'#{slug}-ref-{n}',id=f'{slug}-fn-{n}'); a.string=f'[{n}]'
        first.replace_with(*( [NavigableString(pre)] if pre else []), a, NavigableString(post))
    done=set()
    for t in list(body.find_all(string=re.compile(r'\[\d+\]'))):
        if t.find_parent('a') or any(t.find_parent('p') is p for p in notes.values()): continue
        pieces=re.split(r'(\[\d+\])',t); new=[]
        for x in pieces:
            m=re.fullmatch(r'\[(\d+)\]',x)
            if m and m.group(1) in notes:
                n=m.group(1); attrs={'href':f'#{slug}-fn-{n}'}
                if n not in done: attrs['id']=f'{slug}-ref-{n}'; done.add(n)
                a=body.new_tag('a',**attrs); a.string=x; s=body.new_tag('sup'); s.append(a); new.append(s)
            elif x: new.append(NavigableString(x))
        t.replace_with(*new)
def fetch(u):
    s=BeautifulSoup(S.get(u,timeout=30).text,'html.parser')
    if 'blog.samaltman.com' in u:
        title=s.select_one('.post-title').get_text(strip=True)
        d=s.select_one('.posthaven-formatted-date')
        ts=int(d['data-unix-time']) if d and d.get('data-unix-time') else 0
        body=s.select_one('.posthaven-post-body')
    else:
        title=s.find('h1').get_text(strip=True)
        m=re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}',s.get_text(' '))
        ts=int(datetime.datetime.strptime(m.group(0),'%B %d, %Y').replace(tzinfo=datetime.UTC).timestamp()) if m else 0
        body=generic(s)
        for t in body.find_all(string=re.compile(r'^\s*(by Sam Altman.*|'+(m.group(0) if m else 'x^')+r')\s*$')): t.extract()
    if 'playbook.samaltman.com' in u:
        # drop the site's own byline, clickable contents, back-links and share buttons
        for t in body.select('#toc, .text-center, div.top, a[href="#toc"]'): t.decompose()
        for a in body.find_all('a', string=re.compile(r'^\s*(Table of Contents|Back to Table of Contents|Share on \w+)\s*$')):
            par=a.parent; a.decompose()
            if par and not par.get_text(strip=True): par.decompose()
    from urllib.parse import urljoin, urlparse, parse_qs, unquote
    for img in body.find_all('img'):
        src=img.get('src','')
        if '/_next/image' in src: src=unquote(parse_qs(urlparse(src).query).get('url',[src])[0])
        src=urljoin(u,src)
        if 'ia.samaltman.com/images/cover' in src:
            (img.find_parent('figure') or img).decompose(); continue
        src=re.sub(r'/(medium|large|small|thumb)_([^/]+)$',r'/\2',src)   # Posthaven: use the full-size original
        img['src']=src
        for c in ('class','style','width','height','loading','decoding'): img.attrs.pop(c,None)
        for a in [k for k in img.attrs if k.startswith('data-') or k in ('srcset','sizes')]: del img[a]
    for t in body.find_all(True):
        if t.name in ('article','section','main'): t.name='div'
        for a in ('class','style','id'):
            if not (a=='id' and t.name=='a'): t.attrs.pop(a,None)
    BLOCK=['p','div','ul','ol','blockquote','h1','h2','h3','h4','h5','h6','table','figure','pre','hr','img','iframe','video','section']
    for d in body.find_all('div'):
        if d is not body and not d.find(BLOCK): d.name='p'      # Posthaven writes many paragraphs as bare <div>s
    for d in [body]+body.find_all(['div','section']):            # loose text beside blocks -> its own paragraph
        run=[]
        def flush():
            if run and any((x.get_text() if hasattr(x,'get_text') else str(x)).strip() for x in run):
                p=body.new_tag('p'); run[0].insert_before(p)
                for x in run: p.append(x.extract())
            run.clear()
        for c in list(d.children):
            if getattr(c,'name',None) in BLOCK: flush()
            elif getattr(c,'name',None)=='br' and run and getattr(run[-1],'name',None)=='br': run.pop(); flush()
            else: run.append(c)
        if any(getattr(c,'name',None) in BLOCK for c in d.children): flush()
        else: run.clear()
    tidy(body, slug_of(u,title))
    for p in body.find_all(['p','div']):
        if not p.get_text(strip=True) and not p.find(['img','iframe','video','hr']): p.decompose()
    def edge(br,attr):   # only whitespace / other <br>s between this br and the edge of its block
        x=getattr(br,attr)
        while x is not None:
            if getattr(x,'name',None)=='br' or (isinstance(x,str) and not x.strip()): x=getattr(x,attr); continue
            return False
        return True
    for br in body.find_all('br'):
        if br.parent.name in ('div','section','body') or edge(br,'next_sibling') or edge(br,'previous_sibling'): br.decompose()
    words=len(body.get_text(' ').split())
    slug=slug_of(u,title)
    return dict(ts=ts,title=title,url=u,slug=slug,html=str(body),words=words,
                date=datetime.datetime.fromtimestamp(ts,datetime.UTC).strftime('%B %Y') if ts else '')
guide_urls=[l.strip() for l in open('guide.txt') if l.strip() and not l.startswith('#')] if pathlib.Path('guide.txt').exists() else []
with ThreadPoolExecutor(8) as ex: posts=list(ex.map(fetch,urls)); guides=list(ex.map(fetch,guide_urls))
posts.sort(key=lambda p:p['ts'], reverse=True)
for g in guides: g['guide']=True; g['date']=g['date'] or "A founder's guide"
n_essays=len(posts); posts+=guides
fm_md=open('frontmatter.md').read()
fm_html=subprocess.run(['pandoc','-f','markdown','-t','html'],input=fm_md,capture_output=True,text=True,check=True).stdout
fm_html=fm_html.replace('<h1 ','<h1 class="unlisted" ',1).replace('<h1>','<h1 class="unlisted">',1)
D=pathlib.Path('dist'); D.mkdir(exist_ok=True)
json.dump(posts,open(D/'posts.json','w'))
total=sum(p['words'] for p in posts)

# Images: download once, shrink to a sensible size, embed locally (keeps the EPUB/PDF small)
from PIL import Image; import hashlib, io
IMG=D/'img'; IMG.mkdir(exist_ok=True)
def local(src):
    out=IMG/(hashlib.sha1(src.encode()).hexdigest()[:12]+'.jpg')
    if not out.exists():
        im=Image.open(io.BytesIO(S.get(src,timeout=60).content))
        if im.mode in ('RGBA','LA','P'):
            im=im.convert('RGBA'); bg=Image.new('RGB',im.size,'white'); bg.paste(im,mask=im.split()[-1]); im=bg
        im=im.convert('RGB'); im.thumbnail((1400,1400)); im.save(out,'JPEG',quality=82,optimize=True)
    return str(out.resolve())
def localize(h):
    return re.sub(r'(<img[^>]*?src=")([^"]+)(")',lambda m:m.group(1)+local(H.unescape(m.group(2)))+m.group(3),h)
for p in posts: p['book_html']=localize(p['html'])

# EPUB
contents=''.join(f'<li><a href="#{p["slug"]}">{H.escape(p["title"])}</a></li>' for p in posts)
book=['<html><head><meta charset="utf-8"><title>The Essays</title></head><body>',
      f'<section class="front">{fm_html}</section>',
      f'<h1 id="contents" class="unlisted">Contents</h1><div class="contents"><ol>{contents}</ol></div>']
for p in posts:
    book.append(f'<h1 id="{p["slug"]}">{H.escape(p["title"])}</h1><div class="meta"><p>{p["date"]} · <a href="{p["url"]}">Read the original</a></p></div>{p["book_html"]}')
book.append('</body></html>')
(D/'altman.html').write_text('\n'.join(book))
meta=['--metadata','title=The Essays','--metadata','author=Sam Altman','--metadata','lang=en',
      '--metadata',"description=Sam Altman's essays on startups, ambition and the future, collected in one book."]
subprocess.run(['pandoc',str(D/'altman.html'),'-o',str(D/'altman.epub'),'--epub-title-page=false','--epub-embed-font=art/fonts/EBGaramond.ttf','--epub-embed-font=art/fonts/EBGaramond-Italic.ttf','--split-level=1',
  '--epub-cover-image=cover.jpg','--css=epub.css',*meta],check=True)

# Markdown: one file per essay, zipped
with zipfile.ZipFile(D/'altman-markdown.zip','w',zipfile.ZIP_DEFLATED) as z:
    z.writestr('altman-essays/00-about.md',fm_md)
    for i,p in enumerate(posts,1):
        md=subprocess.run(['pandoc','-f','html','-t','gfm','--wrap=none'],input=p['html'],capture_output=True,text=True,check=True).stdout
        z.writestr(f'altman-essays/{i:02d}-{p["slug"]}.md',f'# {p["title"]}\n\n*{p["date"]} · [original]({p["url"]})*\n\n{md}')

# PDF (book layout via WeasyPrint)
import weasyprint
toc=''.join(f'<li><a href="#{p["slug"]}">{H.escape(p["title"])}</a><span>{p["date"]}</span></li>' for p in posts)
chap=''.join(f'<section class="essay" id="{p["slug"]}"><h1>{H.escape(p["title"])}</h1><p class="meta">{p["date"]} · <a href="{p["url"]}">Read the original</a></p>{p["book_html"]}</section>' for p in posts)
pdf_html=f'''<html><head><meta charset="utf-8"><style>{open("pdf.css").read()}</style></head><body>
<div class="cover"><img src="cover.jpg"></div>
<div class="front">{fm_html}</div>
<div class="toc"><h2>Contents</h2><ol>{toc}</ol></div>{chap}</body></html>'''
weasyprint.HTML(string=pdf_html,base_url='.').write_pdf(D/'altman.pdf')
# Safety check: if anything looks wrong, fail here so the workflow never publishes a broken book
problems=[f'{p["url"]}: only {p["words"]} words' for p in posts if p['words']<80]
problems+=[f'{p["url"]}: no date' for p in posts if not p['ts']]
if len(posts)!=len(urls): problems.append(f'expected {len(urls)} essays, got {len(posts)}')
for f,mb in (('altman.epub',1),('altman.pdf',1)):
    if (D/f).stat().st_size<mb*1_000_000: problems.append(f'{f} is suspiciously small')
if problems: raise SystemExit('Build stopped, nothing published:\n'+'\n'.join(problems))
print(f'built {n_essays} essays + {len(guides)} guide, {total:,} words')
