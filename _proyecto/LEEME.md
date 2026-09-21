# Notas para retomar este proyecto en una conversacion nueva con Claude

Este repositorio es el sitio de paginas QR del mural fisico "Mis viajes por USA".

- `manifest.json`: tabla completa de los 45 lugares (numero de indice, nombre,
  viaje/anio, color, codigo de carpeta real, visitas repetidas). Es la fuente
  de verdad de todo el proyecto.
- Cada lugar vive en `/{viaje}/{codigo}/index.html` + sus fotos, segun el
  campo "trip" y "slug" de cada entrada del manifest.
- `/index.html` (raiz): indice maestro navegable (por anio y alfabetico).
- Lugares ya completos con fotos reales (no placeholder): revisar cuales
  carpetas tienen mas que un index.html generico de "en construccion".
- Plantilla estandar de cada pagina: portada sin texto superpuesto, ficha
  (nombre/ubicacion/año) debajo, recuadro de "dato curioso", reseña general,
  carrusel de fotos con lupa/zoom y leyenda opcional por foto, navegacion
  anterior/siguiente + acceso al indice, cierre "seguir explorando".
- Lugares con mas de una visita usan pestañas de año (ver Warner Bros. Studios
  como referencia) en vez de la plantilla simple.
- Privacidad: robots.txt + meta noindex en todas las paginas; URLs con codigo
  random en vez de nombre real del lugar (no revertir sin que el usuario lo
  pida).
