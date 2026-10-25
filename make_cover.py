"""Draws cover.jpg (1600x2560) from the IA painting.

Design logic
- The painting is the cover. Type only goes where the paint is calm and continuous: the sky.
- The road is a leading line that runs from the reader to the horizon; the title sits just
  above the vanishing point so the eye travels up the road into it.
- Two typefaces: EB Garamond (title), Inter (author). Two colours: ink navy, paper cream.
- Author is a known name, so it is strong (about 30% of title size), but the title leads.
- Nothing that changes over time (count, years) is printed on the cover.
Usage: python3 make_cover.py [sky|split]
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
ROOT=os.path.dirname(os.path.abspath(__file__)); A=lambda p:os.path.join(ROOT,'art',p)
W,H=1600,2560
INK=(20,29,56); CREAM=(250,246,236)
def font(name,size,wght=None,opsz=None):
    f=ImageFont.truetype(A(f'fonts/{name}.ttf'),size)
    if wght or opsz: f.set_variation_by_axes([opsz if a['name']==b'Optical size' else (wght or a['default']) for a in f.get_variation_axes()])
    return f
def center(d,s,f,y,fill,track=0):
    ws=[d.textlength(c,font=f) for c in s]; tw=sum(ws)+track*(len(s)-1); x=(W-tw)/2
    for c,w in zip(s,ws): d.text((x,y),c,font=f,fill=fill); x+=w+track
    return tw
def vramp(y0,y1,peak,curve):
    m=Image.new('L',(W,H),0); d=ImageDraw.Draw(m)
    lo,hi=sorted((y0,y1))
    for y in range(lo,hi): d.line((0,y,W,y),fill=int(peak*((y-y0)/(y1-y0))**curve))
    return m

def base():
    src=Image.open(A('ia-painting.png')).convert('RGB')
    img=src.resize((W,round(src.height*W/src.width)),Image.LANCZOS).crop((0,0,W,H))
    img=img.filter(ImageFilter.UnsharpMask(1.6,45,2))
    # very gentle lift of the upper sky only, so navy type sits on even tone
    return Image.composite(Image.new('RGB',(W,H),CREAM),img,vramp(700,0,90,1.2))

def panel():
    # painting on top, fading into a cream panel that holds the title
    src=Image.open(A('ia-painting.png')).convert('RGB')
    img=src.resize((W,round(src.height*W/src.width)),Image.LANCZOS)
    off=440; img=img.crop((0,off,W,off+H))
    img=img.filter(ImageFilter.UnsharpMask(1.6,45,2))
    paper=Image.new('RGB',(W,H),CREAM)
    img=Image.composite(paper,img,vramp(330,0,150,1.0))      # calm the strip of sky behind the author
    m=vramp(1720,1980,255,1.6); ImageDraw.Draw(m).rectangle((0,1980,W,H),fill=255)
    return Image.composite(paper,img,m)

def build(style):
    if style=='panel':
        img=panel(); d=ImageDraw.Draw(img)
        center(d,'SAM ALTMAN',font('Inter',64,650,32),130,INK,track=22)
        center(d,'The Essays',font('EBGaramond',250,500),2010,INK)
        center(d,'On startups, ambition, and the future',font('EBGaramond-Italic',66,450),2330,(44,52,82))
        return img
    img=base()
    title=font('EBGaramond',250,500); author=font('Inter',62,600,32)
    if style=='split':
        # author sits on the pale road where it opens toward the reader
        d=ImageDraw.Draw(img)
        center(d,'The Essays',title,300,INK)
        center(d,'SAM ALTMAN',font('Inter',70,700,32),H-215,INK,track=20)
    elif style=='subtitle':
        d=ImageDraw.Draw(img)
        center(d,'SAM ALTMAN',author,170,INK,track=20)
        center(d,'The Essays',title,320,INK)
        center(d,'On startups, ambition, and the future',font('EBGaramond-Italic',58,400),630,(58,64,88))
    else:
        d=ImageDraw.Draw(img)
        center(d,'SAM ALTMAN',author,190,INK,track=20)
        center(d,'The Essays',title,350,INK)
    return img

if __name__=='__main__':
    s=sys.argv[1] if len(sys.argv)>1 else 'panel'
    if s=='all':
        for k in ['sky','split','subtitle']: build(k).save(A(f'v_{k}.jpg'),quality=92)
    else:
        build(s).save(os.path.join(ROOT,'cover.jpg'),quality=90,optimize=True,progressive=True)
