"""Arma el trazado por rutas de una gira usando la red de rutas de Natural Earth (10m).
Uso: python3 build.py roads.geojson salida.json"""
import json, math, sys
import networkx as nx
from scipy.spatial import cKDTree

ROADS, OUT = sys.argv[1], sys.argv[2]

def hav(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(h))

# ---- grafo de rutas de USA (oeste) ----
G = nx.Graph()
fc = json.load(open(ROADS))
def keep(c):  # caja que cubre el oeste y las grandes llanuras
    return 30 < c[1] < 50 and -126 < c[0] < -100
for f in fc['features']:
    p = f['properties']
    if p.get('sov_a3') != 'USA' or p.get('type') == 'Ferry Route':
        continue
    g = f['geometry']
    lines = g['coordinates'] if g['type'] == 'MultiLineString' else [g['coordinates']]
    for ln in lines:
        if not any(keep(c) for c in ln):
            continue
        prev = None
        for c in ln:
            node = (round(c[1], 5), round(c[0], 5))
            if prev is not None and prev != node:
                G.add_edge(prev, node, w=hav(prev, node))
            prev = node
nodes = list(G.nodes)
tree = cKDTree([(n[0], n[1] * math.cos(math.radians(n[0]))) for n in nodes])
# unir extremos sueltos que quedaron a menos de ~1,5 km (cruces sin vértice compartido)
for i, j in tree.query_pairs(0.014):
    a, b = nodes[i], nodes[j]
    if not G.has_edge(a, b):
        G.add_edge(a, b, w=hav(a, b) * 1.2)
comp = max(nx.connected_components(G), key=len)
print('nodos', G.number_of_nodes(), 'componente principal', len(comp))

def snap(pt):
    d, i = tree.query((pt[0], pt[1] * math.cos(math.radians(pt[0]))), k=8)
    for k in i:
        if nodes[k] in comp:
            return nodes[k]
    return nodes[i[0]]

def road(a, b):
    na, nb = snap(a), snap(b)
    try:
        path = nx.shortest_path(G, na, nb, weight='w')
    except nx.NetworkXNoPath:
        return [a, b], None
    return [a] + [list(p) for p in path] + [b], sum(G[path[k]][path[k + 1]]['w'] for k in range(len(path) - 1))

# ---- paradas: ('r', punto) = ir por ruta; ('m', punto) = tramo dibujado a mano ----
S = [
 ('Los Angeles', (34.0522, -118.2437), 'r'),
 ('Las Vegas', (36.1699, -115.1398), 'r'),
 ('Provo', (40.2338, -111.6585), 'r'),
 ('Heber City', (40.5069, -111.4133), 'r'),
 ('Rawlins', (41.7911, -107.2387), 'r'),
 ('Casper', (42.8501, -106.3252), 'r'),
 ('Lusk', (42.7625, -104.4522), 'r'),
 ('Custer', (43.7666, -103.5988), 'r'),
 # US-385/US-16 al norte, pasando por Crazy Horse, y SD-244 hasta Rushmore
 ('US-385 (norte de Custer)', (43.8010, -103.6080), 'm'),
 ('Crazy Horse', (43.8366, -103.6236), 'm'),
 ('US-385/16', (43.8850, -103.6000), 'm'),
 ('Hill City', (43.9325, -103.5752), 'm'),
 ('Empalme SD-244', (43.9560, -103.5260), 'm'),
 ('Horsethief Lake', (43.8960, -103.4880), 'm'),
 ('Mount Rushmore', (43.8791, -103.4591), 'm'),
 ('Sheridan', (44.7972, -106.9562), 'r'),
 ('Cody', (44.5263, -109.0565), 'r'),
 # Yellowstone: entrada este y lazo por el parque hasta la salida oeste
 ('Entrada este', (44.4887, -110.0026), 'r'),
 ('Fishing Bridge', (44.5650, -110.3700), 'm'),
 ('Mud Volcano', (44.6245, -110.4325), 'm'),
 ('Canyon Village', (44.7350, -110.4890), 'm'),
 ('Norris', (44.7266, -110.7036), 'm'),
 ('Mammoth', (44.9767, -110.7020), 'm'),
 ('Norris ', (44.7266, -110.7036), 'm'),
 ('Madison', (44.6460, -110.8610), 'm'),
 ('Midway', (44.5250, -110.8380), 'm'),
 ('Madison ', (44.6460, -110.8610), 'm'),
 ('West Yellowstone', (44.6621, -111.1041), 'm'),
 ('Bozeman', (45.6770, -111.0429), 'r'),
 ('Missoula', (46.8721, -113.9940), 'r'),
 ('Kellogg', (47.5383, -116.1360), 'r'),
 ('Spokane', (47.6588, -117.4260), 'r'),
 ('Ellensburg', (46.9965, -120.5478), 'r'),
 ('Seattle', (47.6062, -122.3321), 'r'),
 ('Olympia', (47.0379, -122.9007), 'r'),
 ('Centralia', (46.7162, -122.9543), 'r'),
 ('Longview', (46.1382, -122.9382), 'r'),
 ('Portland', (45.5152, -122.6784), 'r'),
 ('Salem', (44.9429, -123.0351), 'r'),
 ('Eugene', (44.0521, -123.0868), 'r'),
 ('Medford', (42.3265, -122.8756), 'r'),
 ('Redding', (40.5865, -122.3917), 'r'),
 ('Dunnigan (I-5 / I-505)', (38.8852, -121.9697), 'r'),
 ('Vacaville', (38.3566, -121.9877), 'r'),
 ('San Francisco', (37.7749, -122.4194), 'r'),
 ('Santa Cruz', (36.9741, -122.0308), 'r'),
 ('Carmel', (36.5552, -121.9233), 'r'),
 ('Big Sur', (36.2704, -121.8081), 'r'),
 ('Lucia', (36.0185, -121.5490), 'm'),
 ('Gorda', (35.9068, -121.4652), 'm'),
 # desvío por Los Burros Road y South Coast Ridge Road hasta la 101
 ('Los Burros Rd', (35.8926, -121.4560), 'm'),
 ('Los Burros (cresta)', (35.9050, -121.3960), 'm'),
 ('South Coast Ridge Rd', (35.9600, -121.4000), 'm'),
 ('Nacimiento-Fergusson', (36.0060, -121.3870), 'm'),
 ('Fort Hunter Liggett', (35.9800, -121.2600), 'm'),
 ('Jolon', (35.9719, -121.1749), 'm'),
 ('Lockwood', (35.9378, -121.0827), 'm'),
 ('Bradley', (35.8644, -120.8007), 'm'),
 ('Paso Robles', (35.6266, -120.6910), 'r'),
 ('Atascadero', (35.4894, -120.6707), 'm'),
 ('San Luis Obispo', (35.2828, -120.6596), 'm'),
 ('Pismo Beach', (35.1428, -120.6413), 'm'),
 ('Solvang', (34.5958, -120.1376), 'r'),
 ('Santa Barbara', (34.4208, -119.6982), 'r'),
 ('Los Angeles', (34.0522, -118.2437), 'r'),
]
pts, km = [list(S[0][1])], 0
for (na, a, _), (nb, b, mode) in zip(S, S[1:]):
    if mode == 'm':
        seg, d = [list(a), list(b)], hav(a, b) * 1.25
    else:
        seg, d = road(a, b)
        direct = hav(a, b)
        if d is None or d > direct * 2.2:
            print(f'  ! {na} -> {nb}: ruta dudosa ({d} km vs {direct:.0f} recto), uso línea')
            seg, d = [list(a), list(b)], direct * 1.2
    km += d
    print(f'{na:>22} -> {nb:<22} {d:7.0f} km')
    pts += seg[1:]

def dp(P, eps):  # Douglas-Peucker
    if len(P) < 3: return P
    a, b = P[0], P[-1]
    def dist(p):
        if a == b: return math.hypot(p[0]-a[0], p[1]-a[1])
        return abs((b[1]-a[1])*(a[0]-p[0]) - (a[1]-p[1])*(b[0]-a[0])) / math.hypot(b[0]-a[0], b[1]-a[1])
    i, m = max(((i, dist(P[i])) for i in range(1, len(P)-1)), key=lambda t: t[1])
    if m > eps:
        return dp(P[:i+1], eps)[:-1] + dp(P[i:], eps)
    return [a, b]
simp = []
# simplificar por tramos de 400 puntos para no recursar demasiado
for k in range(0, len(pts), 400):
    simp += dp(pts[k:k+401], 0.004)[:-1] if k + 401 < len(pts) else dp(pts[k:], 0.004)
simp = [[round(p[0], 4), round(p[1], 4)] for p in simp]
print('total aprox', round(km), 'km · puntos', len(pts), '->', len(simp))
json.dump(simp, open(OUT, 'w'), separators=(',', ':'))
