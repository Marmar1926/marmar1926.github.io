/* Mejoras visuales comunes a todas las páginas de lugares:
   título sobre la portada, sello de pasaporte, tira de miniaturas en la galería
   y aparición suave de las fotos. No cambia el contenido de cada página. */
(function(){
  var css = ''
  + '.hero-in{position:relative;width:fit-content;max-width:100%;margin:0 auto;}'
  + '.hero-in{overflow:hidden;}'
  + '.hero-in img{display:block;}'
  + '.hero-in.hit{animation:heroHit .28s ease-out;}'
  + '@keyframes heroHit{0%{transform:translate(0,0)}30%{transform:translate(0,3px)}60%{transform:translate(0,-1px)}100%{transform:none}}'
  + '.hero-ov h1,.hero-ov .location{transform-origin:left bottom;animation:titleIn .55s cubic-bezier(.3,.7,.4,1) both;}'
  + '.hero-ov h1{animation-delay:.3s}.hero-ov .location{animation-delay:.5s}'
  + '@keyframes titleIn{0%{transform:scale(1.9);opacity:0}60%{transform:scale(.96);opacity:1}80%{transform:scale(1.02)}100%{transform:none;opacity:1}}'
  + '@media (prefers-reduced-motion:reduce){.hero-in,.hero-ov h1,.hero-ov .location,.stamp{animation:none!important}}'
  + '.hero-ov{position:absolute;left:0;right:0;bottom:0;padding:70px 22px 16px;background:linear-gradient(180deg,rgba(20,15,10,0),rgba(20,15,10,.78));color:#fff;}'
  + '.hero-ov h1{color:#fff!important;margin:0!important;text-shadow:0 2px 10px rgba(0,0,0,.5);}'
  + '.hero-ov .location{color:rgba(255,255,255,.92)!important;margin:2px 0 0!important;}'
  + '.stamp{position:absolute;top:12px;right:12px;width:96px;height:96px;border-radius:50%;border:3px solid var(--st);outline:1.5px dashed var(--st);outline-offset:-9px;background:rgba(247,242,231,.9);color:var(--st);display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;font:700 .58rem "Source Sans 3",sans-serif;letter-spacing:.8px;text-transform:uppercase;line-height:1.15;padding:0 10px;transform:rotate(-12deg);animation:stampIn .5s ease-out 1s both;pointer-events:none;}'
  + '.stamp b{font-size:1.15rem;letter-spacing:0;line-height:1.1;margin:1px 0;}'
  + '.stamp b.sm{font-size:.82rem;}'
  + '.stamp b.xs{font-size:.66rem;max-width:72px;line-height:1.15;}'
  + '.stamp span.lg{font-size:.5rem;letter-spacing:.4px;max-width:70px;}'
  + '@keyframes stampIn{from{transform:rotate(-12deg) scale(2.2);opacity:0}to{transform:rotate(-12deg) scale(1);opacity:1}}'
  + '.carousel-track img.fx{opacity:0;transition:opacity .5s ease;}'
  + '.carousel-track img.fx.ok{opacity:1;}'
  + '.thumbs{display:flex;gap:6px;overflow-x:auto;padding:10px 2px 4px;scrollbar-width:none;-webkit-overflow-scrolling:touch;}'
  + '.thumbs::-webkit-scrollbar{display:none;}'
  + '.thumbs img{width:62px;height:46px;object-fit:cover;border-radius:3px;flex-shrink:0;opacity:.55;cursor:pointer;border:2px solid transparent;background:var(--paper-2,#EFE7D6);}'
  + '.thumbs img.on{opacity:1;border-color:var(--st);}'
  + '.thumbs.hide{display:none;}'
  + '.hero-in~*{}.place-header{padding-top:14px!important;}';
  var st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);

  // color y años del viaje, tomados de las pastillas de la página
  var pills = [].slice.call(document.querySelectorAll('.visit-years .pill'));
  var years = [], ycol = {}; pills.forEach(function(p){ var m = (p.textContent || '').match(/\d{4}/), d = p.querySelector('span'); if (m && years.indexOf(m[0]) < 0) { years.push(m[0]); ycol[m[0]] = (d && d.style.background) || ''; } }); years.sort();
  function dark(c){ return /241,\s*196,\s*15|f1c40f/i.test(c) ? '#B08600' : c; }
  var dot = pills.length && pills[0].querySelector('span');
  var color = (dot && dot.style.background) || '#8A6800';
  if (/241,\s*196,\s*15|f1c40f/i.test(color)) color = '#B08600'; // amarillo 2022: más oscuro para leerse
  document.documentElement.style.setProperty('--st', color);

  // título sobre la portada + sello
  var hero = document.querySelector('.hero'), himg = hero && hero.querySelector('img');
  var h1 = document.querySelector('.place-header h1, .content h1');
  var loc = document.querySelector('.place-header .location, .content .location');
  if (hero && himg && h1) {
    var wrap = document.createElement('div'); wrap.className = 'hero-in';
    himg.parentNode.insertBefore(wrap, himg); wrap.appendChild(himg);
    var ov = document.createElement('div'); ov.className = 'hero-ov';
    ov.appendChild(h1); if (loc) ov.appendChild(loc);
    wrap.appendChild(ov);
    var name = h1.textContent.trim();
    var state = loc ? loc.textContent.split('·')[0].split(',').pop().trim() : '';
    var s = document.createElement('div'); s.className = 'stamp';
    s.innerHTML = '<span' + (name.length > 11 ? ' class="lg"' : '') + '></span><b' + (years.length > 2 ? ' class="xs"' : years.length > 1 ? ' class="sm"' : '') + '></b><span></span>';
    s.children[0].textContent = name; years.forEach(function(y, k){ if (k) s.children[1].appendChild(document.createTextNode(years.length > 2 ? ' ' : ' · ')); var e = document.createElement('i'); e.textContent = y; e.style.color = dark(ycol[y]) || ''; e.style.fontStyle = 'normal'; s.children[1].appendChild(e); }); s.children[2].textContent = state;
    wrap.appendChild(s);
  }

  // aparición suave de las fotos de la galería
  var track = document.getElementById('track');
  function fx(img){
    if (img.tagName !== 'IMG' || img.dataset.fx) return; img.dataset.fx = 1;
    if (img.complete && img.naturalWidth) return;
    img.classList.add('fx');
    var done = function(){ img.classList.add('ok'); };
    img.addEventListener('load', done); img.addEventListener('error', done);
  }

  // tira de miniaturas
  var count = document.getElementById('count'), next = document.getElementById('nextBtn'), prev = document.getElementById('prevBtn');
  var carousel = document.getElementById('carousel');
  if (!track || !count || !next || !prev || !carousel) return;
  var tb = document.createElement('div'); tb.className = 'thumbs';
  carousel.parentNode.insertBefore(tb, carousel.nextSibling);
  function cur(){ var m = (count.textContent || '').match(/(\d+)\s*\/\s*(\d+)/); return m ? [+m[1] - 1, +m[2]] : [0, 0]; }
  function build(){
    tb.innerHTML = '';
    [].forEach.call(track.children, function(el, k){
      fx(el);
      var src = el.tagName === 'VIDEO' ? el.getAttribute('poster') : (el.getAttribute('src') || '');
      var t = new Image(); t.loading = 'lazy'; t.decoding = 'async'; t.alt = ''; t.src = src || '';
      t.addEventListener('click', function(){
        var c = cur(), n = c[1]; if (!n) return;
        var d = k - c[0]; if (!d) return;
        var fwd = ((d % n) + n) % n, back = n - fwd;
        var b = fwd <= back ? next : prev, times = Math.min(fwd, back);
        for (var i = 0; i < times; i++) b.click();
      });
      tb.appendChild(t);
    });
    mark();
  }
  function mark(){
    var hidden = carousel.classList.contains('hide') || track.children.length < 2;
    tb.classList.toggle('hide', hidden);
    var i = cur()[0];
    [].forEach.call(tb.children, function(t, k){ t.classList.toggle('on', k === i); });
    var a = tb.children[i];
    if (a && !hidden) tb.scrollTo({ left: a.offsetLeft - tb.clientWidth / 2 + 31, behavior: 'smooth' });
  }
  new MutationObserver(build).observe(track, { childList: true });
  new MutationObserver(mark).observe(count, { childList: true, characterData: true, subtree: true });
  new MutationObserver(mark).observe(carousel, { attributes: true, attributeFilter: ['class'] });
  build();
})();

/* Cierre de página: "Dónde queda", anterior/siguiente, botón al índice y pie */
(function(){
  var css = ''
  + '.locmap-box{margin-top:10px!important;}'
  + '.locmap-box .lm-label{font-family:"Playfair Display",serif!important;font-size:1.45rem!important;color:var(--ink)!important;margin:40px 0 2px!important;}'
  + '.locmap-box .lm-label::before{content:"";display:block;width:44px;height:3px;border-radius:2px;background:var(--st);margin:0 auto 14px;}'
  + '.locmap-box .lm-map{border-radius:10px!important;}'
  + '.locmap-box .lm-hint{opacity:.85;}'
  + '.pn2{max-width:640px;margin:34px auto 0;padding:0 20px;display:grid;grid-template-columns:1fr 1fr;gap:10px;}'
  + '.pn2 a{display:flex;align-items:center;gap:10px;padding:10px;border-radius:10px;background:var(--paper-2,#EFE7D6);text-decoration:none;color:var(--ink);box-shadow:0 2px 8px rgba(43,38,32,.08);min-width:0;}'
  + '.pn2 a.nx{flex-direction:row-reverse;text-align:right;}'
  + '.pn2 img{width:54px;height:54px;object-fit:cover;border-radius:7px;flex-shrink:0;}'
  + '.pn2 .tx{display:flex;flex-direction:column;min-width:0;}'
  + '.pn2 small{font-size:.68rem;letter-spacing:.8px;text-transform:uppercase;color:var(--ink-soft);}'
  + '.pn2 b{font-size:.92rem;line-height:1.2;overflow:hidden;text-overflow:ellipsis;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;}'
  + '.pn2 i{font-style:normal;font-size:.75rem;font-weight:700;}'
  + '.closing-cta{display:flex!important;align-items:center;justify-content:center;gap:8px;width:fit-content;max-width:calc(100% - 40px);margin:26px auto 0!important;padding:12px 22px!important;border:none!important;border-radius:30px!important;background:var(--ink,#2B2620)!important;color:#fff!important;font-size:.92rem!important;box-shadow:0 6px 16px rgba(43,38,32,.2);}'
  + '.foot2{display:block!important;max-width:640px;margin:44px auto 0;padding:22px 20px 40px;border-top:1px solid var(--line,#D9CFB8);text-align:center;color:var(--ink-soft);}'
  + '.foot2 .t{font-family:"Playfair Display",serif;font-size:1.15rem;color:var(--ink);margin:0 0 6px;}'
  + '.foot2 .m{font-size:.82rem;margin:0;}'
  + '.foot2 .y{display:flex;justify-content:center;gap:5px;margin:12px 0 0;}'
  + '.foot2 .y span{width:9px;height:9px;border-radius:50%;}';
  var st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);

  var D = window.PLACES, places = (D && D.places) || [];
  var urls = places.map(function(p){ return p.url; }).slice().sort();
  function byUrl(u){ for (var i = 0; i < places.length; i++) if (places[i].url === u) return places[i]; return null; }
  function thumb(u){ var k = urls.indexOf(u); return k < 0 ? '' : '/assets/cover/' + (k < 10 ? '0' : '') + k + '.jpg'; }
  function col(c){ return /241,\s*196,\s*15|f1c40f/i.test(c || '') ? '#B08600' : c; }
  var here = byUrl(location.pathname.replace(/index\.html$/, ''));

  // anterior / siguiente como tarjetas
  var pn = document.querySelector('.prevnext');
  if (pn) {
    var box = document.createElement('nav'); box.className = 'pn2';
    [['prev','Anterior','pv'],['next','Siguiente','nx']].forEach(function(t){
      var a = pn.querySelector('a.' + t[0]); if (!a) { box.appendChild(document.createElement('span')); return; }
      var u = a.getAttribute('href'), p = byUrl(u);
      var name = p ? p.name : a.textContent.replace(/[←→]/g, '').trim();
      var c = p ? col((p.visits && p.visits[0] && p.visits[0].color) || ((D.trips[p.trip] || {}).color)) : '';
      var yrs = p && p.visits ? p.visits.map(function(v){ return '<span style="color:' + col(v.color) + '">' + v.year + '</span>'; }).join(' · ') : '';
      var n = document.createElement('a'); n.href = u; n.className = t[2];
      n.innerHTML = (thumb(u) ? '<img loading="lazy" alt="" src="' + thumb(u) + '">' : '') +
        '<span class="tx"><small>' + (t[0] === 'prev' ? '← ' : '') + t[1] + (t[0] === 'next' ? ' →' : '') + '</small><b></b><i>' + yrs + '</i></span>';
      n.querySelector('b').textContent = name;
      box.appendChild(n);
    });
    pn.parentNode.replaceChild(box, pn);
  }

  // botón al índice
  var cta = document.querySelector('.closing-cta');
  if (cta) cta.textContent = 'Ver los 45 lugares en el índice →';

  // pie de página
  var ft = document.querySelector('body > footer');
  if (ft) {
    var num = (ft.textContent.match(/#\s*(\d+)/) || [])[1] || (here ? here.n : '');
    var f = document.createElement('footer'); f.className = 'foot2';
    var tr = D && D.trips ? Object.keys(D.trips).map(function(k){ return D.trips[k]; }) : [];
    if (!tr.some(function(t){ return t.year == 2019; })) tr.push({ year: 2019, color: '#17A2B8' });
    tr.sort(function(a, b){ return a.year - b.year; });
    f.innerHTML = '<p class="t">Mis viajes por USA</p>' +
      '<p class="m">' + (num ? 'Lugar #' + num + ' de 45 · ' : '') + '7 viajes · 15 estados · 15.034 km</p>' +
      '<div class="y">' + tr.map(function(t){ return '<span title="' + t.year + '" style="background:' + t.color + '"></span>'; }).join('') + '</div>';
    ft.parentNode.replaceChild(f, ft);
  }
})();
