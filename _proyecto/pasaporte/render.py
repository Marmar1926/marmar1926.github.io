import asyncio, sys, os
from playwright.async_api import async_playwright
from pypdf import PdfReader
S=os.path.dirname(os.path.abspath(__file__))
async def render(notes):
    h=open(f'{S}/librito.html',encoding='utf-8').read()
    lines=''.join('<div></div>' for _ in range(13))
    nb=''.join(f'<section class="notes"><h2>Notas de viaje</h2>{lines}</section>' for _ in range(notes))
    open(f'{S}/_r.html','w',encoding='utf-8').write(h.replace('NOTES',nb))
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page()
        await pg.goto('file://'+S+'/_r.html'); await pg.wait_for_timeout(500)
        await pg.pdf(path=f'{S}/librito-A6.pdf',prefer_css_page_size=True,print_background=True)
        await b.close()
    return len(PdfReader(f'{S}/librito-A6.pdf').pages)
n=asyncio.run(render(0)); k=(4-n%4)%4
if k: n=asyncio.run(render(k))
print('pages',n,'notes',k)
