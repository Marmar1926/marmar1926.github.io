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
  + '.stamp{position:absolute;top:12px;right:12px;width:96px;height:96px;border-radius:50%;border:3px solid var(--st);outline:1.5px dashed var(--st);outline-offset:-9px;background:rgba(247,242,231,.86);color:var(--st);display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;font:800 .58rem "Source Sans 3",sans-serif;letter-spacing:.8px;text-transform:uppercase;line-height:1.15;padding:0 10px;transform:rotate(-12deg);opacity:.95;animation:stampIn .6s cubic-bezier(.5,0,.6,1) 1s both;pointer-events:none;-webkit-mask-image:url("data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22140%22 height=%22140%22%3E%3Cfilter id=%22n%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%22.85%22 numOctaves=%222%22 seed=%227%22/%3E%3CfeColorMatrix values=%220 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -2.6 2.35%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23n)%22/%3E%3C/svg%3E");mask-image:url("data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22140%22 height=%22140%22%3E%3Cfilter id=%22n%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%22.85%22 numOctaves=%222%22 seed=%227%22/%3E%3CfeColorMatrix values=%220 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -2.6 2.15%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23n)%22/%3E%3C/svg%3E");-webkit-mask-size:140px;mask-size:140px;}'
  + '.stamp b{font-size:1.15rem;letter-spacing:0;line-height:1.1;margin:1px 0;}'
  + '.stamp b.sm{font-size:.82rem;}'
  + '.stamp span.lg{font-size:.5rem;letter-spacing:.4px;max-width:70px;}'
  + '@keyframes stampIn{0%{transform:rotate(-24deg) scale(2.6);opacity:0;filter:blur(2px) drop-shadow(0 14px 10px rgba(0,0,0,.4))}55%{transform:rotate(-12deg) scale(.9);opacity:1;filter:none}70%{transform:rotate(-12deg) scale(1.05)}85%{transform:rotate(-12deg) scale(.98)}100%{transform:rotate(-12deg) scale(1);opacity:.95}}'
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
  var years = []; pills.forEach(function(p){ var m = (p.textContent || '').match(/\d{4}/); if (m && years.indexOf(m[0]) < 0) years.push(m[0]); }); years.sort();
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
    var yt = years.length > 2 ? years[0] + '–' + years[years.length - 1] : years.join(' · ');
    s.innerHTML = '<span' + (name.length > 11 ? ' class="lg"' : '') + '></span><b' + (yt.length > 5 ? ' class="sm"' : '') + '></b><span></span>';
    s.children[0].textContent = name; s.children[1].textContent = yt || ''; s.children[2].textContent = state;
    wrap.appendChild(s);
    s.addEventListener('animationend', function(){ wrap.classList.add('hit'); }, { once: true });
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
