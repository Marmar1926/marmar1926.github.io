"""Arma los datos de la presentación (/presentacion/data/<viaje>.json): para cada viaje, sus paradas
en orden y las fotos de cada una con su texto, tomadas de las páginas de los lugares.
Uso: python3 _proyecto/herramientas/gen_viajes.py && python3 _proyecto/herramientas/gen_presentacion.py"""
import json, os, re, subprocess, hashlib, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import estados
from PIL import Image, ImageFilter, ImageEnhance

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EXTRACT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'extraer_fotos.js')
pj = open(f'{ROOT}/assets/places.js', encoding='utf-8').read()
P = json.loads(pj[pj.index('{'):pj.rindex('}') + 1])
BYURL = {p['url']: p for p in P['places']}
TRIPS = json.load(open(f'{ROOT}/viajes/stops.json', encoding='utf-8'))
CACHE = {}

def page(url):
    if url not in CACHE:
        out = subprocess.run(['node', EXTRACT, f'{ROOT}{url}index.html'], capture_output=True, text=True, check=True).stdout
        CACHE[url] = json.loads(out)
    return CACHE[url]

def year_of(tab):
    m = re.search(r'(20\d\d)', str(tab.get('group') or '') + ' ' + str(tab.get('year')))
    return int(m.group(1)) if m else None

def tab_trip(tab, place):
    """A qué viaje pertenece una pestaña de la página de un lugar."""
    y = year_of(tab)
    if y is None:
        return place['trip']
    for v in place.get('visits', []):
        if v['year'] == y and v.get('trip'):
            return v['trip']
    if y == 2012:
        return '2012md' if re.search('Orlando|Miami|Disney', str(tab.get('year')) + str(tab.get('sub'))) else '2012ny'
    return {2013: '2013', 2016: 'trip2', 2018: '2018', 2019: '2019', 2022: '2022'}.get(y)

BGDIR = f'{ROOT}/presentacion/bg'
os.makedirs(BGDIR, exist_ok=True)
def fondo(src):
    """Fondo ya difuminado y oscurecido (imagen chiquita): algunos televisores no pueden aplicar el desenfoque en vivo."""
    name = hashlib.md5(src.encode()).hexdigest()[:12] + '.jpg'
    out = f'{BGDIR}/{name}'
    if not os.path.exists(out):
        im = Image.open(ROOT + src).convert('RGB')
        im.thumbnail((96, 96))
        im = im.filter(ImageFilter.GaussianBlur(4))
        im = ImageEnhance.Color(im).enhance(1.2)
        im = ImageEnhance.Brightness(im).enhance(0.45)
        im.save(out, quality=70)
    return '/presentacion/bg/' + name

def items(photos, base):
    out = []
    for ph in photos:
        it = dict(src=base + ph['src'], caption=re.sub(r'<[^>]+>', '', ph.get('caption', '')), ratio=ph.get('ratio', 0.66))
        it['bg'] = fondo(it['src'])
        if ph.get('srcWide'):  # versión lado a lado (Then / Now) para pantallas horizontales
            it['wide'] = base + ph['srcWide']
            it['ratioWide'] = ph.get('ratioWide', 0.45)
            it['bgWide'] = fondo(it['wide'])
        if ph.get('srcThen') and ph.get('srcNow'):  # para el efecto cortina Then -> Now
            it['then'] = base + ph['srcThen']; it['now'] = base + ph['srcNow']
            w, h = Image.open(ROOT + it['then']).size
            it['ratioThen'] = round(h / w, 4)
        if ph.get('video'):
            it['video'] = base + ph['video']
        out.append(it)
    return out

def photos_for(trip, stop):
    url, h = (stop['url'].split('#') + [''])[:2]
    place = BYURL[url]
    d = page(url)
    if d['kind'] == 'PHOTOS':
        ph = d['data']
        # Williams y Oatman son parte de las páginas de Flagstaff y Kingman
        name = stop['name'].lower()
        if stop.get('star'):
            ph = [x for x in ph if name in x['src'].lower()]
        elif place['n'] == 43:
            ph = [x for x in ph if 'williams' not in x['src']]
        elif place['n'] == 41:
            ph = [x for x in ph if 'oatman' not in x['src']]
        return items(ph, url)
    tabs = d['data']
    if h:
        sel = [t for t in tabs if t.get('hash') == h]
    else:
        sel = [t for t in tabs if tab_trip(t, place) == trip]
        named = [t for t in sel if str(t.get('year')) == stop['name']]
        if named:
            sel = named
    return items([p for t in sel for p in t.get('photos', [])], url)

os.makedirs(f'{ROOT}/presentacion/data', exist_ok=True)
index = []
for k, t in TRIPS.items():
    stops = []
    for s in t['stops']:
        url, h = (s['url'].split('#') + [''])[:2]
        place = BYURL[url]
        ph = photos_for(k, s)
        lat, lng = place['lat'], place['lng']
        # coordenadas propias de pestañas y puntos ★ (data-extra de la página)
        html = open(f'{ROOT}{url}index.html', encoding='utf-8').read()
        mx = re.search(r"data-extra='([^']*)'", html)
        if mx:
            for x in json.loads(mx.group(1)):
                if (h and x.get('key') == h) or (s.get('star') and x.get('name', '').split(' ')[0] == s['name'].split(' ')[0]) or x.get('name') == s['name']:
                    lat, lng = x['lat'], x['lng']
        stops.append(dict(s, lat=lat, lng=lng, state=place['sub'], photos=ph))
    data = dict(key=k, **{x: t[x] for x in ('slug', 'label', 'year', 'color', 'intro', 'km', 'estados', 'meses')}, stops=stops)
    # cruces de estado sobre la ruta en auto (cartel «Welcome to ...»)
    rj = f'{ROOT}/assets/routes/{k}.json'
    if os.path.exists(rj):
        rd = json.load(open(rj))
        data['cruces'] = estados.cruces(rd['auto'] if isinstance(rd, dict) else [rd])
    json.dump(data, open(f'{ROOT}/presentacion/data/{k}.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    n = sum(len(s['photos']) for s in stops)
    index.append(dict(key=k, slug=t['slug'], label=t['label'], year=t['year'], color=t['color'], fotos=n,
                      corta=sum(min(6, len(s['photos'])) for s in stops), paradas=len(stops),
                      cover=next((s['photos'][0]['src'] for s in stops if s['photos']), ''),
                      fechas=[[s['date'], s['name']] for s in stops]))
    print(k, len(stops), 'paradas', n, 'fotos', [len(s['photos']) for s in stops])
json.dump(index, open(f'{ROOT}/presentacion/data/index.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
