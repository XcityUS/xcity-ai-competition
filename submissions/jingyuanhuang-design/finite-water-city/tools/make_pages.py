"""Original graphic pages; no generated or third-party imagery."""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import textwrap,json
P=Path(__file__).resolve().parents[1];(P/'pages').mkdir(exist_ok=True)
W,H=2400,1697;BG='#F0EBDD';INK='#163D50';MUT='#586466';GOLD='#C38B4F';RED='#9C513B'
def font(n,b=False):return ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial'+(' Bold' if b else '')+'.ttf',n)
def page(k,title,sub):
 im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
 d.text((105,80),'XCITY / AGUA FINITA',font=font(29,True),fill=INK);d.text((W-530,80),k,font=font(27),fill=MUT)
 d.line((105,145,2295,145),fill=INK,width=3);d.text((100,195),title,font=font(84,True),fill=INK);d.text((105,310),sub,font=font(31),fill=MUT)
 d.line((105,1580,2295,1580),fill=INK,width=2);d.text((105,1615),'JINGYUAN HUANG + CODEX   /   25 OCT 2026   /   PREVIEW SCHEME',font=font(22),fill=MUT)
 return im,d
def wrap(d,x,y,s,width=58,size=32,color=INK):
 for line in textwrap.wrap(s,width=width):d.text((x,y),line,font=font(size),fill=color);y+=size*1.45
 return y
im,d=page('01 / POSITION','AGUA FINITA','The Finite Water City / San Juan, Argentina')
d.arc((120,480,830,1190),30,330,fill=INK,width=65);d.line((150,1060,850,1060),fill=GOLD,width=28)
d.text((1040,500),'A CITY THAT',font=font(110,True),fill=INK);d.text((1040,635),'CAN SAY:',font=font(110,True),fill=INK);d.text((1040,770),'ENOUGH.',font=font(140,True),fill=GOLD)
wrap(d,1040,1010,'Growth follows a public water ledger. Shade, homes and essential services come before another server hall.',width=43,size=39)
for x,n,l in [(130,'B03','HEAT WITHOUT THIRST'),(870,'C03','THE ABSENT RIVER'),(1610,'A03','THE RIGHT TO SHADE')]:d.text((x,1340),n,font=font(70,True),fill=INK);d.text((x,1445),l,font=font(28,True),fill=MUT)
# Wide cover sized for the organiser's hero panel, avoiding crop loss.
im=Image.new('RGB',(2400,1050),BG);d=ImageDraw.Draw(im)
d.arc((130,160,830,860),30,330,fill=INK,width=62);d.line((155,730,850,730),fill=GOLD,width=26)
d.text((1030,180),'A CITY THAT',font=font(110,True),fill=INK);d.text((1030,320),'CAN SAY:',font=font(110,True),fill=INK);d.text((1030,460),'ENOUGH.',font=font(140,True),fill=GOLD)
wrap(d,1040,690,'Growth follows a public water ledger. Shade, homes and essential services come before another server hall.',width=43,size=38)
im.save(P/'pages/cover.png')
im,d=page('02 / WATER COVENANT','Water is a public limit.','Assumed annual phase-one operating ledger; all values are m3/year.')
for x,num,l in [(110,'840,000','FRESH INPUT'),(880,'200,000','INTERNAL REUSE'),(1650,'1,000,000','GROSS END USE')]:
 d.text((x,465),num,font=font(100,True),fill=INK);d.text((x,595),l,font=font(28,True),fill=MUT)
wrap(d,110,700,'40,000 distribution loss leaves 800,000 fresh delivered. Reuse supplies the other 200,000. The same reclaimed water is not a new external source.',width=105,size=32)
uses=[('Agriculture + panel cleaning',778263.2,GOLD),('Domestic + community',140160,INK),('Industry',60000,'#738C8F'),('Landscape',20000,'#A7B7A8'),('Compute makeup',1576.8,RED)]
x=110
for name,v,c in uses:
 w=int(2180*v/1000000);d.rectangle((x,900,x+w,1020),fill=c);x+=w
for i,(name,v,c) in enumerate(uses):
 col=i%3;row=i//3;x=110+col*750;y=1080+row*145
 d.rectangle((x,y+8,x+18,y+26),fill=c);d.text((x+35,y),name,font=font(28),fill=INK);d.text((x+35,y+45),f'{v:,.1f}',font=font(42,True),fill=c)
wrap(d,110,1410,'A 30% shortfall stops new irrigation and processing first. Essential-needs review governs emergency household conservation. Pilot operations remain protected.',width=112,size=28)
im.save(P/'pages/water-covenant.png')
im,d=page('03 / THE FIRST ROAD','No road is assumed to exist.','Conceptual connection diagram / not a surveyed alignment, easement or approved route.')
pts=[(290,800),(1050,800),(1940,800)]
d.line((290,800,1050,800),fill=GOLD,width=14);d.line((1050,800,1940,800),fill=INK,width=14)
for x,y in pts:d.ellipse((x-20,y-20,x+20,y+20),fill=INK)
d.text((170,650),'RN40',font=font(65,True),fill=INK);d.text((870,650),'SITE EDGE',font=font(65,True),fill=INK);d.text((1700,650),'CUENCA UNO',font=font(65,True),fill=INK)
wrap(d,110,925,'OFF SITE: 80 km assumed allowance, 8 m carriageway. 640,000 m2 pavement quantity. Requires alignment comparison, easements, crossings, funding and emergency access.',width=48,size=34)
wrap(d,1300,925,'ON SITE: the submitted service route connects the boundary to the productive edge. All GeoJSON remains within the competition site. People enter the shaded public network at gated interfaces.',width=48,size=34)
wrap(d,110,1310,'27.6 km is the nearest distance from ANY site boundary to RN40. It is not the road length from the proposed settlement. The eastern RP510 alternative remains conditional.',width=110,size=34,color=RED)
im.save(P/'pages/access.png')
print('Created 3 original pages')
