#!/usr/bin/env python3
"""
html-to-pdf.py — Conversor HTML→PDF para e-books Bastidores da Sindicatura.

Usa Chromium headless com viewport A4 exato (794×1123px) e mídia "print",
para que o CSS @media print do template seja aplicado corretamente.
Resultado: cada .page do HTML vira EXATAMENTE uma folha A4 do PDF.

Uso:
    python3 _skill/html-to-pdf.py "Meu E-Book.html"          # → "Meu E-Book.pdf"
    python3 _skill/html-to-pdf.py "Meu E-Book.html" "out.pdf"

RECOMENDADO: rode antes _skill/audit-overflow.py para garantir que o
conteúdo cabe nas margens. Se a auditoria reclamar, NÃO gere o PDF.
"""
import asyncio
import sys
from pathlib import Path

from playwright.async_api import async_playwright


async def convert(src: Path, dst: Path) -> None:
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ctx = await browser.new_context(viewport={"width": 794, "height": 1123})
        page = await ctx.new_page()
        await page.emulate_media(media="print")
        await page.goto(src.as_uri(), wait_until="networkidle")
        await page.evaluate("document.fonts.ready")
        await page.pdf(
            path=str(dst),
            format="A4",
            print_background=True,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
            prefer_css_page_size=True,
            scale=1,
        )
        await browser.close()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    src = Path(sys.argv[1]).resolve()
    if not src.exists():
        print(f"Arquivo não encontrado: {src}")
        sys.exit(2)
    dst = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else src.with_suffix(".pdf")
    asyncio.run(convert(src, dst))
    print(f"✓ PDF gerado: {dst}")


if __name__ == "__main__":
    main()
