"""Detecta dónde cada recorrido cruza de un estado a otro (para el cartel «Welcome to ...» de la presentación).
Límites de los estados: us-atlas (US Census, dominio público) convertido a GeoJSON en datos/us-states.geojson."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
_POLYS = None

def _load():
    global _POLYS
    if _POLYS is None:
        g = json.load(open(f'{HERE}/datos/us-states.geojson', encoding='utf-8'))
        _POLYS = []
        for f in g['features']:
            geo = f['geometry']
            polys = geo['coordinates'] if geo['type'] == 'MultiPolygon' else [geo['coordinates']]
            for poly in polys:
                ring = poly[0]
                xs = [p[0] for p in ring]; ys = [p[1] for p in ring]
                _POLYS.append((f['properties']['name'], (min(xs), min(ys), max(xs), max(ys)), poly))
    return _POLYS

def _inside(x, y, ring):
    c = False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i]; xj, yj = ring[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            c = not c
        j = i
    return c

def estado(lat, lng):
    for name, (x0, y0, x1, y1), poly in _load():
        if x0 <= lng <= x1 and y0 <= lat <= y1 and _inside(lng, lat, poly[0]) and not any(_inside(lng, lat, h) for h in poly[1:]):
            return name
    return None

def cruces(tramos):
    """tramos: listas de [lat, lng] recorridas en auto. Devuelve [{lat, lng, state}] en cada entrada a un estado nuevo."""
    out = []
    for pts in tramos:
        st = [estado(a, b) for a, b in pts]
        # los puntos sobre el agua o justo en el borde toman el estado anterior
        for i in range(1, len(st)):
            if st[i] is None:
                st[i] = st[i - 1]
        prev = st[0] if st else None
        for i in range(1, len(st)):
            if st[i] and st[i] != prev:
                # se ignoran las idas y vueltas muy cortas sobre un límite (menos de 3 puntos en el otro estado)
                if st[i + 1:i + 3] and any(x != st[i] for x in st[i + 1:i + 3]):
                    continue
                out.append(dict(lat=pts[i][0], lng=pts[i][1], state=st[i]))
                prev = st[i]
    return out
