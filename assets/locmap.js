/* Mapa "Dónde queda" para cada página de lugar.
   Uso: <div class="locmap-box" data-n="NN"></div> + leaflet.js + places.js + este archivo.
   Datos en /assets/places.js (generado desde _proyecto/manifest.json). */
(function () {
  var box = document.querySelector('.locmap-box');
  if (!box || !window.PLACES) return;
  var n = +box.getAttribute('data-n');
  var D = window.PLACES, P = D.places;
  var me = P.filter(function (p) { return p.n === n; })[0];
  if (!me) return;
  var col = (D.trips[me.trip] || {}).color || '#2E7CF6';

  var css = document.createElement('style');
  css.textContent =
    '.locmap-box{max-width:640px;margin:0 auto;padding:0 26px;text-align:center;}' +
    '.locmap-box .lm-label{font-family:"Caveat","Playfair Display",cursive;font-size:1.9rem;color:var(--accent-ink,var(--accent));margin:46px 0 4px;}' +
    '.locmap-box .lm-sub{font-size:0.92rem;color:var(--ink-soft);margin:0 0 14px;}' +
    '.locmap-box .lm-map{position:relative;z-index:0;isolation:isolate;height:320px;border-radius:4px;overflow:hidden;box-shadow:0 10px 26px rgba(43,38,32,0.18);background:#E8E2D4;}' +
    '.locmap-box .lm-bar{display:flex;flex-wrap:wrap;justify-content:center;align-items:center;gap:8px;margin:12px 0 0;}' +
    '.locmap-box .lm-bar button{font:600 0.82rem "Source Sans 3",sans-serif;color:var(--ink);background:transparent;border:1.5px solid var(--ink-soft);border-radius:20px;padding:5px 13px;cursor:pointer;opacity:.75;}' +
    '.locmap-box .lm-bar button.on{background:var(--accent);border-color:var(--accent);color:var(--accent-on,#fff);opacity:1;}' +
    '.locmap-box .lm-bar a{font-size:0.82rem;font-weight:600;color:var(--accent-ink,var(--accent));text-decoration:none;margin-left:4px;}' +
    '.locmap-box .lm-hint{font-size:0.78rem;color:var(--ink-soft);margin:8px 0 0;}' +
    '.lm-tip{font:600 13px "Source Sans 3",sans-serif;}' +
    '.lm-pop{font:14px "Source Sans 3",sans-serif;line-height:1.35;}' +
    '.lm-pop b{display:block;font-size:15px;}.lm-pop span{color:#6B6255;font-size:12.5px;}' +
    '.lm-pop a{display:inline-block;margin-top:6px;font-weight:600;text-decoration:none;}';
  document.head.appendChild(css);

  // viajes en los que se visitó este lugar (un lugar puede estar en varios, p. ej. Los Angeles)
  function tripsOf(p) {
    var out = [];
    (p.visits || [{ trip: p.trip }]).forEach(function (v) { if (v.trip && out.indexOf(v.trip) < 0) out.push(v.trip); });
    return out;
  }
  var myTrips = tripsOf(me);
  function tripButtons() {
    if (myTrips.length < 2) return '<button type="button" data-v="trip:' + me.trip + '">Todo el viaje</button>';
    return myTrips.map(function (t) { return '<button type="button" data-v="trip:' + t + '">Viaje ' + D.trips[t].year + '</button>'; }).join('');
  }
  function bg(p) {
    var vs = p.visits || [];
    if (vs.length < 2) return (D.trips[p.trip] || {}).color || '#888';
    var k = 360 / vs.length;
    return 'conic-gradient(' + vs.map(function (v, i) { return v.color + ' ' + (i * k) + 'deg ' + ((i + 1) * k) + 'deg'; }).join(',') + ')';
  }
  function years(p) { return (p.visits || []).map(function (v) { return v.year; }).join(' · '); }
  function dot(size, p, op) {
    return L.divIcon({ className: '', iconSize: [size, size], iconAnchor: [size / 2, size / 2], popupAnchor: [0, -size / 2],
      html: '<div style="width:' + size + 'px;height:' + size + 'px;border-radius:50%;background:' + bg(p) + ';border:' + (size > 14 ? 3 : 1.5) + 'px solid #fff;box-sizing:border-box;box-shadow:0 1px 3px rgba(0,0,0,.35);opacity:' + op + '"></div>' });
  }

  box.innerHTML =
    '<p class="lm-label">Dónde queda</p>' +
    '<p class="lm-sub">' + me.name + (me.sub ? ' · ' + me.sub : '') + '</p>' +
    '<div class="lm-map"></div>' +
    '<div class="lm-bar">' +
      '<button type="button" data-v="here" class="on">El lugar</button>' +
      tripButtons() +
      '<button type="button" data-v="all">Los 45 lugares</button>' +
      '<a target="_blank" rel="noopener" href="https://www.google.com/maps/search/?api=1&query=' + me.lat + ',' + me.lng + '">Abrir en Google Maps ↗</a>' +
    '</div>' +
    '<p class="lm-hint">Tocá cualquier punto para ver qué lugar es e ir a su página' + (('ontouchstart' in window) ? ' · con dos dedos acercás y movés el mapa' : '') + '.</p>';

  if (!window.L) { box.style.display = 'none'; return; }
  var touch = ('ontouchstart' in window) || navigator.maxTouchPoints > 0;
  var map = L.map(box.querySelector('.lm-map'), {
    scrollWheelZoom: false,
    dragging: !touch,          // en el celular no "secuestra" el scroll de la página
    tap: false,
    zoomSnap: 0.5
  });
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18, attribution: '&copy; OpenStreetMap'
  }).addTo(map);
  function popup(p) {
    var t = D.trips[p.trip] || {};
    return '<div class="lm-pop"><b>#' + p.n + ' · ' + p.name + '</b><span>' + (p.sub || '') +
      ' — ' + (years(p) || t.year) + '</span>' +
      (p.n === n ? '' : '<br><a style="color:' + (p.trip === '2022' ? '#8A6800' : t.color) + '" href="' + p.url + '">Ir a la página →</a>') + '</div>';
  }
  var tripPts = {}, allPts = [];
  P.forEach(function (p) {
    allPts.push([p.lat, p.lng]);
    tripsOf(p).forEach(function (t) { (tripPts[t] = tripPts[t] || []).push([p.lat, p.lng]); });
    if (p.n === n) return;
    var same = tripsOf(p).some(function (t) { return myTrips.indexOf(t) >= 0; });
    L.marker([p.lat, p.lng], { icon: dot(same ? 12 : 9, p, same ? 1 : 0.55) }).bindPopup(popup(p)).addTo(map);
  });
  // halo + punto principal (con los colores de cada visita)
  L.circleMarker([me.lat, me.lng], { radius: 16, stroke: false, fillColor: col, fillOpacity: 0.22, interactive: false }).addTo(map);
  L.marker([me.lat, me.lng], { icon: dot(20, me, 1), zIndexOffset: 1000 })
    .bindPopup(popup(me))
    .bindTooltip(me.name, { permanent: true, direction: 'top', offset: [0, -10], className: 'lm-tip' })
    .addTo(map);

  function view(v) {
    box.querySelectorAll('.lm-bar button').forEach(function (b) { b.classList.toggle('on', b.getAttribute('data-v') === v); });
    if (v === 'here') map.setView([me.lat, me.lng], me.z || 10);
    else map.fitBounds(v.indexOf('trip:') === 0 ? tripPts[v.slice(5)] : allPts, { padding: [30, 30], maxZoom: 10 });
  }
  box.querySelector('.lm-bar').addEventListener('click', function (e) {
    var b = e.target.closest('button'); if (b) view(b.getAttribute('data-v'));
  });
  view('here');
})();
