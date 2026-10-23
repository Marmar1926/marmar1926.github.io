/* Dibuja los recorridos de las giras en un mapa Leaflet.
   Donde dos o más giras usaron la misma ruta, la línea se dibuja con trazos
   alternados de cada color, para que se vean todas. */
(function () {
  var TOL = 0.0025;   // ~250 m: distancia para considerar que dos giras van por la misma ruta
  var STEP = 0.01;    // los tramos se parten cada ~1 km para comparar
  var DASH = 9;       // largo de cada trazo de color, en píxeles
  // estilo de los tramos compartidos: 'lado' (líneas paralelas) o 'trazos' (colores alternados)
  var SIDE = (window.MV_SHARED_STYLE || 'lado') === 'lado' && !!(window.L && L.PolylineOffset);

  function densify(pts) {
    var out = [pts[0]];
    for (var i = 1; i < pts.length; i++) {
      var a = pts[i - 1], b = pts[i], d = Math.max(Math.abs(b[0] - a[0]), Math.abs(b[1] - a[1]));
      var n = Math.ceil(d / STEP);
      for (var k = 1; k <= n; k++) out.push([a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n]);
    }
    return out;
  }
  function segDist(p, a, b) {
    var cx = Math.cos(p[0] * Math.PI / 180);
    var ax = (a[1] - p[1]) * cx, ay = a[0] - p[0], bx = (b[1] - p[1]) * cx, by = b[0] - p[0];
    var dx = bx - ax, dy = by - ay, L = dx * dx + dy * dy, t = L ? -(ax * dx + ay * dy) / L : 0;
    t = Math.max(0, Math.min(1, t));
    var x = ax + t * dx, y = ay + t * dy;
    return Math.sqrt(x * x + y * y);
  }
  function key(i, j) { return i + ',' + j; }

  // routes: [{t: 'clave', color: '#hex', pts: [[lat,lng],...]}] en el orden en que se reparten los trazos
  function layers(routes, weight) {
    var grid = {}, R = routes.map(function (r) { return { t: r.t, color: r.color, pts: densify(r.pts) }; });
    R.forEach(function (r, ri) {
      for (var s = 0; s < r.pts.length - 1; s++) {
        var a = r.pts[s], b = r.pts[s + 1];
        var i0 = Math.floor(Math.min(a[0], b[0]) / STEP), i1 = Math.floor(Math.max(a[0], b[0]) / STEP);
        var j0 = Math.floor(Math.min(a[1], b[1]) / STEP), j1 = Math.floor(Math.max(a[1], b[1]) / STEP);
        for (var i = i0; i <= i1; i++) for (var j = j0; j <= j1; j++) (grid[key(i, j)] = grid[key(i, j)] || []).push([ri, s]);
      }
    });
    var out = [];
    R.forEach(function (r, ri) {
      // para cada tramo, qué giras pasan por ahí
      var sets = [];
      for (var s = 0; s < r.pts.length - 1; s++) {
        var a = r.pts[s], b = r.pts[s + 1], m = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2], found = {};
        found[ri] = 1;
        var ci = Math.floor(m[0] / STEP), cj = Math.floor(m[1] / STEP);
        for (var di = -1; di <= 1; di++) for (var dj = -1; dj <= 1; dj++) {
          (grid[key(ci + di, cj + dj)] || []).forEach(function (e) {
            if (found[e[0]]) return;
            var o = R[e[0]].pts;
            if (segDist(m, o[e[1]], o[e[1] + 1]) < TOL) found[e[0]] = 1;
          });
        }
        sets.push(Object.keys(found).map(Number).sort(function (x, y) { return x - y; }).join('|'));
      }
      // suavizar: un tramo corto (menos de ~4 km) distinto entre dos iguales toma el valor del anterior
      for (var pass = 0; pass < 2; pass++) {
        var k0 = 0;
        for (var k1 = 1; k1 <= sets.length; k1++) {
          if (k1 < sets.length && sets[k1] === sets[k0]) continue;
          if (k0 > 0 && k1 - k0 < 4) for (var z = k0; z < k1; z++) sets[z] = sets[k0 - 1];
          k0 = k1;
        }
      }
      // agrupar tramos seguidos con las mismas giras
      var start = 0;
      for (var s2 = 1; s2 <= sets.length; s2++) {
        if (s2 < sets.length && sets[s2] === sets[start]) continue;
        var who = sets[start].split('|').map(Number), seg = r.pts.slice(start, s2 + 1);
        var opt = { color: r.color, weight: weight, opacity: 0.95, interactive: false, lineCap: 'butt' }, cw = weight + 2.5;
        if (who.length > 1 && SIDE) {
          // una al lado de la otra: todas las giras orientan el tramo igual, así el desplazamiento cae del mismo lado
          var A = seg[0], B = seg[seg.length - 1];
          if (A[1] > B[1] || (A[1] === B[1] && A[0] > B[0])) seg = seg.slice().reverse();
          opt.offset = (who.indexOf(ri) - (who.length - 1) / 2) * weight;
          cw = weight * who.length + 2.5;
        } else if (who.length > 1) {
          opt.dashArray = DASH + ' ' + (DASH * (who.length - 1));
          opt.dashOffset = String(DASH * who.indexOf(ri));
        } else opt.lineCap = 'round';
        out.push({ casing: L.polyline(seg, { color: '#fff', weight: cw, opacity: 0.75, interactive: false }), line: L.polyline(seg, opt) });
        start = s2;
      }
    });
    // primero todos los bordes blancos, después los colores
    return L.layerGroup(out.map(function (o) { return o.casing; }).concat(out.map(function (o) { return o.line; })));
  }

  var cache = {};
  function get(t) {
    if (cache[t]) return Promise.resolve(cache[t]);
    return fetch('/assets/routes/' + t + '.json?v=6').then(function (r) { return r.json(); })
      .then(function (p) { return (cache[t] = p); });
  }
  // dibuja todas las giras; devuelve una promesa con el grupo de capas y todos los puntos
  function drawAll(map, D, weight) {
    var keys = (D.routes || []).slice().sort(function (a, b) { return (D.trips[a] || {}).year - (D.trips[b] || {}).year; });
    return Promise.all(keys.map(function (t) { return get(t).catch(function () { return null; }); })).then(function (list) {
      var routes = [];
      list.forEach(function (p, i) { if (p) routes.push({ t: keys[i], color: (D.trips[keys[i]] || {}).color || '#888', pts: p }); });
      return { group: layers(routes, weight || 3), pts: [].concat.apply([], routes.map(function (r) { return r.pts; })) };
    });
  }
  window.MVRoutes = { get: get, drawAll: drawAll };
})();
