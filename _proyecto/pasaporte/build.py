import os as _os; _os.makedirs(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)),'img'),exist_ok=True)
import json, os, io, segno, html
from PIL import Image
R='/home/claude/marmar1926.github.io'; S=os.path.dirname(os.path.abspath(__file__))
m=json.load(open(f'{R}/_proyecto/manifest.json',encoding='utf-8'))
hexc=lambda c:'#%02X%02X%02X'%tuple(c)
T=m['trips']; y2t={}
for k,v in T.items(): y2t.setdefault(v['year'],k)
ink=lambda c: '#A87D00' if c.upper()=='#F1C40F' else c
def qr(url):
    q=segno.make(url,error='m'); b=io.BytesIO(); q.save(b,kind='svg',scale=1,border=0,xmldecl=False,svgns=True,nl=False,dark='#2B2620',omitsize=True); return b.getvalue().decode()
groups=[]
for e in m['entries']:
    if not groups or groups[-1][0]!=e['trip']: groups.append((e['trip'],[]))
    groups[-1][1].append(e)
import re, sys
sys.path.insert(0,S)
from stamps import round_stamp, rect_stamp
from stamps import oval_stamp, anaheim_stamp, wdw_stamp
DATES=json.load(open(f'{S}/dates.json'))
ABBR={'Florida':'FL','New York':'NY','Massachusetts':'MA','California':'CA','Nevada':'NV','Arizona':'AZ','Georgia':'GA','South Dakota':'SD','Wyoming':'WY','Washington':'WA','Utah':'UT'}
def ink2(c):
    c=c.lstrip('#'); r,g,b=[int(c[i:i+2],16) for i in (0,2,4)]; k=0.78
    return '#%02X%02X%02X'%(int(r*k),int(g*k),int(b*k))
def stamps_for(e,vis):
    state=e.get('sub','').split(',')[-1].strip(); ab=ABBR.get(state,'')
    nm=e['name'].upper().replace('NATIONAL PARK',"NAT'L PARK").replace('STATE PARK','S.P.').replace('MEMORIAL','MEM.')
    SHOW_WDW=False  # sellos propios 'WALT DISNEY WORLD' retirados temporalmente
    if e['number']==5:
        return [f'<div class="dlimg"><img src="file://{S}/sello_disneyland.png"></div>']
    if e['number']==2:
        G='#2E7D32'; P=DATES['_parks']['2019']
        def fd(x): dd,mm,yy=x.split('/'); return f"{int(dd):02d} {['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'][int(mm)-1]} {yy}"
        def at(x,y,w,inner,rot): return f'<div class="dwi" style="left:{x}mm;top:{y}mm;width:{w}mm;height:{w}mm;transform:rotate({rot}deg)">{inner}</div>'
        def img(f): return f'<img src="file://{S}/{f}">'
        def g(park,code,u,rot): return wdw_stamp(u,G,fd(P[code]),park=park,rot=0)
        ov=(at(50,48,19,img('sello_epcot.png'),8)+at(74,48,21,g('EPCOT','EP',201,0),-9)
            +at(48,65,25,img('sello_magic_kingdom.png'),-5)+at(75,64,21,g('MAGIC KINGDOM','MK',202,0),11)
            +at(34,127,16,img('sello_hollywood_studios.png'),7)+at(48,126,18,g('HOLLYWOOD STUDIOS','HS',203,0),-12)
            +at(63,127,17,img('sello_animal_kingdom.png'),-4)+at(77,125,18,g('ANIMAL KINGDOM','AK',204,0),9))
        return [f'<div class="dwov">{ov}</div>','']
    out=[]
    for i,(y,cc) in enumerate(vis):
        d=DATES.get(f"{e['number']}-{y}") or str(y); d=d if isinstance(d,str) else str(y); ink=ink2(cc); u=e['number']*10+i
        if i==0: out.append(round_stamp(u,ink,f"{nm} · {state.upper()}",d))
        elif i==1: out.append(rect_stamp(u,ink,f"{nm} · {ab}" if ab else nm,d,'VISITOR · ADMITTED'))
        else: out.append(oval_stamp(u,ink,'',d,f"{nm} · {ab} · USA"))
    import random as _r
    rng=_r.Random(e['number']*7919)
    def jit(svg):
        rot=rng.uniform(6,20)*rng.choice([-1,1]); dx=rng.uniform(-1.5,1.5); dy=rng.uniform(-1.2,1.2)
        return re.sub(r'style="--rot:[^"]*"', f'style="--rot:{rot:.1f}deg;--dx:{dx:.2f}mm;--dy:{dy:.2f}mm"', svg, count=1)
    return [jit(x) for x in out]
B=json.load(open(f'{S}/blurbs2.json',encoding='utf-8'))
YOSE='Yosemite fue el primer territorio que el gobierno de Estados Unidos protegió para el disfrute público: Abraham Lincoln firmó en 1864 la ley que preservaba el valle, años antes de que existieran los parques nacionales.'
def texts(e):
    k=str(e['number'])
    h=open(f"{R}/{e['trip']}/{e['slug']}/index.html",encoding='utf-8').read()
    st=re.search(r'<div class="story">(.*?)</div>',h,re.S)
    if k in B and (k=='14' or not st): return B[k][0], B[k][1]
    para=re.sub(r'<[^>]+>','',re.findall(r'<p>(.*?)</p>',st.group(1),re.S)[0]).strip()
    f=re.search(r'<div class="fact-box">(.*?)</div>',h,re.S)
    d=re.sub(r'^Dato curioso:\s*','',re.sub(r'<[^>]+>','',f.group(1)).strip())
    return para, d[0].upper()+d[1:]
rows=[]
for trip,es in groups:
    t=T[trip]; c=hexc(t['color'])
    nums=f"{es[0]['number']} – {es[-1]['number']}"
    rows.append(f'<section class="div" style="--c:{c}"><div class="dband"></div><p class="dy">{t["year"]}</p><h2>{html.escape(t["label"])}</h2><p class="dn">{len(es)} lugares · del {nums.replace(" – "," al ")}</p><ul>'+''.join(f"<li><span>{x['number']}</span>{html.escape(x['name'])}</li>" for x in es)+'</ul></section>')
    for e in es:
        im=Image.open(f"{R}/{e['trip']}/{e['slug']}/hero.jpg").convert('RGB'); w,h=im.size
        tw,th=1240,640; r=max(tw/w,th/h); im=im.resize((round(w*r),round(h*r)),Image.LANCZOS); w,h=im.size
        FOCUS={}; fy=FOCUS.get(e['number'],0.5); y0=round((h-th)*fy)
        if e['number'] in (9,42):   # cartel completo sobre fondo desenfocado (Beverly Hills, Seligman)
            from PIL import ImageFilter
            src=Image.open(f"{R}/{e['trip']}/{e['slug']}/hero.jpg").convert('RGB')
            bg=im.crop(((w-tw)//2,(h-th)//2,(w-tw)//2+tw,(h-th)//2+th)).filter(ImageFilter.GaussianBlur(18))
            sw,sh=src.size; crop=src.crop((0,int(sh*(0 if e['number']==9 else 0.08)),sw,int(sh*(0.78 if e['number']==9 else 0.85)))); k=min(tw/crop.width,(th-10)/crop.height); crop=crop.resize((round(crop.width*k),round(crop.height*k)),Image.LANCZOS)
            bg.paste(crop,((tw-crop.width)//2,(th-crop.height)//2)); im=bg
        else:
            im=im.crop(((w-tw)//2,y0,(w-tw)//2+tw,y0+th))
        fn=f"img/{e['number']:02d}.jpg"; im.save(f'{S}/{fn}',quality=88)
        vis=[(t['year'],c)]+[(v['year'],hexc(T[y2t[v['year']]]['color']) if v['year'] in y2t else hexc(v['color'])) for v in e.get('extra_visits',[])]
        yrs=''.join(f'<span class="yp" style="--yc:{cc};color:{ink(cc)}">{y}</span>' for y,cc in vis)
        url=f"https://marmar1926.github.io/{e['trip']}/{e['slug']}/"
        ST=stamps_for(e,vis)
        rows.append(f'''<section class="place" data-n="{e['number']}" style="--c:{c}"><div class="ph"><img src="{fn}"><span class="num">{e['number']}</span></div>
<div class="stamps">{ST[0]}</div><div class="body"><h3>{html.escape(e['name'])}</h3><p class="sub">{html.escape(e.get('sub',''))}</p><div class="yrs"{' style="margin-bottom:25mm"' if e["number"]==2 else ""}>{yrs}</div>
<p class="txt">{html.escape(texts(e)[0])}</p><p class="dato"><b>Dato curioso:</b> {html.escape(texts(e)[1])}</p></div>
<div class="foot"><div class="qr">{qr(url)}</div>{"" if (len(ST)>2 or e["number"]==2) else "<p>Escaneá el código para ver nuestras fotos y la historia completa.</p>"}{"".join(ST[1:])}</div></section>''')
TL=[x[1:] for x in sorted([(v['year'],i,v['year'],hexc(v['color']),v['label']) for i,v in enumerate(T.values())]+[(2019,0,2019,'#17A2B8','Miami - Disney 2019')])]

TRIPS_KM=[('#D81B60','Disney & Miami Vibes','MAR 2012','1.132'),('#2EA043','La Ruta del Este','OCT 2012','865'),
 ('#E67E22','Triángulo Dorado de la Costa Oeste','JUN 2013','1.258'),('#2E7CF6','Palmeras y magnolias','JUN 2016','2.975'),
 ('#DC322F','Ruta de Gigantes y Géiseres','JUN 2018','6.117'),('#17A2B8','Miami - Disney 2019','JUN 2019','427'),
 ('#F1C40F','Ruta de Gigantes: Del Pacífico al Gran Cañón','OCT 2022','2.260')]
trows=''.join(f'<tr><td><span class="tdot" style="--c:{c}"></span></td><td><b>{html.escape(n)}</b><br><span>{d}</span></td><td class="km">{k}</td></tr>' for c,n,d,k in TRIPS_KM)
STATS=(f'<section class="stats"><h2>La gira en números</h2><p class="st-sub">Mis viajes por USA · 2012 – 2022</p>'
 '<div class="big4"><div><b>7</b><span>viajes</span></div><div><b>45</b><span>lugares</span></div><div><b>15.034</b><span>km</span></div><div><b>15</b><span>estados</span></div></div>'
 f'<table class="trips"><thead><tr><th></th><th>Viaje</th><th>Km</th></tr></thead><tbody>{trows}</tbody><tfoot><tr><td></td><td>Total</td><td class="km">15.034</td></tr></tfoot></table>'
 '<div class="rec"><b>El viaje más largo:</b> Ruta de Gigantes y Géiseres (2018): 6.117 km en 21 días, 31 paradas y 10 estados cruzados (CA · NV · AZ · UT · WY · SD · MT · ID · WA · OR).</div></section>')

FIRMAS=('<section class="firmas"><h2>Viajeros</h2><p class="st-sub">Firmas de los titulares de este pasaporte</p>'
 +''.join('<div class="sig"><div class="sl"></div><span>Firma</span><div class="sl"></div><span>Nombre</span></div>' for _ in range(4))
 +'</section><section class="firmas"><h2>Próximos sellos</h2><p class="st-sub">Para los viajes que todavía no hicimos</p><div class="vis">'
 +''.join('<div class="vb"><span>Lugar</span><div class="vl"></div><span>Fecha</span><div class="vl"></div></div>' for _ in range(6))
 +'</div></section>')
legend=''.join(f'<li><span class="tdot" style="--c:{c}"></span>{html.escape(l)} <i>{y}</i></li>' for _,y,c,l in TL)
home=qr('https://marmar1926.github.io/')
stripes=''.join(f'<span style="background:{c}"></span>' for _,y,c,l in TL)
doc=f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><style>
@font-face{{font-family:Play;src:url("file://{S}/fonts/PlayfairDisplay.ttf");}}
@font-face{{font-family:Cav;src:url("file://{S}/fonts/Caveat.ttf");}}
@font-face{{font-family:SpEl;src:url("file://{S}/fonts/SpecialElite.woff2");}}
@font-face{{font-family:Src;src:url("file://{S}/fonts/SourceSans3.ttf");}}
@page{{size:105mm 148mm;margin:0}}
section{{width:105mm;height:148mm;padding:9mm 8mm 10mm;overflow:hidden;position:relative;break-after:page;page-break-after:always}}
section:last-child{{break-after:auto;page-break-after:auto}}
*{{box-sizing:border-box}} html,body{{margin:0;font-family:Src,sans-serif;color:#2B2620;}}
.cover{{padding:0;background:#F7F2E7;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;page-break-after:always;position:relative}}
.stripes{{position:absolute;left:0;right:0;display:flex;height:5mm}} .stripes span{{flex:1}} .stripes.t{{top:0}} .stripes.b{{bottom:0}}
.cover h1{{font-family:Cav;font-weight:700;font-size:34pt;color:#1D2B5B;margin:0 0 2mm;line-height:1}}
.cover p{{margin:0;font-size:9pt;color:#6B6255;letter-spacing:.3px}}
.cover .big{{font-family:Play;font-weight:700;font-size:13pt;color:#2B2620;margin:6mm 0 1mm}}
.cover .qr{{width:24mm;height:24mm;margin:8mm auto 2mm}} .cover .qr svg{{width:100%;height:100%}}
.cover small{{font-size:7pt;color:#6B6255}}
.intro h2{{font-family:Play;font-size:13pt;margin:0 0 3mm}} .intro p{{font-size:8.6pt;line-height:1.45;margin:0 0 3mm}}
.intro ul{{list-style:none;padding:0;margin:3mm 0 0;font-size:8.2pt}} .intro li{{display:flex;align-items:center;gap:2mm;margin:0 0 1.8mm}} .intro i{{color:#6B6255;font-style:normal}}
.tdot{{width:3mm;height:3mm;border-radius:50%;background:var(--c);flex:0 0 3mm;display:inline-block}}
.trip{{display:flex;align-items:center;gap:2mm;border-bottom:.5mm solid var(--c);padding:0 0 1.5mm;margin:4mm 0 2mm;font-size:9pt;break-after:avoid;page-break-after:avoid}}
.trip:first-child{{margin-top:0}} .trip .ty{{color:#6B6255;margin-left:1.5mm}}
.trip.newpage{{break-before:page;page-break-before:always;margin-top:0}}
.row{{display:flex;align-items:center;gap:2.2mm;padding:1.6mm 0;border-bottom:.2mm solid #E4DCC9;break-inside:avoid;page-break-inside:avoid}}
.num{{width:5.2mm;height:5.2mm;border-radius:50%;background:var(--c);color:#fff;font-size:6.8pt;font-weight:700;display:flex;align-items:center;justify-content:center;flex:0 0 5.2mm}}
.row img{{width:14mm;height:14mm;border-radius:1.2mm;object-fit:cover;flex:0 0 14mm}}
.info{{flex:1;display:flex;flex-direction:column;min-width:0;line-height:1.2}} .info b{{font-size:8.6pt}} .sub{{font-size:6.8pt;color:#6B6255}} .yrs{{font-size:6.8pt;font-weight:700;margin-top:.4mm}}
.row .qr{{width:15mm;height:15mm;flex:0 0 15mm}} .row .qr svg{{width:100%;height:100%;display:block}}
.back{{display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}}
.back .qr{{width:30mm;height:30mm;margin:0 auto 3mm}} .back .qr svg{{width:100%;height:100%}} .back p{{font-size:8pt;color:#6B6255;margin:1mm 0}}
.notes{{}} .notes h2{{font-family:Cav;font-size:18pt;margin:0 0 3mm;color:#1D2B5B}} .notes div{{border-bottom:.2mm solid #D9CFB8;height:8mm}}


.div{{display:flex;flex-direction:column;justify-content:center}}
.dband{{position:absolute;top:0;left:0;right:0;height:6mm;background:var(--c)}}
.div .dy{{font-family:Cav;font-size:30pt;color:var(--c);margin:0;line-height:1}}
.div h2{{font-family:Play;font-size:14pt;margin:1mm 0 2mm;line-height:1.2}}
.div .dn{{font-size:8pt;color:#6B6255;margin:0 0 4mm}}
.div ul{{list-style:none;padding:0;margin:0;columns:2;column-gap:4mm;font-size:7.6pt}}
.div li{{display:flex;align-items:center;gap:1.6mm;margin:0 0 1.6mm;break-inside:avoid}}
.div li span{{width:4.4mm;height:4.4mm;border-radius:50%;background:var(--c);color:#fff;font-size:6pt;font-weight:700;display:inline-flex;align-items:center;justify-content:center;flex:0 0 4.4mm}}
.ph{{position:relative;margin:-9mm -8mm 0;height:54mm;overflow:hidden;border-bottom:1.6mm solid var(--c)}}
.ph img{{width:100%;height:100%;object-fit:cover;display:block}}
.ph .num{{position:absolute;left:5mm;bottom:3mm;width:9mm;height:9mm;border-radius:50%;background:var(--c);color:#fff;font-weight:700;font-size:11pt;display:flex;align-items:center;justify-content:center;border:.6mm solid #fff}}
.body{{padding-top:3.5mm}}
.body h3{{padding-right:26mm;font-family:Play;font-size:14pt;margin:0;line-height:1.15}}
.body .sub{{font-size:8pt;color:#6B6255;margin:.6mm 0 1.6mm}}
.yrs{{display:flex;gap:1.5mm;margin:0 0 6mm}}
.yp{{font-size:7.4pt;font-weight:700;padding:.4mm 2mm;border:.3mm solid var(--yc);border-radius:3mm}}
.txt{{font-size:8.4pt;line-height:1.42;margin:0 0 2mm}}
.dato{{font-size:7.9pt;line-height:1.4;margin:0;padding:1.6mm 2.2mm;background:#F4EEE1;border-left:.8mm solid var(--c);border-radius:.6mm}} .dato b{{color:var(--c)}}
.foot{{position:absolute;left:8mm;right:8mm;bottom:7mm;display:flex;align-items:center;gap:3mm;border-top:.2mm solid #E4DCC9;padding-top:2.5mm}}
.foot .qr{{width:16mm;height:16mm;flex:0 0 16mm}} .foot .qr svg{{width:100%;height:100%;display:block}}
.foot p{{font-size:7.2pt;color:#6B6255;margin:0;line-height:1.35}}

.pp{{background:radial-gradient(ellipse at 30% 20%,#1f3a6b 0%,#13254a 55%,#0c1934 100%);color:#E3C77A;justify-content:flex-start;padding-top:14mm}}
.pp::before{{content:"";position:absolute;inset:4mm;border:.35mm solid rgba(227,199,122,.45);border-radius:2mm}}
.pp-top{{font-family:Play;font-weight:700;letter-spacing:2.2px;font-size:12.5pt;color:#E8CD82;margin:0}}
.pp-sub{{font-size:7pt;letter-spacing:3px;color:#C9AE6A;margin:1mm 0 0}}
.pp-emb{{width:52mm;height:52mm;margin:6mm auto 3mm}}
.pp h1{{font-family:Cav;color:#F0D78C;font-size:27pt;margin:0;line-height:1}}
.pp-yrs{{font-size:7.5pt;color:#C9AE6A;margin:2.5mm 0 0;letter-spacing:.5px}}
.pp-n{{font-size:7pt;color:#C9AE6A;margin:5mm 0 0;letter-spacing:2.5px}}
.cover.pp p{{color:#D9BD72}} .cover.pp .pp-top{{color:#F0D78C;font-size:13pt}} .cover.pp .pp-yrs{{margin-top:3mm}} .cover.pp .pp-n{{margin-top:4mm}}
.pp-chip{{position:absolute;bottom:10mm;left:50%;width:12mm;height:8mm;transform:translateX(-50%)}}

/* margen de encuadernacion (lomo): 8 mm extra del lado del pegado */
section.rp:not(.cover){{padding-left:16mm}} section.lp{{padding-right:16mm}}
section.rp .ph .num{{left:11mm}} section.lp .stamps{{right:19mm}} section.lp .foot{{right:19.5mm}}
.pn{{position:absolute;bottom:3.2mm;font-size:6.8pt;color:#9A9080;letter-spacing:.5px}}
section.rp .pn{{right:8mm}} section.lp .pn{{left:8mm}}
section.rp .ph{{margin-left:-8mm}} section.lp .ph{{margin-right:-8mm}}
section.rp .foot{{left:16mm}} section.lp .foot{{right:16mm}}
section.rp .dband{{left:8mm}} section.lp .dband{{right:8mm}}
.stamps{{position:absolute;right:7mm;top:55mm;width:24mm;height:24mm;pointer-events:none;z-index:2}}
.stamp{{position:absolute;width:23mm;height:23mm;right:0;top:0;transform:translate(var(--dx,0),var(--dy,0)) rotate(var(--rot));mix-blend-mode:multiply;opacity:.92}}
.foot .stamp.oval{{position:static;width:27mm;height:17.3mm;flex:0 0 27mm;margin-left:1mm}}
.foot .stamp.rect{{position:static;width:30mm;height:17.2mm;margin-left:auto;flex:0 0 30mm}}
.stamp.big-oval{{width:33mm;height:19.5mm;top:2mm;right:1mm}}
.foot .stamp.wdw{{position:absolute;width:23mm;height:22mm;right:2.5mm;bottom:-0.5mm}}
.stamps .stamp.wdw{{width:28mm;height:28mm;top:1.5mm;right:-1mm}}

.stats h2{{font-family:Cav;font-size:22pt;color:#1D2B5B;margin:0;line-height:1}}
.st-sub{{font-size:7.6pt;color:#6B6255;margin:1mm 0 4mm;letter-spacing:.4px}}
.big4{{display:grid;grid-template-columns:repeat(4,1fr);gap:2mm;margin:0 0 4mm}}
.big4 div{{background:#F4EEE1;border-radius:1.5mm;padding:2.2mm 1mm;text-align:center;display:flex;flex-direction:column}}
.big4 b{{font-variant-numeric:lining-nums;font-family:Play;font-size:13pt;color:#1D2B5B;line-height:1.1}} .big4 span{{font-size:6.6pt;text-transform:uppercase;letter-spacing:.8px;color:#6B6255}}
.trips{{width:100%;border-collapse:collapse;font-size:7.6pt}}
.trips th{{font-size:6.4pt;text-transform:uppercase;letter-spacing:.8px;color:#6B6255;text-align:left;border-bottom:.3mm solid #D9CFB8;padding:0 0 1mm}}
.trips th:last-child,.trips .km{{text-align:right}}
.trips td{{padding:1.3mm 0;border-bottom:.2mm solid #E9E2D2;vertical-align:middle;line-height:1.25}}
.trips td:first-child{{width:5mm}} .trips td span{{color:#6B6255;font-size:6.6pt}}
.trips .km{{font-variant-numeric:lining-nums;font-family:Play;font-weight:700;font-size:9pt;white-space:nowrap}}
.trips tfoot td{{border:none;font-weight:700;padding-top:1.8mm}} .trips tfoot .km{{color:#1D2B5B;font-size:10pt}}
.rec{{margin-top:3mm;font-size:7.2pt;line-height:1.4;background:#F4EEE1;border-left:.8mm solid #DC322F;padding:1.8mm 2.2mm;border-radius:.6mm}}
.foot .stamp-img{{position:absolute;width:19mm;right:24mm;bottom:-0.5mm;transform:rotate(-6deg);mix-blend-mode:multiply}}
.stamps .stamp-img2{{position:absolute;width:19mm;right:29mm;top:9mm;transform:rotate(8deg);mix-blend-mode:multiply}}
.stamps .stamp-img3{{position:absolute;width:27mm;right:41mm;top:20mm;transform:rotate(-5deg);mix-blend-mode:multiply}}
.foot .stamp-img4{{position:absolute;width:16mm;right:45.5mm;bottom:0mm;transform:rotate(7deg);mix-blend-mode:multiply}}
.foot .stamp.wdw{{width:22mm!important;height:22mm!important}}
section[data-n="2"] .stamps{{left:0;top:0;right:0;bottom:0;width:auto;height:auto;z-index:3}}
.dwov{{position:absolute;inset:0}} .dwi{{position:absolute;display:flex;align-items:center;justify-content:center;mix-blend-mode:multiply}}
.dwi img{{max-width:100%;max-height:100%}} .dwi svg.stamp{{position:static;width:100%;height:100%;transform:none}}
section[data-n="2"] .ph{{height:44mm}}
.stamps .dlimg{{position:absolute;right:-1mm;top:1mm;width:34mm;transform:rotate(-6deg);mix-blend-mode:multiply;text-align:center}}
.dlimg img{{width:100%;display:block}} .dlimg span{{display:block;font-size:4.6pt;color:#9A9080;margin-top:.3mm}}

.firmas h2{{font-family:Cav;font-size:22pt;color:#1D2B5B;margin:0;line-height:1}} .firmas .h2b{{margin-top:6mm}}
.sig{{display:grid;grid-template-columns:1fr 1fr;column-gap:5mm;margin:8mm 0 0}}
.sig .sl{{border-bottom:.3mm solid #8A8070;height:9mm;grid-row:1}} .sig span{{grid-row:2;font-size:6.6pt;color:#9A9080;text-transform:uppercase;letter-spacing:.8px;margin-top:.8mm}}
.vis{{display:grid;grid-template-columns:1fr 1fr;gap:3mm}}
.vb{{border:.5mm dashed #B9AE98;border-radius:2mm;height:27mm;padding:2mm 2.5mm;display:flex;flex-direction:column;justify-content:flex-end;gap:.6mm}}
.vb span{{font-size:6pt;color:#9A9080;text-transform:uppercase;letter-spacing:.8px}} .vb .vl{{border-bottom:.25mm solid #CFC5B0;height:3.5mm}}
.pp-back{{justify-content:center!important;padding:0!important}}
.pp-back .bq{{background:#F3E7C4;border-radius:2mm;padding:2.5mm;margin:9mm auto 3mm;box-shadow:0 0 0 .4mm #C9A24A}}
.pp-back .bq .qr{{width:24mm;height:24mm;margin:0}} .pp-back .bq svg{{width:100%;height:100%;display:block}}
.cover.pp p.bq-t,.pp-back p.bq-t{{font-size:7.5pt;color:#E8CD82;margin:0;letter-spacing:.4px}} .pp-back p.bq-u{{font-size:6.8pt;color:#C9AE6A;margin:1mm 0 0}}
.pp-back .pp-top{{color:#F0D78C;font-size:11pt}} .pp-back .pp-sub{{color:#C9AE6A}}
.pp-in{{padding:0!important}}
</style></head><body>
<section class="cover pp"><p class="pp-top">PASAPORTE DE VIAJE</p><p class="pp-sub">TRAVEL PASSPORT</p><svg class="pp-emb" viewBox="0 0 200 200"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#F3DE9A"/><stop offset=".5" stop-color="#C9A24A"/><stop offset="1" stop-color="#E9CF7E"/></linearGradient></defs><g fill="none" stroke="url(#g)" stroke-width="2.2"><circle cx="100" cy="112" r="46"/><ellipse cx="100" cy="112" rx="20" ry="46"/><ellipse cx="100" cy="112" rx="38" ry="46"/><line x1="54" y1="112" x2="146" y2="112"/><path d="M60 90 Q100 98 140 90"/><path d="M60 134 Q100 126 140 134"/><path d="M38 150 Q100 40 168 88" stroke-dasharray="5 5" stroke-width="1.8"/></g><g fill="url(#g)"><path transform="translate(34.2,76.1) scale(0.9)" d="M0,-5 L1.5,-1.5 5,-1.5 2.2,0.8 3.2,4.5 0,2.3 -3.2,4.5 -2.2,0.8 -5,-1.5 -1.5,-1.5Z"/><path transform="translate(49.1,52.0) scale(0.9)" d="M0,-5 L1.5,-1.5 5,-1.5 2.2,0.8 3.2,4.5 0,2.3 -3.2,4.5 -2.2,0.8 -5,-1.5 -1.5,-1.5Z"/><path transform="translate(72.2,35.8) scale(0.9)" d="M0,-5 L1.5,-1.5 5,-1.5 2.2,0.8 3.2,4.5 0,2.3 -3.2,4.5 -2.2,0.8 -5,-1.5 -1.5,-1.5Z"/><path transform="translate(99.9,30.0) scale(0.9)" d="M0,-5 L1.5,-1.5 5,-1.5 2.2,0.8 3.2,4.5 0,2.3 -3.2,4.5 -2.2,0.8 -5,-1.5 -1.5,-1.5Z"/><path transform="translate(127.6,35.7) scale(0.9)" d="M0,-5 L1.5,-1.5 5,-1.5 2.2,0.8 3.2,4.5 0,2.3 -3.2,4.5 -2.2,0.8 -5,-1.5 -1.5,-1.5Z"/><path transform="translate(150.8,51.8) scale(0.9)" d="M0,-5 L1.5,-1.5 5,-1.5 2.2,0.8 3.2,4.5 0,2.3 -3.2,4.5 -2.2,0.8 -5,-1.5 -1.5,-1.5Z"/><path transform="translate(165.7,75.8) scale(0.9)" d="M0,-5 L1.5,-1.5 5,-1.5 2.2,0.8 3.2,4.5 0,2.3 -3.2,4.5 -2.2,0.8 -5,-1.5 -1.5,-1.5Z"/><path transform="translate(170,86) rotate(30)" d="M0,-9 L2,-2 9,2 9,4 2,2 1.5,7 4,9 4,10.5 0,9.5 -4,10.5 -4,9 -1.5,7 -2,2 -9,4 -9,2 -2,-2Z"/></g></svg><h1>Mis viajes<br>por USA</h1><p class="pp-yrs">2012 · 2013 · 2016 · 2018 · 2019 · 2022</p><p class="pp-n">45 LUGARES · 7 VIAJES</p><svg class="pp-chip" viewBox="0 0 40 26"><g fill="none" stroke="url(#g2)" stroke-width="1.6"><rect x="1" y="1" width="38" height="24" rx="3"/><circle cx="20" cy="13" r="5"/><line x1="1" y1="13" x2="15" y2="13"/><line x1="25" y1="13" x2="39" y2="13"/></g><defs><linearGradient id="g2"><stop offset="0" stop-color="#E9CF7E"/><stop offset="1" stop-color="#C9A24A"/></linearGradient></defs></svg></section>
<section class="pp pp-in"></section>
<section class="intro"><h2>Cómo usar este pasaporte</h2>
<p>Cada lugar tiene un número (el mismo del mapa) y un código QR. Apuntá la cámara del celular al código y se abre su página, con las fotos, la historia y el lugar en el mapa.</p>
<p>Los años en color indican cada visita; algunos lugares los visitamos más de una vez.</p>
<ul>{legend}</ul></section>
{"".join(rows).replace('<div class="trip"','<div class="trip newpage"')}
{STATS}
{FIRMAS}
NOTES
<section class="pp pp-in"></section>
<section class="back pp pp-back"><p class="pp-top">MIS VIAJES POR USA</p><p class="pp-sub">2012 · 2022</p><div class="bq"><div class="qr">{home}</div></div><p class="bq-t">Índice completo y mapa interactivo</p><p class="bq-u">marmar1926.github.io</p></section>
<script>
var _all=document.querySelectorAll('body > section');_all.forEach(function(sec,i){{sec.classList.add(i%2===0?'rp':'lp'); if(i>0 && i<_all.length-1 && !sec.classList.contains('pp')){{var p=document.createElement('div');p.className='pn';p.textContent=i+1;sec.appendChild(p);}}}});
document.querySelectorAll('.place').forEach(function(pg){{
  var body=pg.querySelector('.body'), foot=pg.querySelector('.foot'), fs=1;
  while(body.getBoundingClientRect().bottom > foot.getBoundingClientRect().top-8 && fs>0.6){{
    fs-=0.03; body.style.fontSize=''; pg.querySelectorAll('.txt,.dato').forEach(function(el){{el.style.zoom=fs;}});
  }}
  if(fs<1) pg.setAttribute('data-fit',fs.toFixed(2));
}});
</script></body></html>'''
open(f'{S}/librito.html','w',encoding='utf-8').write(doc)
print('ok')
