"""Genera una página por viaje en /viajes/<clave>/ a partir de manifest.json y assets/places.js.
Uso: python3 _proyecto/herramientas/gen_viajes.py"""
import json, os, re, html
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
m = json.load(open(f'{ROOT}/_proyecto/manifest.json', encoding='utf-8'))
pj = open(f'{ROOT}/assets/places.js', encoding='utf-8').read()
P = json.loads(pj[pj.index('{'):pj.rindex('}') + 1])

# Datos de cada viaje que no están en el manifest
META = {
    '2012md': dict(slug='2012-miami-disney', km=1132, estados=['Florida'], meses='Marzo de 2012',
        intro='El primer viaje y el primer lugar que pisamos en Estados Unidos: Miami. De ahí, la costa atlántica hasta Daytona, '
              'los parques de Disney y Universal en Orlando, y la vuelta por el golfo de México pasando por Tampa, '
              'St. Petersburg, Venice y Naples.'),
    '2012ny': dict(slug='2012-nueva-york-boston', km=865, estados=['Nueva York', 'Connecticut', 'Massachusetts'], meses='Octubre y noviembre de 2012',
        intro='Una semana en Manhattan, con el huracán Sandy como compañero de toda la estadía y un cumpleaños festejado en Central Park. '
              'Después, la ruta hacia Boston, Harvard, Fenway Park y la costa de Salem y Swampscott, y la vuelta por el mismo camino.'),
    '2013': dict(slug='2013-triangulo-dorado', km=1258, estados=['California', 'Nevada', 'Arizona'], meses='Junio de 2013',
        intro='Los Ángeles y sus estudios de cine, San Diego, la Pacific Coast Highway por Big Sur y Monterey, Yosemite y San Francisco. '
              'Un vuelo a Las Vegas para cerrar con el Skywalk del Gran Cañón y el Valley of Fire, y otro de regreso a Los Ángeles.'),
    'trip2': dict(slug='2016-palmeras-y-magnolias', km=2975, estados=['Florida', 'Georgia'], meses='Junio de 2016',
        intro='Florida de punta a punta y una escapada a Georgia: Key West, la costa atlántica hasta el Kennedy Space Center y Saint Augustine, '
              'Atlanta y Covington, el «Hollywood del Sur» de The Dukes of Hazzard, y la vuelta por la costa del golfo con Sanibel y Captiva.'),
    '2018': dict(slug='2018-gigantes-y-geiseres', km=6117, estados=['California', 'Nevada', 'Utah', 'Wyoming', 'Dakota del Sur', 'Montana', 'Idaho', 'Washington', 'Oregón', 'Arizona'], meses='Junio y julio de 2018',
        intro='El gran loop: 21 días y más de 6.000 km desde Los Ángeles, cruzando el desierto y las Rocosas hasta Mount Rushmore y Crazy Horse, '
              'Yellowstone, Seattle y la costa del Pacífico, con el desvío inesperado por los caminos de tierra de Big Sur.'),
    '2019': dict(slug='2019-miami-disney', km=427, estados=['Florida'], meses='Mayo y junio de 2019',
        intro='La vuelta a Florida: varios días en los parques de Disney, el Florida\'s Turnpike hacia Miami y un crucero en el MSC Seaside '
              'hasta San Juan de Puerto Rico (el tramo en barco no está dibujado en el mapa).'),
    '2022': dict(slug='2022-del-pacifico-al-gran-canon', km=2260, estados=['California', 'Arizona', 'Utah'], meses='Octubre y noviembre de 2022',
        intro='Del Pacífico al desierto: el Gran Cañón, Horseshoe Bend, Antelope Canyon y Monument Valley, la Ruta 66 histórica por Williams, '
              'Seligman, Kingman y Oatman, Palm Springs, y el regreso a la costa con Malibú, Santa Bárbara y Universal Studios.'),
}
ORDER = sorted(m['trips'], key=lambda k: (m['trips'][k]['year'], k != '2012md'))
urls = sorted(p['url'] for p in P['places'])
def cover(u):
    return '/assets/cover/%02d.jpg' % urls.index(u)
def d(s):
    dd, mm, yy = map(int, s.split('/')); return date(yy, mm, dd)
MESES = 'enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre'.split()
def largo(x):
    return f'{x.day} de {MESES[x.month - 1]}'
def hexc(c): return '#%02X%02X%02X' % tuple(c)
def ink(c): return '#B08600' if c.upper() == '#F1C40F' else c

# lugares de cada viaje, con su fecha
stops = {k: [] for k in ORDER}
for p in P['places']:
    for v in p.get('visits', []):
        t = v.get('trip') or ('2019' if v['year'] == 2019 else None)
        if t in stops and v.get('date'):
            stops[t].append(dict(n=p['n'], name=p['name'], sub=p['sub'], url=p['url'], date=v['date'], img=cover(p['url'])))
# lugares con pestañas: en vez del lugar, se listan sus pestañas con su propia fecha
SUBS = {
    ('2012ny', 3): [('Times Square', '24/10/2012', 'timessquare'), ('Estatua de la Libertad y Ellis Island', '25/10/2012', 'liberty'),
                    ('Memorial 9/11', '25/10/2012', '911'), ('Rockefeller Center', '25/10/2012', 'rockefeller'),
                    ('Central Park', '26/10/2012', 'centralpark'), ('Empire State', '27/10/2012', 'empire')],
    ('2012ny', 4): [('Harvard University', '02/11/2012', 'harvard'), ('Boston y alrededores', '03/11/2012', 'boston'), ('Fenway Park', '03/11/2012', 'fenway')],
    ('2012md', 2): [('Animal Kingdom', '21/03/2012', ''), ('Magic Kingdom', '22/03/2012', ''), ('Hollywood Studios', '24/03/2012', ''), ('Epcot', '25/03/2012', '')],
    ('2019', 2): [('Magic Kingdom', '31/05/2019', ''), ('Hollywood Studios', '02/06/2019', ''), ('Animal Kingdom', '03/06/2019', ''), ('Epcot', '05/06/2019', '')],
}
for (k, n), subs in SUBS.items():
    base = [x for x in stops[k] if x['n'] == n][0]
    stops[k].remove(base)
    for name, dt, h in subs:
        stops[k].append(dict(base, name=name, sub=base['name'], date=dt, url=base['url'] + ('#' + h if h else '')))
# puntos ★ con fecha que pertenecen a otro viaje (Universal Orlando 2012)
stops['2012md'].append(dict(n=45, name='Universal Studios Florida', sub='Orlando, Florida', url='/2022/t3yh5c8d/#orlando-2012', date='27/03/2012', img=cover('/2022/t3yh5c8d/'), star=True))
for n, name, sub, dt in [(43, 'Williams', 'Arizona, Ruta 66', '27/10/2022'), (41, 'Oatman', 'Arizona, Ruta 66', '28/10/2022')]:
    pl = [p for p in P['places'] if p['n'] == n][0]
    stops['2022'].append(dict(n=n, name=name, sub=sub, url=pl['url'], date=dt, img=cover(pl['url']), star=True))
# orden real dentro de un mismo día (según el recorrido)
TIE = {'2022': ['Horseshoe Bend', 'Antelope Canyon', 'Flagstaff', 'Williams', 'Seligman', 'Kingman', 'Oatman'],
       '2018': ['Crazy Horse Memorial', 'Mount Rushmore Memorial']}
def tie(k, s):
    l = TIE.get(k, [])
    return l.index(s['name']) if s['name'] in l else -1
for k in stops:
    stops[k].sort(key=lambda s: (d(s['date']), tie(k, s), s['n']))

TPL = open(f'{ROOT}/_proyecto/herramientas/viaje.tpl.html', encoding='utf-8').read()
for i, k in enumerate(ORDER):
    t, me, ss = m['trips'][k], META[k], stops[k]
    color = hexc(t['color']); c2 = ink(color)
    d0, d1 = d(ss[0]['date']), d(ss[-1]['date'])
    if d0.month == d1.month: rango = f'Del {d0.day} al {largo(d1)} de {d1.year}'
    else: rango = f'Del {largo(d0)} al {largo(d1)} de {d1.year}'
    lugares = len({s['n'] for s in ss})
    items = []
    for s in ss:
        items.append(
            f'<li><a href="{s["url"]}"><span class="when">{html.escape(s["date"][:5])}</span>'
            f'<img loading="lazy" src="{s["img"]}" alt="">'
            f'<span class="tx"><b>{"★ " if s.get("star") else ""}{html.escape(s["name"])}</b><small>{html.escape(s["sub"])} · #{s["n"]}</small></span></a></li>')
    prev_k = ORDER[i - 1] if i else None
    next_k = ORDER[i + 1] if i + 1 < len(ORDER) else None
    def nav(kk, lbl, cls):
        if not kk: return '<span></span>'
        tt = m['trips'][kk]
        return (f'<a class="{cls}" href="/viajes/{META[kk]["slug"]}/"><small>{lbl}</small>'
                f'<b><i style="background:{hexc(tt["color"])}"></i>{html.escape(tt["label"].split(",")[0].split(":")[0])}</b><span>{tt["year"]}</span></a>')
    strip = ''.join(f'<img src="{s["img"]}" alt="">' for s in ss[:4])
    out = (TPL.replace('{{KEY}}', k).replace('{{TITLE}}', html.escape(t['label']))
           .replace('{{YEAR}}', str(t['year'])).replace('{{COLOR}}', color).replace('{{INK}}', c2)
           .replace('{{MESES}}', me['meses']).replace('{{RANGO}}', rango).replace('{{INTRO}}', html.escape(me['intro']))
           .replace('{{KM}}', f'{me["km"]:,}'.replace(',', '.')).replace('{{LUGARES}}', str(lugares))
           .replace('{{NESTL}}', 'estado' if len(me['estados']) == 1 else 'estados').replace('{{NEST}}', str(len(me['estados']))).replace('{{ESTADOS}}', ' · '.join(me['estados']))
           .replace('{{ITEMS}}', '\n'.join(items)).replace('{{STRIP}}', strip)
           .replace('{{PREV}}', nav(prev_k, '← Viaje anterior', 'pv')).replace('{{NEXT}}', nav(next_k, 'Viaje siguiente →', 'nx'))
           .replace('{{N}}', str(i + 1)).replace('{{SLUG}}', me['slug']))
    os.makedirs(f'{ROOT}/viajes/{me["slug"]}', exist_ok=True)
    open(f'{ROOT}/viajes/{me["slug"]}/index.html', 'w', encoding='utf-8').write(out)
    print(me['slug'], lugares, rango)
json.dump({k: dict(slug=META[k]['slug']) for k in ORDER}, open(f'{ROOT}/viajes/viajes.json', 'w'), ensure_ascii=False)
# paradas de cada viaje en orden, para la presentación (gen_presentacion.py)
json.dump({k: dict(slug=META[k]['slug'], label=m['trips'][k]['label'], year=m['trips'][k]['year'], color=hexc(m['trips'][k]['color']),
                   intro=META[k]['intro'], km=META[k]['km'], estados=META[k]['estados'], meses=META[k]['meses'],
                   stops=[dict(n=s['n'], name=s['name'], sub=s['sub'], url=s['url'], date=s['date'], star=bool(s.get('star'))) for s in stops[k]])
           for k in ORDER}, open(f'{ROOT}/viajes/stops.json', 'w'), ensure_ascii=False, indent=0)
