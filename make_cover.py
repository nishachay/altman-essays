"""Draws cover.jpg (1600x2560): painted dawn seascape with the title set over the sky."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H=1600,2560
F='/usr/share/fonts/opentype/urw-base35/'
serif=lambda s:ImageFont.truetype(F+'P052-Roman.otf',s)
ital=lambda s:ImageFont.truetype(F+'P052-Italic.otf',s)
sans=lambda s:ImageFont.truetype(F+'NimbusSans-Regular.otf',s)
N=sum(1 for l in open('posts.txt') if l.strip() and not l.startswith('#'))
img=Image.open('art/cover-art.jpg').convert('RGB').resize((W,H))
# soft darkening at the top so the type reads
shade=Image.new('L',(W,H),0); sd=ImageDraw.Draw(shade)
for y in range(1300): sd.line((0,y,W,y),fill=int(120*(1-y/1300)**1.6))
for y in range(2150,H): sd.line((0,y,W,y),fill=int(170*((y-2150)/(H-2150))**1.3))
img=Image.composite(Image.new('RGB',(W,H),(8,12,20)),img,shade)
d=ImageDraw.Draw(img)
def center(text,font,y,fill,track=0):
    widths=[d.textlength(ch,font=font) for ch in text]; tw=sum(widths)+track*(len(text)-1); x=(W-tw)/2
    for ch,w in zip(text,widths): d.text((x,y),ch,font=font,fill=fill); x+=w+track
cream=(244,236,222); soft=(214,204,190); gold=(232,176,112)
center('SAM ALTMAN',sans(60),250,cream,track=26)
d.line((W/2-70,360,W/2+70,360),fill=gold,width=3)
center('The',ital(140),450,cream)
center('Essays',serif(290),580,cream)
center('On startups, ambition, and the future',ital(62),960,soft)
center(f'{N} ESSAYS   ·   2013 – 2026',sans(44),2380,cream,track=8)
img.save('cover.jpg',quality=86,optimize=True,progressive=True)
