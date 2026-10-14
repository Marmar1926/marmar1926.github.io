/* Clave liviana para el sitio "Mis viajes por USA".
   No es seguridad fuerte: evita que entre quien solo tenga un QR o la dirección.
   Para cambiar la clave: H = sha256("mv-salt:" + CLAVE). */
(function () {
  var H = 'db58e3a0d16713ea564e386b6aa983f6df33336aed8f919474f5ab36c9007aee';
  try { if (localStorage.getItem('mvk') === H) return; } catch (e) {}
  var d = document.documentElement; d.classList.add('mv-lock');
  var st = document.createElement('style');
  st.textContent = 'html.mv-lock body>*:not(#mv-gate){display:none!important}' +
    '#mv-gate{position:fixed;inset:0;z-index:99999;display:flex;align-items:center;justify-content:center;padding:16px;' +
    'background:radial-gradient(ellipse at 30% 20%,#1f3a6b 0%,#13254a 55%,#0c1934 100%);font-family:"Source Sans 3",system-ui,sans-serif;color:#E8CD82}' +
    '#mv-gate .bx{width:100%;max-width:340px;border:1px solid rgba(227,199,122,.5);border-radius:12px;padding:28px 24px;text-align:center}' +
    '#mv-gate h1{font-family:"Playfair Display",Georgia,serif;font-size:1.25rem;letter-spacing:2px;margin:0 0 4px;color:#F0D78C}' +
    '#mv-gate p{margin:0 0 18px;font-size:.9rem;color:#D9BD72}' +
    '#mv-gate input{width:100%;box-sizing:border-box;font-size:1.05rem;padding:12px 14px;border-radius:8px;border:1px solid #C9A24A;background:#F7F2E7;color:#2B2620;text-align:center;letter-spacing:2px}' +
    '#mv-gate button{margin-top:12px;width:100%;padding:12px;border:0;border-radius:8px;background:#C9A24A;color:#13254a;font-weight:700;font-size:1rem;cursor:pointer}' +
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
      '<input type="password" autocomplete="current-password" aria-label="Clave" autofocus>' +
      '<button type="submit">Entrar</button><div class="er" aria-live="polite"></div></form>';
    document.body.appendChild(g);
    var f = g.querySelector('form'), inp = g.querySelector('input'), er = g.querySelector('.er');
    f.addEventListener('submit', function (ev) {
      ev.preventDefault();
      check(inp.value).then(function (ok) {
        if (!ok) { er.textContent = 'Clave incorrecta'; inp.select(); return; }
        try { localStorage.setItem('mvk', H); } catch (e) {}
        g.remove(); d.classList.remove('mv-lock');
        window.dispatchEvent(new Event('resize'));
      });
    });
  }
  if (document.body) build(); else document.addEventListener('DOMContentLoaded', build);
})();
