#!/usr/bin/env python3
"""
audit-overflow.py — Auditor de overflow para e-books Bastidores da Sindicatura.

Roda Chromium headless sobre o HTML, mede cada .pg-body em modo print
(viewport A4 = 794×1123px) e reporta páginas cujo conteúdo escapa da área
segura. Use SEMPRE antes de gerar o PDF final.

Uso:
    python3 _skill/audit-overflow.py "Meu E-Book.html"

Saída:
    Pág NN | ok | extentBelow=0px
    Pág NN | ⚠️  OVERFLOW | extentBelow=39px (...)

Exit code 0 = limpo. Exit code 1 = pelo menos uma página com overflow.

Dependência única: playwright (pip install playwright; playwright install chromium).
"""
import asyncio
import sys
from pathlib import Path

from playwright.async_api import async_playwright


async def audit(html_path: str) -> int:
    src = Path(html_path).resolve()
    if not src.exists():
        print(f"Arquivo não encontrado: {src}")
        return 2

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ctx = await browser.new_context(viewport={"width": 794, "height": 1123})
        page = await ctx.new_page()
        await page.emulate_media(media="print")
        await page.goto(src.as_uri(), wait_until="networkidle")
        await page.evaluate("document.fonts.ready")

        results = await page.evaluate(
            """() => {
              const pages = document.querySelectorAll('.page');
              return Array.from(pages).map((pg, idx) => {
                const body = pg.querySelector('.pg-body');
                if (!body) return {idx: idx+1, type:'cover/manifesto', overflow:false};
                const bodyRect = body.getBoundingClientRect();
                let maxChildBottom = 0;
                for (const child of body.children) {
                  const r = child.getBoundingClientRect();
                  maxChildBottom = Math.max(maxChildBottom, r.bottom);
                }
                const extentBelow = Math.round(maxChildBottom - bodyRect.bottom);
                return {
                  idx: idx+1,
                  scrollH: body.scrollHeight,
                  clientH: body.clientHeight,
                  extentBelow,
                  hasOverflow: extentBelow > 1
                };
              });
            }"""
        )

        bad = 0
        for r in results:
            if r.get("type"):
                print(f"Pág {r['idx']:>2} | ok (capa/manifesto)")
                continue
            mark = "⚠️  OVERFLOW" if r["hasOverflow"] else "ok"
            if r["hasOverflow"]:
                bad += 1
            print(
                f"Pág {r['idx']:>2} | {mark} | "
                f"extentBelow={r['extentBelow']}px "
                f"(scroll={r['scrollH']}, client={r['clientH']})"
            )

        await browser.close()

        if bad == 0:
            print("\n✓ Nenhum overflow. Pode gerar o PDF.")
            return 0
        print(f"\n✗ {bad} página(s) com overflow. Reduza conteúdo antes de gerar PDF.")
        return 1


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(asyncio.run(audit(sys.argv[1])))


if __name__ == "__main__":
    main()
