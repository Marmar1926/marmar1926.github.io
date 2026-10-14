from pypdf import PdfReader, PdfWriter, Transformation, PageObject
r=PdfReader('librito-A6.pdf'); P=r.pages; n=len(P); assert n%4==0
W=float(P[0].mediabox.width); H=float(P[0].mediabox.height)
w=PdfWriter()
for k in range(n//4):
    for l,rr in [(n-1-2*k,2*k),(2*k+1,n-2-2*k)]:
        s=PageObject.create_blank_page(width=2*W,height=H)
        s.merge_transformed_page(P[l],Transformation().translate(0,0))
        s.merge_transformed_page(P[rr],Transformation().translate(W,0))
        w.add_page(s)
w.write('librito-para-imprimir-A5.pdf'); print(len(w.pages))
