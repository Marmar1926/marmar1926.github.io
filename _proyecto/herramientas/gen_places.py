"""Genera assets/places.js desde _proyecto/manifest.json (coordenadas, viajes y años de visita).
Uso: python3 _proyecto/herramientas/gen_places.py"""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
m = json.load(open(f'{ROOT}/_proyecto/manifest.json', encoding='utf-8'))
hexc = lambda c: '#%02X%02X%02X' % tuple(c)
trips = {k: {'color': hexc(v['color']), 'label': v['label'], 'year': v['year']} for k, v in m['trips'].items()}
year2trip = {}
for k, v in m['trips'].items():
    year2trip.setdefault(v['year'], k)
places = []
for e in m['entries']:
    visits = [{'year': m['trips'][e['trip']]['year'], 'color': trips[e['trip']]['color'], 'trip': e['trip']}]
    for v in e.get('extra_visits', []):
        t = year2trip.get(v['year'])
        visits.append({'year': v['year'], 'color': trips[t]['color'] if t else hexc(v['color']), 'trip': t})
    places.append({'n': e['number'], 'trip': e['trip'], 'name': e['name'], 'sub': e.get('sub', ''),
                   'url': f"/{e['trip']}/{e['slug']}/", 'lat': e['lat'], 'lng': e['lng'], 'z': e['zoom'],
                   'visits': visits})
open(f'{ROOT}/assets/places.js', 'w', encoding='utf-8').write(
    '// Generado por _proyecto/herramientas/gen_places.py desde _proyecto/manifest.json\nwindow.PLACES = '
    + json.dumps({'trips': trips, 'places': places}, ensure_ascii=False) + ';\n')
print(len(places))
