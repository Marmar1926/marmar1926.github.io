"""Escala librito-A6.pdf a A5 (misma proporción) -> librito-A5.pdf"""
from pypdf import PdfReader, PdfWriter, Transformation
r=PdfReader('librito-A6.pdf'); w=PdfWriter(); A5=(148*72/25.4,210*72/25.4)
for p in r.pages:
    k=A5[0]/float(p.mediabox.width); p.add_transformation(Transformation().scale(k,k))
    p.mediabox.lower_left=(0,0); p.mediabox.upper_right=A5; p.cropbox=p.mediabox; w.add_page(p)
w.write('librito-A5.pdf'); print('A5', len(r.pages))
