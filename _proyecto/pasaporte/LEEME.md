# Pasaporte de viaje (librito A6)
Generador del "Pasaporte de viaje": una página por lugar (foto, años, texto, dato curioso, sellos, QR).
- Textos: los lugares con página toman la reseña y el dato curioso del sitio; los demás, de blurbs2.json.
- Sellos: 1ª visita redondo, 2ª rectangular, 3ª ovalado, color del viaje, inclinación aleatoria fija. Disney World (#2) usa el sello especial "WALT DISNEY WORLD" (uno por visita).
- Fechas de los sellos: dates.json, clave "NUMERO-AÑO" -> "DD MON YYYY" (o "JUN 2013"). Sin fecha => solo el año.
Uso (requiere playwright, segno, pypdf, Pillow):
  cd _proyecto/pasaporte && python3 build.py && python3 render.py && python3 impose.py
Salidas: librito-A6.pdf (páginas en orden) y librito-para-imprimir-A5.pdf (armado para doblar). Margen de lomo 16 mm.
