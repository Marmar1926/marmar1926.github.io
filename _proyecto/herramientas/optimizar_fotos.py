"""Genera versiones livianas para el carrusel (carpeta sm/) y achica las portadas.
Uso: python3 _proyecto/herramientas/optimizar_fotos.py   (desde la raiz del repo; es idempotente)
- sm/NN.jpg: lado mayor 1400 px (1800 para las fusionadas anchas *w.jpg), calidad 78.
- hero.jpg: si pesa mas de 260 KB se reduce a lado mayor 1400 px, calidad 80.
Las fotos originales (2200 px) quedan para la vista ampliada.
"""
import glob, os, re, sys
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
made = heroes = 0
for page in sorted(glob.glob(f'{ROOT}/*/*/index.html')):
    d = os.path.dirname(page)
    for f in sorted(glob.glob(f'{d}/*.jpg')):
        b = os.path.basename(f)
        if b == 'hero.jpg':
            im = Image.open(f)
            if os.path.getsize(f) > 260 * 1024 and max(im.size) > 1400:   # no recomprimir las ya achicadas
                im = im.convert('RGB'); im.thumbnail((1400, 1400), Image.LANCZOS)
                im.save(f, quality=80, optimize=True, progressive=True); heroes += 1
            continue
        if re.fullmatch(r'\d+[tn]\.jpg', b):   # fotos sueltas Then/Now: solo vista ampliada
            continue
        out = f'{d}/sm/{b}'
        if os.path.exists(out) and os.path.getmtime(out) >= os.path.getmtime(f):
            continue
        os.makedirs(f'{d}/sm', exist_ok=True)
        im = Image.open(f).convert('RGB')
        lim = 1800 if b.endswith('w.jpg') else 1400
        im.thumbnail((lim, lim), Image.LANCZOS)
        im.save(out, quality=78, optimize=True, progressive=True); made += 1
print('sm creadas:', made, '| portadas achicadas:', heroes)
