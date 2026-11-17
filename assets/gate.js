/* Clave liviana para el sitio "Mis viajes por USA".
   No es seguridad fuerte: evita que entre quien solo tenga un QR o la dirección.
   Para cambiar la clave: H = sha256("mv-salt:" + CLAVE).
   La clave se pide cada vez que se abre el sitio (vale mientras el navegador siga abierto
   y se pierde tras 2 horas sin uso). Solo si se tilda «Recordar en este dispositivo»
   queda guardada 30 días: así un televisor ajeno nunca queda con el sitio abierto. */
(function () {
  var H = '89cf0ffde49b52cd21f085f00d541b0b57f9c0b4a03deeda935d9bfac1616ad4';
  var IDLE = 2 * 3600e3, REMEMBER = 30 * 864e5, now = Date.now();
  function rd(store, k) { try { return JSON.parse(store.getItem(k) || 'null'); } catch (e) { return null; } }
  function wr(store, k, v) { try { store.setItem(k, JSON.stringify(v)); } catch (e) {} }
  // la versión anterior guardaba la clave para siempre: se borra
  try { localStorage.removeItem('mvk'); } catch (e) {}
  var ses = rd(sessionStorage, 'mvs'), rem = rd(localStorage, 'mvr');
  if ((ses && ses.h === H && now - ses.t < IDLE) || (rem && rem.h === H && now < rem.exp)) {
    wr(sessionStorage, 'mvs', { h: H, t: now });
    return;
  }
  try { sessionStorage.removeItem('mvs'); localStorage.removeItem('mvr'); } catch (e) {}
  var d = document.documentElement; d.className += ' mv-lock';
  var st = document.createElement('style');
  st.textContent = 'html.mv-lock body>*:not(#mv-gate){display:none!important}' +
    '#mv-gate{position:fixed;top:0;right:0;bottom:0;left:0;z-index:99999;display:-webkit-flex;display:flex;-webkit-align-items:center;align-items:center;-webkit-justify-content:center;justify-content:center;padding:16px;' +
    'background:#13254a;background:radial-gradient(ellipse at 30% 20%,#1f3a6b 0%,#13254a 55%,#0c1934 100%);font-family:"Source Sans 3",system-ui,sans-serif;color:#E8CD82}' +
    '#mv-gate .bx{width:100%;max-width:340px;border:1px solid rgba(227,199,122,.5);border-radius:12px;padding:28px 24px;text-align:center}' +
    '#mv-gate h1{font-family:"Playfair Display",Georgia,serif;font-size:1.25rem;letter-spacing:2px;margin:0 0 4px;color:#F0D78C}' +
    '#mv-gate p{margin:0 0 18px;font-size:.9rem;color:#D9BD72}' +
    '#mv-gate input[type=password]{width:100%;box-sizing:border-box;font-size:1.05rem;padding:12px 14px;border-radius:8px;border:1px solid #C9A24A;background:#F7F2E7;color:#2B2620;text-align:center;letter-spacing:2px}' +
    '#mv-gate label{display:block;margin:14px 0 0;font-size:.85rem;color:#D9BD72;cursor:pointer}' +
    '#mv-gate label input{margin:0 6px 0 0;vertical-align:middle;width:16px;height:16px}' +
    '#mv-gate label small{display:block;font-size:.72rem;opacity:.75;margin-top:2px}' +
    '#mv-gate button{margin-top:14px;width:100%;padding:12px;border:0;border-radius:8px;background:#C9A24A;color:#13254a;font-weight:700;font-size:1rem;cursor:pointer}' +
    '#mv-gate .er{min-height:1.2em;margin:10px 0 0;font-size:.85rem;color:#ffb4a8}';
  (document.head || d).appendChild(st);
  function hex(buf) { return Array.prototype.map.call(new Uint8Array(buf), function (b) { return ('0' + b.toString(16)).slice(-2); }).join(''); }
  function check(v) {
    if (!(window.crypto && crypto.subtle)) return Promise.resolve(false);
    return crypto.subtle.digest('SHA-256', new TextEncoder().encode('mv-salt:' + v.trim())).then(function (b) { return hex(b) === H; });
  }
  function build() {
    var g = document.createElement('div'); g.id = 'mv-gate';
    g.innerHTML = '<form class="bx"><h1>MIS VIAJES POR USA</h1><p>Ingresá la clave para ver el sitio</p>' +
      '<input type="password" autocomplete="off" aria-label="Clave" autofocus>' +
      '<label><input type="checkbox" id="mv-rem">Recordar en este dispositivo<small>Solo en tu teléfono o tu compu, nunca en un TV ajeno</small></label>' +
      '<button type="submit">Entrar</button><div class="er" aria-live="polite"></div></form>';
    document.body.appendChild(g);
    var f = g.querySelector('form'), inp = g.querySelector('input[type=password]'), er = g.querySelector('.er');
    f.addEventListener('submit', function (ev) {
      ev.preventDefault();
      check(inp.value).then(function (ok) {
        if (!ok) { er.textContent = 'Clave incorrecta'; inp.select(); return; }
        var t = Date.now();
        wr(sessionStorage, 'mvs', { h: H, t: t });
        if (g.querySelector('#mv-rem').checked) wr(localStorage, 'mvr', { h: H, exp: t + REMEMBER });
        g.parentNode.removeChild(g); d.className = d.className.replace(/\s*mv-lock/g, '');
        var e = document.createEvent('Event'); e.initEvent('resize', true, true); window.dispatchEvent(e);
      });
    });
  }
  if (document.body) build(); else document.addEventListener('DOMContentLoaded', build);
})();
