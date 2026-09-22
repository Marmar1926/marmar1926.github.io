# Estado actual del proyecto (ver fecha del ultimo commit para saber que tan reciente es esto)

## Lugares con fotos reales y pagina completa
- #5 Disneyland (2013/yyzr6szr) - 11 fotos
- #6 San Diego (2013/7a2qpwvt) - 15 fotos (Coronado y La Jolla), numeradas 01..15 segun el numero original del usuario
- #8 Santa Monica (2013/fprphxqb) - 26 fotos en la pestaña 2013 con textos completos; pestañas 2018 y 2022 creadas pero vacias (pendiente de fotos)
- #17 Grand Canyon West Skywalk (2013/fef9ux73) - 17 fotos con textos (capas de roca roja cerca del Skywalk, Eagle Point, Guano Point, Skywalk, Hualapai Ranch); faltan 2 fotos que el usuario va a agregar mas adelante (reordenadas por contenido real, no coinciden 1 a 1 con la numeracion original del usuario: ver notas del chat)
- #16 Las Vegas (2013/95a7284c) - 11 fotos en la pestaña 2013 (Venetian, Paris, Wynn/Encore); pestaña 2018 creada pero vacia (pendiente de fotos)
- #9 Beverly Hills (2013/r4kmmtsn) - 12 fotos
- #10 Warner Bros. Studios (2013/5ubvwzzk) - 23 fotos (2013) + 19 fotos (2018), pestañas por anio
- #27 Mount Rushmore Memorial (2018/uye2hff3) - 10 fotos

## Resto de los 45 lugares
Todavia en placeholder ("en construccion"). Revisar manifest.json para la
lista completa con numero/nombre/codigo de carpeta.

## Lugares que van a necesitar la plantilla de "pestañas por año" cuando
lleguen sus fotos (visitados mas de una vez):
Las Vegas, San Francisco, Los Angeles, Santa Monica, Santa Barbara, Miami,
Disney World.

## Como agregar un lugar nuevo
1. Pedir las fotos por chat (no depender del boton "Add file" de GitHub,
   el usuario tuvo problemas con eso).
2. Buscar en manifest.json el numero/trip/slug/sub/color del lugar.
3. Procesar fotos: PIL.ImageOps.exif_transpose (importante, ya hubo bugs de
   fotos giradas), resize a ~2200px lado largo, quality ~87, nombrar 01.jpg,
   02.jpg, etc.
4. Armar index.html con la plantilla estandar (ver Rushmore o Beverly Hills
   como referencia de la version simple; Warner Bros. Studios para la
   version con pestañas de año).
5. Pedir un token de GitHub (personal access token, scope public_repo) si no
   se tiene uno vigente, clonar/pull el repo, copiar fotos + index.html a
   {trip}/{slug}/, commit, push. Borrar el token del entorno despues.
6. Actualizar este archivo (ESTADO.md) con el nuevo lugar completado.


## Fotos de portada (hero.jpg)
Las 45 carpetas ya tienen su hero.jpg guardado (la misma foto icónica que
se usó en el índice impreso), aunque el lugar todavía sea un placeholder.
Al armar la página real de un lugar nuevo, NO hace falta pedirle la foto de
portada al usuario — ya está en {trip}/{slug}/hero.jpg, lista para usar.

## Portadas en paginas placeholder (19/09)
Las 41 paginas "en construccion" ahora muestran su hero.jpg en la cabecera (mismo bloque .hero que las paginas completas). Portadas muy pesadas (Los Angeles, World of Coca-Cola, Yellowstone, Antelope Canyon, Monument Valley) se aligeraron a max 2200px. Al completar un lugar, la plantilla completa reemplaza a la placeholder y reutiliza el mismo hero.jpg.

## Fix cabecera en pantallas anchas (22/09)
Se corrigio el CSS .hero en las 45 paginas: antes usaba width:100% + max-height:65vh sin tope de ancho, y en pantallas de escritorio (anchas y no muy altas) el recorte se volvia extremo (relacion de aspecto disparada), mostrando la foto muy pegada/estirada. Ahora .hero tiene max-width:640px y margin:0 auto (igual que el resto del contenido), con max-height:min(65vh,720px). En movil no cambia nada.
Beverly Hills ademas tiene portada nueva (foto real 3840x2160 provista por el usuario), reemplazando la version de baja resolucion.
