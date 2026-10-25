"""Draws cover.png (1600x2560): a dawn horizon, the title in serif, quiet type."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H=1600,2560
F='/usr/share/fonts/opentype/urw-base35/'
serif=lambda s:ImageFont.truetype(F+'P052-Roman.otf',s)
ital=lambda s:ImageFont.truetype(F+'P052-Italic.otf',s)
sans=lambda s:ImageFont.truetype(F+'NimbusSans-Regular.otf',s)
N=sum(1 for l in open('posts.txt') if l.strip() and not l.startswith('#'))
img=Image.new('RGB',(W,H))
px=img.load()
top,bot=(14,15,20),(34,26,30)
for y in range(H):
    t=y/H; c=tuple(int(top[i]+(bot[i]-top[i])*t) for i in range(3))
    for x in range(W): px[x,y]=c
# sun glow rising from horizon
hy=1700
glow=Image.new('L',(W,H),0); g=ImageDraw.Draw(glow)
for r in range(900,0,-6):
    g.ellipse((W/2-r,hy-r,W/2+r,hy+r),fill=int(255*(1-r/900)**2.2))
glow=glow.filter(ImageFilter.GaussianBlur(30))
warm=Image.new('RGB',(W,H),(236,120,62))
img=Image.composite(warm,img,glow.point(lambda v:int(v*0.75)))
d=ImageDraw.Draw(img)
d.ellipse((W/2-230,hy-230,W/2+230,hy+230),fill=(246,170,98))
d.rectangle((0,hy,W,H),fill=(16,15,19))
d.line((160,hy,W-160,hy),fill=(246,170,98),width=3)
# reflection lines
for i,y in enumerate(range(hy+40,hy+260,36)):
    w=300-i*45
    d.line((W/2-w,y,W/2+w,y),fill=(90,58,45),width=4)
def center(text,font,y,fill,track=0):
    if track:
        widths=[d.textlength(ch,font=font) for ch in text]; tw=sum(widths)+track*(len(text)-1); x=(W-tw)/2
        for ch,w in zip(text,widths): d.text((x,y),ch,font=font,fill=fill); x+=w+track
    else:
        d.text(((W-d.textlength(text,font=font))/2,y),text,font=font,fill=fill)
cream=(240,232,218); muted=(160,150,140)
center('SAM ALTMAN',sans(58),260,cream,track=22)
d.line((W/2-60,370,W/2+60,370),fill=(246,170,98),width=3)
center('The',ital(150),470,cream)
center('Essays',serif(300),610,cream)
center('On startups, ambition, and the future',ital(64),1010,muted)
center(f'{N} ESSAYS  ·  2013 – 2026',sans(44),2230,muted,track=8)
center('blog.samaltman.com',sans(38),2320,(110,102,96),track=4)
img.save('cover.png',optimize=True)
