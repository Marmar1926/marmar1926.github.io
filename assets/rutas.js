/* Dibuja los recorridos de las giras en un mapa Leaflet.
   Donde dos o más giras usaron la misma ruta, las líneas van una al lado de la otra
   (o con trazos alternados), para que se vean todos los colores.
   Los tramos en avión se dibujan como una curva punteada con un avioncito. */
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

  // routes: [{t: 'clave', ti: nº de gira, color: '#hex', pts: [[lat,lng],...]}]; una gira puede tener varios tramos en auto
  function layers(routes, weight) {
    var grid = {}, R = routes.map(function (r) { return { t: r.t, ti: r.ti, color: r.color, pts: densify(r.pts) }; });
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
        found[r.ti] = 1;
        var ci = Math.floor(m[0] / STEP), cj = Math.floor(m[1] / STEP);
        for (var di = -1; di <= 1; di++) for (var dj = -1; dj <= 1; dj++) {
          (grid[key(ci + di, cj + dj)] || []).forEach(function (e) {
            var oti = R[e[0]].ti; if (found[oti]) return;
            var o = R[e[0]].pts;
            if (segDist(m, o[e[1]], o[e[1] + 1]) < TOL) found[oti] = 1;
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
          opt.offset = (who.indexOf(r.ti) - (who.length - 1) / 2) * weight;
          cw = weight * who.length + 2.5;
        } else if (who.length > 1) {
          opt.dashArray = DASH + ' ' + (DASH * (who.length - 1));
          opt.dashOffset = String(DASH * who.indexOf(r.ti));
        } else opt.lineCap = 'round';
        out.push({ casing: L.polyline(seg, { color: '#fff', weight: cw, opacity: 0.75, interactive: false }), line: L.polyline(seg, opt) });
        start = s2;
      }
    });
    // primero todos los bordes blancos, después los colores
    return L.layerGroup(out.map(function (o) { return o.casing; }).concat(out.map(function (o) { return o.line; })));
  }

  // tramo en avión: curva punteada con un avioncito en el medio
  function flight(a, b, color, weight) {
    var lat1 = a[0], lng1 = a[1], lat2 = b[0], lng2 = b[1];
    var mx = (lat1 + lat2) / 2, my = (lng1 + lng2) / 2, dx = lat2 - lat1, dy = lng2 - lng1;
    var c = [mx + dy * 0.18, my - dx * 0.18], pts = [];   // punto de control, desplazado hacia un costado
    for (var i = 0; i <= 40; i++) {
      var t = i / 40, u = 1 - t;
      pts.push([u * u * lat1 + 2 * u * t * c[0] + t * t * lat2, u * u * lng1 + 2 * u * t * c[1] + t * t * lng2]);
    }
    // rumbo en pantalla (Mercator): 0° = hacia arriba, sentido horario; el avión mira hacia donde va
    var mid = pts[20], pv = pts[19], nx = pts[21];
    var east = nx[1] - pv[1], north = (nx[0] - pv[0]) / Math.cos(mid[0] * Math.PI / 180);
    var ang = Math.atan2(east, north) * 180 / Math.PI;
    var svg = '<svg viewBox="0 0 24 24" width="16" height="16" style="display:block;transform:rotate(' + ang.toFixed(1) + 'deg)">' +
      '<path fill="' + color + '" d="M12 1.5c.9 0 1.5 1 1.5 2.2V9l8 4.6v2.1l-8-2.4v5.1l2.4 1.8v1.7L12 21l-3.9.9v-1.7l2.4-1.8v-5.1l-8 2.4v-2.1l8-4.6V3.7c0-1.2.6-2.2 1.5-2.2z"/></svg>';
    var plane = L.marker(mid, { interactive: false, keyboard: false, zIndexOffset: -1000, icon: L.divIcon({ className: '', iconSize: [24, 24], iconAnchor: [12, 12],
      html: '<div style="width:24px;height:24px;border-radius:50%;background:#fff;box-shadow:0 1px 3px rgba(0,0,0,.35);display:flex;align-items:center;justify-content:center">' + svg + '</div>' }) });
    return { line: L.polyline(pts, { color: color, weight: Math.max(2, weight - 0.5), opacity: 0.9, dashArray: '2 7', lineCap: 'round', interactive: false }),
             casing: L.polyline(pts, { color: '#fff', weight: weight + 1.5, opacity: 0.55, dashArray: '2 7', lineCap: 'round', interactive: false }),
             plane: plane, pts: pts };
  }
  // un archivo de recorrido puede ser una lista de puntos (todo en auto) o {auto: [[...],...], avion: [[a,b],...]}
  function parts(data) {
    if (Array.isArray(data)) return { auto: [data], avion: [] };
    return { auto: data.auto || [], avion: data.avion || [] };
  }
  // una sola gira (botón «Viaje AAAA»)
  function tripLayer(t, data, color, weight) {
    var p = parts(data), g = L.layerGroup(), all = [];
    p.auto.forEach(function (pts) {
      g.addLayer(L.polyline(pts, { color: '#fff', weight: weight + 2.5, opacity: 0.7, interactive: false }));
      all = all.concat(pts);
    });
    p.auto.forEach(function (pts) { g.addLayer(L.polyline(pts, { color: color, weight: weight, opacity: 0.95, interactive: false })); });
    p.avion.forEach(function (ab) { var f = flight(ab[0], ab[1], color, weight); g.addLayer(f.casing); g.addLayer(f.line); g.addLayer(f.plane); all = all.concat(f.pts); });
    return { group: g, pts: all };
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
      var routes = [], flights = [], w = weight || 3;
      list.forEach(function (d, i) {
        if (!d) return;
        var c = (D.trips[keys[i]] || {}).color || '#888', p = parts(d);
        p.auto.forEach(function (pts) { routes.push({ t: keys[i], ti: i, color: c, pts: pts }); });
        p.avion.forEach(function (ab) { flights.push(flight(ab[0], ab[1], c, w)); });
      });
      var g = layers(routes, w);
      flights.forEach(function (f) { g.addLayer(f.casing); g.addLayer(f.line); g.addLayer(f.plane); });
      var pts = [].concat.apply([], routes.map(function (r) { return r.pts; }).concat(flights.map(function (f) { return f.pts; })));
      return { group: g, pts: pts };
    });
  }

  // ---- mapa a pantalla completa (botón ⤢ en la esquina del mapa) ----
  var fsCss = false;
  function fsStyles() {
    if (fsCss) return; fsCss = true;
    var st = document.createElement('style');
    st.textContent =
      'html.mv-fs-on,html.mv-fs-on body{overflow:hidden!important;}' +
      '.mv-fs.mv-fs{position:fixed!important;inset:0!important;z-index:9000!important;margin:0!important;max-width:none!important;width:auto!important;' +
        'display:flex!important;flex-direction:column;background:#F6F1E7;' +
        'padding:calc(6px + env(safe-area-inset-top,0px)) max(8px,env(safe-area-inset-right,0px)) calc(8px + env(safe-area-inset-bottom,0px)) max(8px,env(safe-area-inset-left,0px))!important;}' +
      '.mv-fs > *{flex-shrink:0;}' +
      '.mv-fs .mv-fs-map{flex:1 1 auto!important;height:auto!important;min-height:0;border-radius:6px!important;}' +
      '.mv-fs .lm-label,.mv-fs .lm-hint,.mv-fs .map-hint{display:none!important;}' +
      '.mv-fs .lm-sub{margin:0 0 6px!important;font-size:.85rem!important;}' +
      '.mv-fs .lm-bar,.mv-fs .map-legend{flex-wrap:nowrap!important;justify-content:flex-start!important;overflow-x:auto;padding-bottom:2px;margin-top:8px!important;scrollbar-width:none;}' +
      '.mv-fs .lm-bar > *,.mv-fs .map-legend > *{flex-shrink:0;}' +
      '.mv-fsbtn{width:34px;height:34px;display:flex;align-items:center;justify-content:center;background:#fff;border:none;cursor:pointer;color:#2B2620;}' +
      '.mv-fsbtn svg{width:18px;height:18px;}';
    document.head.appendChild(st);
  }
  var ICON_OPEN = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/></svg>';
  var ICON_CLOSE = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>';
  // box: el bloque que pasa a ocupar toda la pantalla (mapa + botones); mapEl: el div del mapa
  function fullscreen(map, box, mapEl, touch) {
    fsStyles();
    mapEl.classList.add('mv-fs-map');
    var on = false, btn;
    var Ctl = L.Control.extend({ options: { position: 'topright' }, onAdd: function () {
      var d = L.DomUtil.create('div', 'leaflet-bar');
      btn = L.DomUtil.create('button', 'mv-fsbtn', d); btn.type = 'button';
      btn.title = 'Ver el mapa en pantalla completa'; btn.setAttribute('aria-label', btn.title); btn.innerHTML = ICON_OPEN;
      L.DomEvent.disableClickPropagation(d);
      L.DomEvent.on(btn, 'click', function () { on ? close(true) : open(); });
      return d;
    } });
    map.addControl(new Ctl());
    var ph = null;
    function set(v) {
      on = v;
      // se mueve al final de la página mientras está a pantalla completa, para quedar por encima de todo
      if (v) { ph = document.createComment('mapa'); box.parentNode.insertBefore(ph, box); document.body.appendChild(box); }
      else if (ph) { ph.parentNode.insertBefore(box, ph); ph.remove(); ph = null; }
      box.classList.toggle('mv-fs', v);
      if (v) box.style.setProperty('margin', '0', 'important'); else box.style.removeProperty('margin'); document.documentElement.classList.toggle('mv-fs-on', v);
      btn.innerHTML = v ? ICON_CLOSE : ICON_OPEN;
      btn.title = v ? 'Cerrar pantalla completa' : 'Ver el mapa en pantalla completa'; btn.setAttribute('aria-label', btn.title);
      if (touch) { if (v) map.dragging.enable(); else map.dragging.disable(); }
      var c = map.getCenter(), z = map.getZoom();
      setTimeout(function () { map.invalidateSize(); map.setView(c, z, { animate: false }); }, 60);
    }
    function open() { set(true); try { history.pushState({ mvfs: 1 }, ''); } catch (e) {} }
    function close(fromBtn) { if (!on) return; set(false); if (fromBtn) { try { if (history.state && history.state.mvfs) history.back(); } catch (e) {} } }
    // el botón «atrás» del teléfono cierra la pantalla completa en vez de salir de la página
    window.addEventListener('popstate', function () { if (on) close(false); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && on) close(true); });
  }
  window.MVRoutes = { get: get, drawAll: drawAll, tripLayer: tripLayer, flight: flight, fullscreen: fullscreen };
})();
