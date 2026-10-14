import math, html
FILTER='''<defs><filter id="ink{u}" x="-10%" y="-10%" width="120%" height="120%"><feTurbulence type="fractalNoise" baseFrequency="0.55" numOctaves="2" seed="{u}"/><feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.1 1.55"/><feComposite in="SourceGraphic" operator="in"/></filter>
<path id="arc{u}" d="M 60,60 m -43,0 a 43,43 0 1,1 86,0 a 43,43 0 1,1 -86,0"/></defs>'''
def fit(txt, maxw, size):
    est=len(txt)*size*0.62
    return f' textLength="{maxw}" lengthAdjust="spacingAndGlyphs"' if est>maxw else ''

def round_stamp(u,c,top,date,mid='ADMITTED',sub='VISITOR'):
    return (f'<svg class="stamp" viewBox="0 0 120 120" style="--rot:{-14 if u%2 else 9}deg">'+FILTER.format(u=u)+
     f'<g filter="url(#ink{u})" fill="none" stroke="{c}"><circle cx="60" cy="60" r="56" stroke-width="3.2"/><circle cx="60" cy="60" r="35" stroke-width="1.6"/></g>'
     f'<g filter="url(#ink{u})" fill="{c}" font-family="Src" font-weight="700"><text font-size="10.5" letter-spacing="1.6"><textPath href="#arc{u}" startOffset="50%" text-anchor="middle"{fit(top,250,10.5)}>{html.escape(top)}</textPath></text>'
     f'<text x="60" y="52" text-anchor="middle" font-size="9" letter-spacing="1">{mid}</text>'
     f'<text x="60" y="66" text-anchor="middle" font-size="9.6">{date}</text>'
     f'<text x="60" y="78" text-anchor="middle" font-size="7.5" letter-spacing="1.5">{sub}</text>'
     f'<path transform="translate(60,103) rotate(90) scale(.55)" d="M0,-9 L2,-2 9,2 9,4 2,2 1.5,7 4,9 4,10.5 0,9.5 -4,10.5 -4,9 -1.5,7 -2,2 -9,4 -9,2 -2,-2Z"/></g></svg>')
def rect_stamp(u,c,top,date,sub):
    return (f'<svg class="stamp rect" viewBox="0 0 150 86" style="--rot:{7 if u%2 else -8}deg">'+FILTER.format(u=u)+
     f'<g filter="url(#ink{u})"><rect x="3" y="3" width="144" height="80" rx="7" fill="none" stroke="{c}" stroke-width="3"/><rect x="9" y="9" width="132" height="68" rx="4" fill="none" stroke="{c}" stroke-width="1.2"/>'
     f'<g fill="{c}" font-family="Src" font-weight="700"><text x="75" y="27" text-anchor="middle" font-size="11" letter-spacing="1.8"{fit(top,118,11)}>{html.escape(top)}</text>'
     f'<line x1="18" y1="34" x2="132" y2="34" stroke="{c}" stroke-width="1"/>'
     f'<text x="75" y="53" text-anchor="middle" font-size="15">{date}</text>'
     f'<text x="75" y="69" text-anchor="middle" font-size="8" letter-spacing="2">{html.escape(sub)}</text></g></g></svg>')

def oval_stamp(u,c,top,date,sub):
    return (f'<svg class="stamp oval" viewBox="0 0 150 96" style="--rot:{-6 if u%2 else 5}deg">'+FILTER.format(u=u)+
     f'<g filter="url(#ink{u})"><ellipse cx="75" cy="48" rx="71" ry="44" fill="none" stroke="{c}" stroke-width="3.6"/><ellipse cx="75" cy="48" rx="62" ry="36" fill="none" stroke="{c}" stroke-width="1.5"/>'
     f'<g fill="{c}" font-family="Src" font-weight="700"><text x="75" y="31" text-anchor="middle" font-size="9.5" letter-spacing="2">PORT OF ENTRY</text>'
     f'<text x="75" y="55" text-anchor="middle" font-size="16">{date}</text>'
     f'<text x="75" y="70" text-anchor="middle" font-size="9.5" letter-spacing="1.2"{fit(sub,100,9.5)}>{html.escape(sub)}</text></g></g></svg>')

def anaheim_stamp(u,c,date):
    return (f'<svg class="stamp big-oval" viewBox="0 0 170 100" style="--rot:-7deg">'+FILTER.format(u=u)+
     f'<g filter="url(#ink{u})"><ellipse cx="85" cy="50" rx="81" ry="46" fill="none" stroke="{c}" stroke-width="3.4"/>'
     f'<ellipse cx="85" cy="50" rx="72" ry="38" fill="none" stroke="{c}" stroke-width="1.3"/>'
     f'<g fill="{c}" font-family="Src" font-weight="700">'
     f'<text x="85" y="27" text-anchor="middle" font-size="7" letter-spacing="2">· ORANGE COUNTY ·</text>'
     f'<text x="85" y="41" text-anchor="middle" font-size="11" letter-spacing="1.6">ANAHEIM, CA</text>'
     f'<line x1="40" y1="46" x2="130" y2="46" stroke="{c}" stroke-width="1"/>'
     f'<text x="85" y="66" text-anchor="middle" font-family="Play" font-size="20" letter-spacing="1">{date}</text>'
     f'<text x="85" y="78" text-anchor="middle" font-size="6.5" letter-spacing="2">VISITOR · ADMITTED</text></g></g></svg>')

def wdw_stamp(u,c,d1,d2=None,rot=-8,park=None):
    if park:
        fs=13 if len(park)<=6 else (10 if len(park)<=13 else 8.6)
        center=(f'<text x="110" y="103" text-anchor="middle" font-size="{fs}" letter-spacing="1">{park}</text>'
                f'<line x1="74" y1="110" x2="146" y2="110" stroke="{c}" stroke-width="1.2"/>'
                f'<text x="110" y="129" text-anchor="middle" font-size="15">{d1}</text>')
    elif d2:
        center=(f'<text x="110" y="96" text-anchor="middle" font-size="10" letter-spacing="2">ORLANDO · FL</text>'
                f'<text x="110" y="114" text-anchor="middle" font-size="15">{d1}</text>'
                f'<line x1="78" y1="121" x2="142" y2="121" stroke="{c}" stroke-width="1.2"/>'
                f'<text x="110" y="137" text-anchor="middle" font-size="15">{d2}</text>')
    else:
        center=(f'<text x="110" y="100" text-anchor="middle" font-size="10" letter-spacing="2">ORLANDO · FL</text>'
                f'<text x="110" y="124" text-anchor="middle" font-size="17">{d1}</text>'
                f'<text x="110" y="140" text-anchor="middle" font-size="8.5" letter-spacing="2">ADMITTED</text>')
    return (f'<svg class="stamp wdw" viewBox="0 0 220 220" style="--rot:{rot}deg">'
     f'<defs><filter id="ink{u}" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency="0.7" numOctaves="3" seed="{u}"/>'
     f'<feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.6 1.5"/><feComposite in="SourceGraphic" operator="in"/></filter>'
     f'<path id="t{u}" d="M 110,110 m -74,0 a 74,74 0 1,1 148,0"/><path id="b{u}" d="M 36,110 a 74,74 0 0,0 148,0"/></defs>'
     f'<g filter="url(#ink{u})"><g fill="none" stroke="{c}"><circle cx="110" cy="110" r="104" stroke-width="7"/><circle cx="110" cy="110" r="95" stroke-width="2"/><circle cx="110" cy="110" r="54" stroke-width="6"/></g>'
     f'<g fill="{c}" font-family="SpEl"><text font-size="30" letter-spacing="2"><textPath href="#t{u}" startOffset="50%" text-anchor="middle">WALT DISNEY</textPath></text>'
     f'<text font-size="30" letter-spacing="6"><textPath href="#b{u}" startOffset="50%" text-anchor="middle" dominant-baseline="hanging">WORLD</textPath></text>'
     f'<text x="30" y="122" text-anchor="middle" font-size="36">*</text><text x="190" y="122" text-anchor="middle" font-size="36">*</text>'
     +center+'</g></g></svg>')
