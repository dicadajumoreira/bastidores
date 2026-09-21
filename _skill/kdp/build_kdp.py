#!/usr/bin/env python3
"""
build_kdp.py — Gera os arquivos pra publicar os e-books na Amazon (KDP).

Pra cada volume listado em volumes.json, produz em Amazon/<pasta do volume>/:
  - VNN-<slug>.epub          manuscrito reflowável (formato recomendado pela KDP)
  - VNN-<slug>-capa.jpg      capa Kindle 1600x2560 (proporção 1,6:1)
  - VNN-<slug>-ficha-kdp.md  ficha com título, subtítulo, descrição, palavras-chave e categorias

Fontes: o HTML do e-book em Ebooks/ (mesmo template de todos os volumes). Os volumes
02 e 03 só existem em PDF, então o texto deles é extraído do PDF.

Uso:
    python3 _skill/kdp/build_kdp.py            # todos os volumes
    python3 _skill/kdp/build_kdp.py 22 05      # só alguns
    python3 _skill/kdp/build_kdp.py --debug-pdf 02   # imprime as linhas classificadas do PDF

Dependências: beautifulsoup4, lxml, pymupdf, pillow. Chromium pra capa (variável CHROME),
epubcheck opcional pra validar (variável EPUBCHECK apontando pro .jar).
"""
import argparse
import datetime
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import pymupdf
from bs4 import BeautifulSoup, Comment, NavigableString, Tag
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
ASSETS = HERE / "assets"
OUT = ROOT / "Amazon"
CHROME = os.environ.get("CHROME", "/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
EPUBCHECK = os.environ.get("EPUBCHECK", "")

# ---------------------------------------------------------------------------
# Vocabulário do template dos e-books → elementos do EPUB
# ---------------------------------------------------------------------------
SKIP_TAGS = {"script", "style", "svg", "button", "link", "meta", "img", "path", "head", "title", "input", "form", "nav"}
SKIP_CLS = {
    "pg-head", "pg-foot", "pg-num", "brand", "dot", "mark", "logo", "pdf-hint", "pdf-fab", "hr-orn", "glyph",
    "section-num", "big", "dots", "toc-list", "toc-item", "cover-edition", "yr", "barra80", "rail", "fill",
    "marker", "legend", "dot-accent", "cover-brand", "cover-meta", "cover-stats", "cover-bottom", "cover-top",
}
H3_CLS = {"h-sub"}
H4_CLS = {"ttl", "titulo", "name", "gt", "ft"}
KICKER_CLS = {"section-kicker", "kicker", "cover-eyebrow", "invite-head", "k", "ep", "bloco-head", "mod-head", "hdr", "header", "tema"}
LABEL_CLS = {"lbl", "tag", "tag-status", "status", "sit", "range", "fnum", "gn", "role", "when", "label", "num", "grupo", "risco", "u"}
LEDE_CLS = {"section-lede", "lede", "cover-deck", "cover-title", "opener-lede"}
QUOTE_CLS = {"fquote", "phrase", "punch", "q", "word", "lines", "refrain-text"}
BIG_CLS = {"t", "n", "val"}
SMALL_CLS = {"l", "fwhy", "base", "gd", "gh", "hours"}
SIGN_CLS = {"signature", "sig"}
PREFIX = {"fwhy": "<b>Por que funciona:</b> ", "acao": "<b>Ação:</b> ", "base": "<b>Base legal:</b> "}
LIST_PREFIX = {"ynot": "✓ ", "xnot": "✗ "}
# ordem importa: a primeira classe encontrada define a variante da caixa
BOX_VARIANTS = [
    ("callout", "callout"), ("survival", "summary"), ("quote-block", "quote"), ("refrain", "quote"),
    ("good", "good"), ("ok", "good"), ("bad", "bad"), ("lie", "bad"),
    ("model", "model"), ("modelo", "model"), ("clausula", "model"), ("tool", "model"), ("chair", "model"),
    ("note", "note"), ("selection-band", "band"), ("cta-band", "band"),
    ("block-card", "card"), ("norma", "card"), ("reply-card", "card"), ("confusao", "card"), ("tier", "card"),
    ("box", "card"), ("mito-card", "card"), ("grade-card", "card"), ("inv-card", "card"), ("story", "card"),
    ("persona", "card"), ("frase", "card"), ("cell", "card"), ("item", "card"), ("step", "card"), ("etapa", "card"),
    ("sinal", "card"), ("pillar", "card"), ("phrase", "quote"), ("nota-row", "card"), ("msg-row", "card"),
    ("quad", "card"), ("action", "card"), ("horizon", "card"), ("trilha", "card"), ("ator", "card"), ("comm", "card"),
    ("feature", "card"), ("bio", "card"), ("mito", "card"), ("fluxo", "card"), ("aberto", "card"), ("reply", "card"),
    ("lead", "card"), ("q1", "card"), ("q2", "card"), ("q3", "card"), ("q4", "card"), ("mini", "card"),
]
BOX_LABELS = {"model": "Modelo", "modelo": "Modelo", "tool": "Ferramenta", "chair": "Ferramenta", "clausula": "Cláusula"}
BLOCK_TAGS = {
    "div", "p", "section", "article", "ul", "ol", "li", "table", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote",
    "header", "footer", "figure", "figcaption", "tr", "td", "th", "thead", "tbody", "main", "aside", "dl", "dt", "dd",
}
EMPTY_TEXT = {"", "·", "§", "★", "→", "▸", "•", "-", "–", "—", "\"", "!", "\u201c", "\u201d", "\u2018", "\u2019"}


def esc(s):
    return html.escape(s, quote=False).replace("\xa0", " ")


def collapse(s):
    return re.sub(r"\s+", " ", s)


def classes(el):
    return set(el.get("class", [])) if isinstance(el, Tag) else set()


def style_of(el):
    return (el.get("style") or "").replace(" ", "").lower() if isinstance(el, Tag) else ""


def is_block(node):
    if not isinstance(node, Tag):
        return False
    if node.name in BLOCK_TAGS:
        return True
    if node.name == "span":
        c = classes(node)
        if c & LABEL_CLS or c & KICKER_CLS or c & H4_CLS or "display:block" in style_of(node):
            return True
    return False


def inline(node):
    """Renderiza conteúdo inline (texto, negrito, itálico, links) como XHTML."""
    if isinstance(node, Comment):
        return ""
    if isinstance(node, NavigableString):
        return esc(collapse(str(node)))
    if not isinstance(node, Tag):
        return ""
    if node.name in SKIP_TAGS:
        return ""
    c = classes(node)
    if c & SKIP_CLS:
        return ""
    if node.name == "span" and "box" in c:
        return ""
    inner = "".join(inline(ch) for ch in node.children)
    if node.name == "br":
        return "<br/>"
    if node.name in ("b", "strong"):
        return f"<b>{inner}</b>" if inner.strip() else inner
    if node.name in ("i", "em"):
        return f"<em>{inner}</em>" if inner.strip() else inner
    if node.name in ("sup", "sub", "u"):
        return f"<{node.name}>{inner}</{node.name}>" if inner.strip() else inner
    if node.name == "a":
        href = node.get("href", "")
        if href.startswith("http"):
            return f'<a href="{html.escape(href, quote=True)}">{inner}</a>'
        return inner
    if node.name == "span":
        if c & {"it", "serif"} or "font-style:italic" in style_of(node):
            return f"<em>{inner}</em>" if inner.strip() else inner
        if c & {"high", "b", "crit", "moeda", "x12"}:
            return f"<b>{inner}</b>" if inner.strip() else inner
        if c & LABEL_CLS:
            return f'<span class="tagchip">{inner}</span> ' if inner.strip() else inner
        return inner
    # tag de bloco dentro de contexto inline: só o texto
    return " " + inner + " "


def inline_children(el):
    return tidy(" ".join(inline(ch) for ch in el.children))


def tidy(s):
    s = collapse(s)
    s = re.sub(r"\s+([,.;:!?)])", r"\1", s)
    s = re.sub(r"\(\s+", "(", s)
    s = re.sub(r"\s+(</(?:b|em|a|sup|sub|u)>)", r"\1", s)
    s = re.sub(r"(<(?:b|em|a[^>]*|sup|sub|u)>)\s+", r"\1", s)
    s = s.replace("<br/> ", "<br/>").replace(" <br/>", "<br/>")
    return s.strip()


def para(el, tag="p", cls=None, prefix=""):
    txt = inline_children(el)
    if strip_tags(txt) in EMPTY_TEXT:
        return []
    attr = f' class="{cls}"' if cls else ""
    return [f"<{tag}{attr}>{prefix}{txt}</{tag}>"]


def strip_tags(s):
    return collapse(re.sub(r"<[^>]+>", " ", s)).strip()


def render_list(el):
    tag = "ol" if el.name == "ol" else "ul"
    c = classes(el)
    cls = ""
    if "checks" in c:
        cls = ' class="checks"'
    elif "enum" in c:
        cls = ' class="enum"'
    elif "ynot" in c:
        cls = ' class="yes"'
    elif "xnot" in c:
        cls = ' class="no"'
    prefix = ""
    for k, v in LIST_PREFIX.items():
        if k in c:
            prefix = v
    items = []
    for li in el.find_all("li", recursive=False):
        run, nested = [], []
        for ch in li.children:
            if isinstance(ch, Tag) and ch.name in ("ul", "ol"):
                nested.append(render_list(ch))
            elif is_block(ch):
                nested.extend(convert_block(ch))
            else:
                run.append(inline(ch))
        txt = tidy("".join(run))
        if strip_tags(txt) in EMPTY_TEXT and not nested:
            continue
        items.append(f"<li>{prefix}{txt}{''.join(nested)}</li>")
    if not items:
        return ""
    return f"<{tag}{cls}>{''.join(items)}</{tag}>"


def render_table(el):
    rows = []
    for tr in el.find_all("tr"):
        cells = []
        for td in tr.find_all(["td", "th"], recursive=False):
            tag = td.name
            cells.append(f"<{tag}>{inline_children(td)}</{tag}>")
        if cells:
            rows.append("<tr>" + "".join(cells) + "</tr>")
    return f"<table>{''.join(rows)}</table>" if rows else ""


def box_variant(c):
    for key, variant in BOX_VARIANTS:
        if key in c:
            return key, variant
    return None, None


def convert_block(el):
    """Converte um elemento de bloco do template em uma lista de blocos XHTML."""
    if not isinstance(el, Tag):
        return []
    if el.name in SKIP_TAGS:
        return []
    c = classes(el)
    if c & SKIP_CLS:
        return []
    name = el.name
    if name in ("h1", "h2", "h3", "h4", "h5", "h6"):
        lvl = {"h1": 2, "h2": 2, "h3": 3, "h4": 4, "h5": 4, "h6": 4}[name]
        return para(el, f"h{lvl}")
    if "tags" in c:
        parts = [tidy("".join(inline(x) for x in ch.children)) for ch in el.children if isinstance(ch, Tag)]
        parts = [x for x in parts if strip_tags(x)]
        return [f'<p class="tags">{" · ".join(parts)}</p>'] if parts else []
    leaf = not any(is_block(ch) for ch in el.children)
    if c & H3_CLS and leaf:
        return para(el, "h3")
    if c & H4_CLS and leaf:
        return para(el, "h4")
    if c & KICKER_CLS and leaf:
        return para(el, "p", "kicker")
    if c & LABEL_CLS and leaf:
        return para(el, "p", "label")
    if c & SIGN_CLS and leaf:
        return para(el, "p", "signature")
    if c & LEDE_CLS and leaf:
        return para(el, "p", "lede")
    if c & QUOTE_CLS and leaf:
        return para(el, "p", "quote")
    if name in ("ul", "ol"):
        r = render_list(el)
        return [r] if r else []
    if name == "table":
        r = render_table(el)
        return [r] if r else []
    if name == "p" or (name == "span" and is_block(el)) or name in ("dt", "dd", "figcaption"):
        for k, pre in PREFIX.items():
            if k in c:
                return para(el, "p", "small" if k in SMALL_CLS else None, pre)
        cls = None
        if c & BIG_CLS:
            cls = "big"
        elif c & SMALL_CLS:
            cls = "small"
        elif "tags" in c:
            cls = "tags"
        return para(el, "p", cls)
    # contêiner genérico (div, section, li solto etc.)
    key, variant = box_variant(c)
    if c & BIG_CLS and not any(is_block(ch) for ch in el.children):
        return para(el, "p", "big")
    if c & SMALL_CLS and not any(is_block(ch) for ch in el.children):
        return para(el, "p", "small")
    if "tags" in c and not any(is_block(ch) for ch in el.children):
        return para(el, "p", "tags")
    for k, pre in PREFIX.items():
        if k in c and not any(is_block(ch) for ch in el.children):
            return para(el, "p", "small" if k in SMALL_CLS else None, pre)
    out, run = [], []

    def flush():
        txt = tidy("".join(run))
        run.clear()
        if strip_tags(txt) not in EMPTY_TEXT:
            out.append(f"<p>{txt}</p>")

    for ch in el.children:
        if is_block(ch):
            flush()
            out.extend(convert_block(ch))
        else:
            run.append(inline(ch))
    flush()
    if variant and out:
        label = BOX_LABELS.get(key)
        if key == "model" and el.get("data-label"):
            label = el.get("data-label")
        pre = f'<p class="label">{esc(label)}</p>' if label else ""
        return [f'<div class="box {variant}">{pre}{"".join(out)}</div>']
    return out


def html_to_blocks(path):
    """Lê o HTML do e-book e devolve (capa, blocos) com os blocos já em XHTML."""
    soup = BeautifulSoup(Path(path).read_text(encoding="utf-8"), "lxml")
    pages = [pg for pg in soup.select("section.page") if not pg.find_parent("section", class_="page")]
    cover = pages[0]
    blocks = []
    for pg in pages[1:]:
        if pg.select_one(".toc-list"):
            continue
        blocks.extend(convert_block(pg))
    cover_info = cover_from_html(cover)
    return cover_info, blocks


def cover_from_html(cover):
    def txt(sel):
        e = cover.select_one(sel)
        return inline_children(e) if e else ""

    h1 = cover.find("h1")
    labels = [collapse(x.get_text(" ", strip=True)) for x in cover.select(".cover-meta .label")]
    stats = []
    for s in cover.select(".cover-stats .s"):
        n = collapse(s.select_one(".n").get_text(" ", strip=True)) if s.select_one(".n") else ""
        l = collapse(s.select_one(".l").get_text(" ", strip=True)) if s.select_one(".l") else ""
        stats.append([n, l])
    return {
        "eyebrow": strip_tags(txt(".cover-eyebrow")),
        "titulo_html": inline_children(h1) if h1 else "",
        "subtitulo_html": txt("p.cover-title"),
        "deck": strip_tags(txt("p.cover-deck")),
        "label": labels[0] if labels else "",
        "stats": stats,
    }


# ---------------------------------------------------------------------------
# Volumes que só existem em PDF (02 e 03)
# ---------------------------------------------------------------------------
ACCENT, GOLD, MUTED = 0xB8543B, 0x8C6A2A, 0x6A7385


def pdf_lines(page):
    """Extrai as linhas da página como listas de caracteres (sem os espaços do
    PDF, que o letter-spacing do template embaralha). A quebra de palavra é
    decidida depois, pelo vão entre glifos."""
    raw = page.get_text("rawdict")
    lines = []
    for b in raw["blocks"]:
        if b.get("type") != 0:
            continue
        for l in b["lines"]:
            chars = []
            for s in l["spans"]:
                for c in s["chars"]:
                    if not c["c"].strip():
                        continue
                    chars.append({"c": c["c"], "x0": c["bbox"][0], "x1": c["bbox"][2], "size": s["size"], "font": s["font"], "color": s["color"]})
            if not chars:
                continue
            key = max(set((c["size"], c["font"], c["color"]) for c in chars), key=lambda k: sum(1 for c in chars if (c["size"], c["font"], c["color"]) == k))
            size, font, color = key
            gaps = [chars[i]["x0"] - chars[i - 1]["x1"] for i in range(1, len(chars))]
            base = sorted(gaps)[len(gaps) // 4] if gaps else 0
            thr = max(base, 0) + 0.14 * size
            words = []  # lista de [texto, bold, ital, color, espaço antes]
            cur = None
            for i, c in enumerate(chars):
                bold, ital = "Bold" in c["font"], ("Ital" in c["font"] or "Oblique" in c["font"])
                style = (bold, ital, c["color"])
                brk = i > 0 and gaps[i - 1] > thr
                if cur is None or tuple(cur[1:4]) != style:
                    cur = [c["c"], *style, brk]
                    words.append(cur)
                else:
                    cur[0] += (" " if brk else "") + c["c"]
            text = collapse("".join((" " if w[4] else "") + w[0] for w in words)).strip()
            lines.append({"words": words, "text": text, "size": size, "font": font, "color": color,
                          "y0": l["bbox"][1], "y1": l["bbox"][3], "x0": chars[0]["x0"], "x1": chars[-1]["x1"]})
    return lines


def line_html(ln, kind):
    parts = []
    for text, bold, ital, color, lead in ln["words"]:
        t = esc(text)
        if kind in ("kicker", "label"):
            parts.append(t)
        elif kind in ("h2", "h3", "h4"):
            parts.append(f"<em>{t}</em>" if ital and color == ACCENT else t)
        else:
            if bold and ital:
                t = f"<b><em>{t}</em></b>"
            elif bold:
                t = f"<b>{t}</b>"
            elif ital:
                t = f"<em>{t}</em>"
            parts.append(t)
        if lead:
            parts.insert(len(parts) - 1, " ")
    s = "".join(parts)
    s = s.replace("</b><b>", "").replace("</em><em>", "")
    s = re.sub(r"</b>( +)<b>", r"\1", s)
    s = re.sub(r"</em>( +)<em>", r"\1", s)
    return tidy(s)


def classify(ln):
    size, font, color, text = ln["size"], ln["font"], ln["color"], ln["text"]
    serif = "Serif" in font
    bold = "Bold" in font
    ital = "Ital" in font
    letters = re.sub(r"[^A-Za-zÀ-ÿ]", "", text)
    if text in EMPTY_TEXT or (size >= 30 and re.fullmatch(r"[0-9·]+", text)):
        return "skip"
    if "LiberationSans" in font or text.startswith("Fig.") or (serif and size < 8):
        return "skip"  # texto de diagrama SVG e legenda de figura (a figura não vai pro EPUB)
    if size >= 26:
        return "h2"
    if re.fullmatch(r"[0-9·]+", text) and size >= 11.5:
        return "skip"
    if serif and not bold and 18 <= size < 26:
        return "h3"
    if bold and size <= 9.6 and letters and letters.isupper():
        return "label" if color == GOLD else "kicker"
    if serif and size <= 9.5 and color == MUTED and letters and letters.isupper():
        return "signature"
    if serif and 11.5 <= size < 26 and ital:
        return "quote"
    if serif and 11.5 <= size < 26 and len(text.split()) <= 5 and not text.endswith("."):
        return "h4"
    if serif and 11.5 <= size < 26:
        return "lede"
    if size < 8:
        return "skip"
    return "body"


def bullet_rects(page):
    out = []
    for d in page.get_drawings():
        r = d["rect"]
        if 3 <= r.width <= 13 and 3 <= r.height <= 13 and r.y0 > 48:
            out.append(r)
    return out


def has_bullet(ln, rects):
    for r in rects:
        if ln["x0"] - 16 <= r.x1 <= ln["x0"] + 1 and r.y0 < ln["y1"] and r.y1 > ln["y0"]:
            return True
    return False


def figure_at(page, lines, cap, prefix, n, images):
    """Recorta o diagrama que fica logo acima da legenda "Fig. NN" e devolve o
    bloco XHTML com a imagem. O diagrama é desenho vetorial no PDF; no EPUB ele
    vira PNG."""
    x0, x1 = cap["x0"] - 40, cap["x1"] + 40
    top = cap["y0"] - 270
    rect = None
    for d in page.get_drawings():
        r = d["rect"]
        cx = (r.x0 + r.x1) / 2
        if r.y1 <= cap["y0"] + 2 and r.y0 >= top and x0 <= cx <= x1 and r.width < 260:
            rect = r if rect is None else rect | r
    for ln in lines:
        if ln["y1"] <= cap["y0"] + 2 and ln["y0"] >= top and x0 <= (ln["x0"] + ln["x1"]) / 2 <= x1 and ("LiberationSans" in ln["font"] or ln["size"] < 8):
            r = pymupdf.Rect(ln["x0"], ln["y0"], ln["x1"], ln["y1"])
            rect = r if rect is None else rect | r
    if rect is None or rect.width < 40 or rect.height < 40:
        return None
    clip = pymupdf.Rect(rect.x0 - 8, rect.y0 - 8, rect.x1 + 8, rect.y1 + 6) & page.rect
    pix = page.get_pixmap(dpi=220, clip=clip)
    name = f"images/{prefix}-fig{n:02d}.png"
    images[name] = pix.tobytes("png")
    txt = re.sub(r"^Fig\.\s*\d+\s*", "", cap["text"]).strip()
    title = txt[:1].upper() + txt[1:].lower()
    return f'<div class="fig"><img src="../{name}" alt="{esc(title)}"/><p class="small">Figura · {esc(title)}</p></div>'


def pdf_to_blocks(path, debug=False, prefix="fig", images=None):
    doc = pymupdf.open(path)
    blocks = []
    images = images if images is not None else {}
    nfig = 0
    for pno in range(1, len(doc)):
        page = doc[pno]
        H = page.rect.height
        lines = pdf_lines(page)
        head = [ln["text"].replace(" ", "").upper() for ln in lines if ln["y0"] < 48]
        if any("SUMÁRIO" in h or "SUMARIO" in h for h in head):
            continue
        lines = [ln for ln in lines if ln["y0"] >= 48 and ln["y1"] <= H - 36]
        rects = bullet_rects(page)
        para, para_kind, prev = [], None, None
        list_items = []

        def flush():
            nonlocal para, para_kind
            if para:
                txt = tidy(" ".join(para))
                txt = re.sub(r"</b>( +)<b>", r"\1", txt)
                txt = re.sub(r"</em>( +)<em>", r"\1", txt)
                if para_kind in ("h2", "h3", "h4"):
                    blocks.append(f"<{para_kind}>{txt}</{para_kind}>")
                elif para_kind in ("kicker", "label", "quote", "lede", "signature"):
                    blocks.append(f'<p class="{para_kind}">{txt}</p>')
                elif para_kind == "li":
                    list_items.append(f"<li>{txt}</li>")
                else:
                    blocks.append(f"<p>{txt}</p>")
            para, para_kind = [], None

        def flush_list():
            if list_items:
                blocks.append("<ul>" + "".join(list_items) + "</ul>")
                list_items.clear()

        last_fig_y = -100
        for ln in lines:
            kind = classify(ln)
            size = ln["size"]
            if ln["text"].startswith("Fig."):
                last_fig_y = ln["y0"]
                cont = [l2["text"] for l2 in lines if l2 is not ln and 0 <= l2["y0"] - ln["y0"] < 30 and abs(l2["x0"] - ln["x0"]) < 120 and classify(l2) == "kicker"]
                cap = dict(ln, text=(ln["text"] + " " + " ".join(cont)).strip())
                nfig += 1
                fig = figure_at(page, lines, cap, prefix, nfig, images)
                if fig:
                    flush()
                    flush_list()
                    prev = None
                    blocks.append(fig)
            if kind == "kicker" and 0 <= ln["y0"] - last_fig_y < 30:
                kind = "skip"  # continuação da legenda da figura
            bullet = False
            if kind == "body":
                m = re.match(r"^([•▸→✓☐\-–]|\d{1,2}\.)\s+", ln["text"])
                if m:
                    bullet = True
                    ln["words"][0][0] = ln["words"][0][0][m.end():].lstrip() if len(ln["words"][0][0]) >= m.end() else ""
                    ln["text"] = ln["text"][m.end():]
                elif has_bullet(ln, rects):
                    bullet = True
            if debug:
                print(f"p{pno + 1:02d} y{ln['y0']:6.1f} x{ln['x0']:5.1f} {kind:6}{'*' if bullet else ' '} {size:5.1f} {ln['font'][:18]:18} | {ln['text'][:80]}")
            if kind == "skip":
                continue
            gap = ln["y0"] - prev["y1"] if prev else 0
            if bullet:
                kind = "li"
            elif kind == "body" and para_kind == "li" and 0 <= gap <= 0.8 * size and abs(ln["x0"] - prev["x0"]) < 2:
                kind = "li"  # continuação do item
            limit = 1.3 * size if kind in ("h2", "h3") else 0.8 * size
            new_para = prev is None or kind != para_kind or bullet or gap > limit or gap < -0.5 * size
            if new_para:
                flush()
                if kind != "li":
                    flush_list()
                para_kind = kind
            para.append(line_html(ln, kind))
            prev = ln
        flush()
        flush_list()
    return blocks


# ---------------------------------------------------------------------------
# Capítulos
# ---------------------------------------------------------------------------
def split_chapters(blocks):
    """Divide a sequência de blocos em capítulos, um por h2. O kicker que vem
    logo antes do h2 acompanha o capítulo novo."""
    chapters = []
    cur_title, cur = None, []
    for b in blocks:
        if b.startswith("<h2"):
            carried = []
            if cur and cur[-1].startswith('<p class="kicker"'):
                carried = [cur.pop()]
            if cur_title is not None or cur:
                chapters.append((cur_title or "Início", cur))
            cur_title = strip_tags(b).strip()
            cur = carried + [b]
        else:
            cur.append(b)
    if cur_title is not None or cur:
        chapters.append((cur_title or "Início", cur))
    # remove capítulos vazios
    return [(t, bl) for t, bl in chapters if any(strip_tags(x) for x in bl)]


def nav_title(t):
    t = t.strip()
    if t.endswith(".") and not t.endswith(".."):
        t = t[:-1]
    return t


# ---------------------------------------------------------------------------
# EPUB
# ---------------------------------------------------------------------------
XHTML_HEAD = (
    '<?xml version="1.0" encoding="utf-8"?>\n'
    "<!DOCTYPE html>\n"
    '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="pt-BR" lang="pt-BR">\n'
    "<head>\n<meta charset=\"utf-8\"/>\n<title>{title}</title>\n"
    '<link rel="stylesheet" type="text/css" href="../css/style.css"/>\n</head>\n<body{body_attr}>\n'
)
XHTML_FOOT = "\n</body>\n</html>\n"


def xhtml(title, body, epub_type=None):
    attr = f' epub:type="{epub_type}"' if epub_type else ""
    doc = XHTML_HEAD.format(title=esc(title), body_attr=attr) + body + XHTML_FOOT
    ET.fromstring(doc.encode("utf-8"))  # garante XML bem formado
    return doc


def titlepage(meta, vol, cover):
    sub = cover.get("subtitulo_html") or esc(vol["subtitulo"])
    return xhtml(
        vol["titulo"],
        '<section class="titlepage" epub:type="titlepage">\n'
        f'<p class="brand">Bastidores da Sindicatura</p>\n'
        f'<p class="por">por {esc(meta["autora"])}</p>\n'
        f'<p class="vol">Volume {vol["num"]}</p>\n'
        f'<h1>{cover["titulo_html"] or esc(vol["titulo"])}</h1>\n'
        f'<p class="sub">{sub}</p>\n'
        f'<p class="autora">{esc(meta["autora"])}</p>\n'
        f'<p class="site">{esc(meta["site"])}</p>\n'
        "</section>",
        "frontmatter",
    )


def copyright_page(meta, vol):
    ano = meta["ano"]
    return xhtml(
        "Créditos",
        '<section class="copyright" epub:type="copyright-page">\n'
        f'<p><b>{esc(vol["titulo"])}</b><br/>{esc(vol["subtitulo"])}</p>\n'
        f'<p>Bastidores da Sindicatura · Volume {vol["num"]}<br/>Autora: {esc(meta["autora"])}</p>\n'
        f"<p>© {ano} {esc(meta['autora'])}. Todos os direitos reservados.</p>\n"
        f"<p>1ª edição digital · {ano}</p>\n"
        "<p>Nenhuma parte desta obra pode ser reproduzida, armazenada ou transmitida por qualquer meio, "
        "eletrônico ou mecânico, sem autorização prévia e por escrito da autora, exceto citações breves com "
        "indicação da fonte.</p>\n"
        "<p>Este livro tem caráter informativo e educacional. Ele não substitui a orientação jurídica, contábil, "
        "técnica ou de engenharia específica para cada condomínio. Leis, normas e entendimentos mudam: confira "
        "sempre a versão vigente antes de decidir.</p>\n"
        f'<p>{esc(meta["site"])}</p>\n'
        "</section>",
        "frontmatter",
    )


def toc_page(chapters, files):
    items = "".join(f'<li><a href="{f}">{esc(nav_title(t))}</a></li>\n' for (t, _), f in zip(chapters, files))
    items += '<li><a href="autora.xhtml">Sobre a autora</a></li>\n'
    return xhtml("Sumário", '<section class="toc" epub:type="toc">\n<h2>Sumário</h2>\n<ol>\n' + items + "</ol>\n</section>", "frontmatter")


def author_page(meta):
    return xhtml(
        "Sobre a autora",
        '<section epub:type="backmatter">\n'
        '<p class="kicker">Bastidores da Sindicatura</p>\n'
        "<h2>Sobre a <em>autora</em>.</h2>\n"
        '<p class="lede">Juliana Moreira tem trinta anos dentro do mercado imobiliário e condominial.</p>\n'
        "<p>É CEO da Sindicompany e da Condo Academy, professora de gestão condominial no IBMEC, formada em "
        "Finanças pela USP e perita judicial.</p>\n"
        "<p>Começou cedo. Aos quinze, acompanhando obra com o pai na construtora da família. Aos vinte, montou um "
        "<em>family office</em> que a empurrou para o mundo da administração condominial e da sindicatura "
        "profissional.</p>\n"
        "<p>Hoje toca a Sindicompany ao lado de mais de noventa pessoas, entre backoffice e síndicos "
        "profissionais, cuidando de mais de trezentos condomínios. A Condo Academy nasceu por necessidade: para "
        "manter padrão alto quando a operação cresce, alguém precisa formar gente. Hoje ela atende o ecossistema "
        "condominial inteiro.</p>\n"
        "<p>Bastidores da Sindicatura é o projeto editorial em que ela conta o que acontece por trás das decisões "
        "de um condomínio: os bastidores que ninguém mostra, as conversas que ninguém grava e as decisões que "
        "protegem o mandato do síndico.</p>\n"
        '<p class="label">Outros volumes da série e a Mentoria Bastidores da Sindicatura</p>\n'
        f'<p><a href="https://www.{esc(meta["site"])}/">www.{esc(meta["site"])}</a></p>\n'
        "</section>",
        "backmatter",
    )


def build_epub(meta, vol, cover, chapters, out_path, images=None):
    images = images or {}
    uid = "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_URL, f"https://{meta['site']}/kdp/V{vol['num']}"))
    now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    ch_files = [f"ch{idx:03d}.xhtml" for idx in range(1, len(chapters) + 1)]
    docs = {
        "text/titlepage.xhtml": titlepage(meta, vol, cover),
        "text/copyright.xhtml": copyright_page(meta, vol),
        "text/toc.xhtml": toc_page(chapters, ch_files),
        "text/autora.xhtml": author_page(meta),
    }
    for (title, blocks), f in zip(chapters, ch_files):
        body = '<section epub:type="chapter">\n' + "\n".join(blocks) + "\n</section>"
        docs["text/" + f] = xhtml(nav_title(title), body)

    nav_items = "".join(f'<li><a href="text/{f}">{esc(nav_title(t))}</a></li>\n' for (t, _), f in zip(chapters, ch_files))
    nav = (
        '<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE html>\n'
        '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="pt-BR" lang="pt-BR">\n'
        '<head><meta charset="utf-8"/><title>Sumário</title><link rel="stylesheet" type="text/css" href="css/style.css"/></head>\n'
        '<body>\n<nav epub:type="toc" id="toc"><h2>Sumário</h2>\n<ol>\n'
        '<li><a href="text/titlepage.xhtml">Folha de rosto</a></li>\n'
        '<li><a href="text/copyright.xhtml">Créditos</a></li>\n'
        '<li><a href="text/toc.xhtml">Sumário</a></li>\n'
        + nav_items
        + '<li><a href="text/autora.xhtml">Sobre a autora</a></li>\n'
        "</ol>\n</nav>\n"
        '<nav epub:type="landmarks" hidden="hidden"><h2>Guia</h2>\n<ol>\n'
        '<li><a epub:type="titlepage" href="text/titlepage.xhtml">Folha de rosto</a></li>\n'
        '<li><a epub:type="toc" href="text/toc.xhtml">Sumário</a></li>\n'
        f'<li><a epub:type="bodymatter" href="text/{ch_files[0]}">Início da leitura</a></li>\n'
        "</ol>\n</nav>\n</body>\n</html>\n"
    )
    ET.fromstring(nav.encode("utf-8"))

    ncx_points = ""
    order = 1
    for label, src in [("Folha de rosto", "text/titlepage.xhtml"), ("Créditos", "text/copyright.xhtml"), ("Sumário", "text/toc.xhtml")]:
        ncx_points += f'<navPoint id="np{order}" playOrder="{order}"><navLabel><text>{esc(label)}</text></navLabel><content src="{src}"/></navPoint>\n'
        order += 1
    for (t, _), f in zip(chapters, ch_files):
        ncx_points += f'<navPoint id="np{order}" playOrder="{order}"><navLabel><text>{esc(nav_title(t))}</text></navLabel><content src="text/{f}"/></navPoint>\n'
        order += 1
    ncx_points += f'<navPoint id="np{order}" playOrder="{order}"><navLabel><text>Sobre a autora</text></navLabel><content src="text/autora.xhtml"/></navPoint>\n'
    ncx = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1" xml:lang="pt-BR">\n'
        f'<head><meta name="dtb:uid" content="{uid}"/><meta name="dtb:depth" content="1"/>'
        '<meta name="dtb:totalPageCount" content="0"/><meta name="dtb:maxPageNumber" content="0"/></head>\n'
        f"<docTitle><text>{esc(vol['titulo'])}</text></docTitle>\n<navMap>\n{ncx_points}</navMap>\n</ncx>\n"
    )

    fonts = sorted((ASSETS / "fonts").glob("*.ttf"))
    fonts = [f for f in fonts if "SemiBold" not in f.name]
    manifest = [
        '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
        '<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>',
        '<item id="css" href="css/style.css" media-type="text/css"/>',
    ]
    for f in fonts:
        manifest.append(f'<item id="font-{f.stem.lower()}" href="fonts/{f.name}" media-type="font/ttf"/>')
    for i, name in enumerate(images):
        manifest.append(f'<item id="img{i}" href="{name}" media-type="image/png"/>')
    spine = []
    for i, (p, _) in enumerate(docs.items()):
        iid = f"doc{i}"
        manifest.append(f'<item id="{iid}" href="{p}" media-type="application/xhtml+xml"/>')
    order_paths = ["text/titlepage.xhtml", "text/copyright.xhtml", "text/toc.xhtml"] + ["text/" + f for f in ch_files] + ["text/autora.xhtml"]
    ids = {p: f"doc{i}" for i, p in enumerate(docs.keys())}
    for p in order_paths:
        spine.append(f'<itemref idref="{ids[p]}"/>')
    desc = "\n\n".join(vol["descricao"])
    opf = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid" xml:lang="pt-BR">\n'
        '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">\n'
        f'<dc:identifier id="uid">{uid}</dc:identifier>\n'
        f'<dc:title id="title">{esc(vol["titulo"])}</dc:title>\n'
        '<meta refines="#title" property="title-type">main</meta>\n'
        f'<dc:title id="subtitle">{esc(vol["subtitulo"])}</dc:title>\n'
        '<meta refines="#subtitle" property="title-type">subtitle</meta>\n'
        f'<dc:creator id="creator">{esc(meta["autora"])}</dc:creator>\n'
        '<meta refines="#creator" property="role" scheme="marc:relators">aut</meta>\n'
        '<meta refines="#creator" property="file-as">Moreira, Juliana</meta>\n'
        "<dc:language>pt-BR</dc:language>\n"
        f'<dc:publisher>{esc(meta["serie"])}</dc:publisher>\n'
        f'<dc:date>{meta["ano"]}-01-01</dc:date>\n'
        f"<dc:description>{esc(desc)}</dc:description>\n"
        f'<meta property="dcterms:modified">{now}</meta>\n'
        f'<meta property="belongs-to-collection" id="serie">{esc(meta["serie"])}</meta>\n'
        '<meta refines="#serie" property="collection-type">series</meta>\n'
        f'<meta refines="#serie" property="group-position">{int(vol["num"])}</meta>\n'
        "</metadata>\n<manifest>\n" + "\n".join(manifest) + "\n</manifest>\n"
        '<spine toc="ncx">\n' + "\n".join(spine) + "\n</spine>\n</package>\n"
    )
    ET.fromstring(opf.encode("utf-8"))

    container = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n'
        '<rootfiles><rootfile full-path="OEBPS/package.opf" media-type="application/oebps-package+xml"/></rootfiles>\n'
        "</container>\n"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_path, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype"), "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml", container, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/package.opf", opf, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/nav.xhtml", nav, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/toc.ncx", ncx, compress_type=zipfile.ZIP_DEFLATED)
        z.write(ASSETS / "style.css", "OEBPS/css/style.css", compress_type=zipfile.ZIP_DEFLATED)
        for f in fonts:
            z.write(f, f"OEBPS/fonts/{f.name}", compress_type=zipfile.ZIP_DEFLATED)
        for p, content in docs.items():
            z.writestr("OEBPS/" + p, content, compress_type=zipfile.ZIP_DEFLATED)
        for name, data in images.items():
            z.writestr("OEBPS/" + name, data, compress_type=zipfile.ZIP_DEFLATED)
    return docs


# ---------------------------------------------------------------------------
# Capa
# ---------------------------------------------------------------------------
def build_cover(meta, vol, cover, out_jpg):
    tpl = (ASSETS / "cover.html").read_text(encoding="utf-8")
    stats = []
    for n, l in cover.get("stats", []):
        if n.upper() == "A4":
            n, l = meta["ano"], "Edição Kindle"
        stats.append(f'<div class="s"><div class="n">{esc(n)}</div><div class="l">{esc(l)}</div></div>')
    sub = cover.get("subtitulo_html") or ""
    page = (
        tpl.replace("{{VOL}}", vol["num"])
        .replace("{{LABEL}}", esc(cover.get("label") or ""))
        .replace("{{SITE}}", esc(meta["site"]))
        .replace("{{EYEBROW}}", esc(cover.get("eyebrow") or ""))
        .replace("{{TITLE}}", cover.get("titulo_html") or esc(vol["titulo"]))
        .replace("{{SUBTITLE}}", f'<p class="subtitle">{sub}</p>' if sub else "")
        .replace("{{DECK}}", esc(cover.get("deck") or ""))
        .replace("{{STATS}}", "".join(stats))
        .replace("{{ANO}}", meta["ano"])
    )
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        shutil.copytree(ASSETS / "fonts", td / "fonts")
        src = td / "cover.html"
        src.write_text(page, encoding="utf-8")
        png = td / "cover.png"
        cmd = [
            CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
            "--allow-file-access-from-files", "--force-device-scale-factor=1", "--window-size=1600,2560",
            "--virtual-time-budget=3000", f"--screenshot={png}", src.as_uri(),
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        im = Image.open(png).convert("RGB")
        if im.size != (1600, 2560):
            im = im.resize((1600, 2560))
        out_jpg.parent.mkdir(parents=True, exist_ok=True)
        im.save(out_jpg, "JPEG", quality=92, dpi=(300, 300), optimize=True)


# ---------------------------------------------------------------------------
# Ficha KDP
# ---------------------------------------------------------------------------
def ficha_kdp(meta, vol, chapters, epub_name, jpg_name):
    kw = "\n".join(f"{i + 1}. {k}" for i, k in enumerate(vol["palavras_chave"]))
    cats = "\n".join(f"- {c}" for c in vol["categorias"])
    desc_html = "\n".join(f"<p>{html.escape(p, quote=False)}</p>" for p in vol["descricao"])
    desc_txt = "\n\n".join(vol["descricao"])
    caps = "\n".join(f"- {nav_title(t)}" for t, _ in chapters)
    return f"""# Ficha KDP · Volume {vol['num']} · {vol['titulo']}

Arquivos desta pasta:

- Manuscrito: `{epub_name}` (EPUB, formato recomendado pela KDP)
- Capa: `{jpg_name}` (JPG 1600 x 2560 px, RGB)

Preencha o cadastro em kdp.amazon.com copiando os campos abaixo.

## Detalhes do e-book

| Campo | Valor |
|--|--|
| Idioma | Português (Brasil) |
| Título | {vol['titulo']} |
| Subtítulo | {vol['subtitulo']} |
| Série | {meta['serie']} · número {int(vol['num'])} |
| Edição | 1 |
| Autora | {meta['autora']} |
| Editora (opcional) | {meta['serie']} |
| Direitos de publicação | Possuo os direitos autorais e detenho os direitos de publicação necessários |
| Público principal | Adulto (não é conteúdo adulto) |
| Conteúdo gerado por IA | Marque de acordo com o processo de produção do texto e da capa |

## Descrição

Versão com HTML (a KDP aceita as tags `<p>`, `<b>`, `<i>`, `<br>`):

```html
{desc_html}
```

Versão em texto puro:

{desc_txt}

## Palavras-chave (7 campos)

{kw}

## Categorias sugeridas (escolha até 3 na árvore da KDP)

{cats}

## Sumário do e-book (como está no manuscrito)

{caps}
- Sobre a autora

## Preço e distribuição (decisão sua)

- KDP Select (exclusividade de 90 dias, Kindle Unlimited): opcional.
- Territórios: todos os territórios.
- Royalty: 70% exige preço dentro da faixa que a KDP mostra na tela de preços; fora dela vale 35%.
- DRM: escolha na tela de conteúdo; não dá pra mudar depois de publicar.
"""


LEIA_ME = """# Amazon KDP · e-books Bastidores da Sindicatura

Cada pasta desta lista tem tudo o que a Amazon pede pra publicar um e-book Kindle:

- `VNN-<nome>.epub`: o manuscrito, no formato reflowável que a KDP recomenda. Já traz folha de rosto, página de créditos, sumário navegável, os capítulos do e-book, o convite pra Mentoria, o encerramento e a página "Sobre a autora".
- `VNN-<nome>-capa.jpg`: a capa em 1600 x 2560 px (proporção 1,6:1, a que a KDP indica). Não está dentro do EPUB de propósito: a KDP pede a capa em separado e, se ela vier também no manuscrito, aparece duas vezes no livro.
- `VNN-<nome>-ficha-kdp.md`: título, subtítulo, série, descrição, palavras-chave e categorias prontos pra copiar e colar no cadastro.

## Como publicar (passo a passo)

1. Entre em kdp.amazon.com com a conta Amazon e complete o cadastro de pagamento e de impostos (uma vez só).
2. Clique em "Criar" e escolha "E-book Kindle".
3. **Detalhes do e-book:** copie idioma, título, subtítulo, série, autora, descrição, palavras-chave e categorias da ficha do volume. Em "Série", crie a série "Bastidores da Sindicatura" na primeira publicação e use o número do volume nas seguintes.
4. **Conteúdo do e-book:** escolha DRM (sim ou não), envie o `.epub` no campo do manuscrito e o `.jpg` no campo da capa. Espere a conversão e abra o "Visualizador online" pra folhear o livro. Se aparecer aviso de ortografia, revise: normalmente são termos técnicos (LGPD, ANPD, NBR) que a Amazon não conhece.
5. **Preço:** escolha os territórios, o plano de royalty (35% ou 70%) e o preço. A tela mostra a faixa aceita pro plano de 70%.
6. Clique em "Publicar". A revisão da Amazon costuma levar até 72 horas.

## Ordem sugerida de publicação

Publique primeiro um volume, confira como ficou na loja, e só depois suba os demais. A série fica ligada automaticamente pelo nome e pelo número informados no cadastro.

## Como estes arquivos foram gerados

Os EPUBs e as capas saem de `_skill/kdp/build_kdp.py`, a partir dos HTMLs em `Ebooks/` (o mesmo template que gera os PDFs do site). Os metadados de cada volume ficam em `_skill/kdp/volumes.json`. Pra regerar tudo:

```
python3 _skill/kdp/build_kdp.py
```

Os volumes 11 (quiz, que é uma ferramenta interativa) e 19 (guia do MBA, que é material de divulgação da formação) não entram na coleção da Amazon.
"""


# ---------------------------------------------------------------------------
def slugify(s):
    s = s.lower()
    s = re.sub(r"[àáâãä]", "a", s)
    s = re.sub(r"[èéêë]", "e", s)
    s = re.sub(r"[ìíîï]", "i", s)
    s = re.sub(r"[òóôõö]", "o", s)
    s = re.sub(r"[ùúûü]", "u", s)
    s = s.replace("ç", "c")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def build_volume(meta, vol, debug=False, skip_cover=False):
    src = ROOT / vol["source"]
    images = {}
    if src.suffix.lower() == ".pdf":
        blocks = pdf_to_blocks(src, debug=debug, prefix=f"V{vol['num']}", images=images)
        cover = dict(vol.get("capa", {}))
        cover.setdefault("subtitulo_html", "")
    else:
        cover, blocks = html_to_blocks(src)
        if vol.get("capa"):
            cover.update(vol["capa"])
    chapters = split_chapters(blocks)
    folder = OUT / f"V{vol['num']} - {vol['titulo']}"
    base = f"V{vol['num']}-{vol['slug']}"
    epub_path = folder / f"{base}.epub"
    jpg_path = folder / f"{base}-capa.jpg"
    md_path = folder / f"{base}-ficha-kdp.md"
    folder.mkdir(parents=True, exist_ok=True)
    build_epub(meta, vol, cover, chapters, epub_path, images)
    if not skip_cover:
        build_cover(meta, vol, cover, jpg_path)
    md_path.write_text(ficha_kdp(meta, vol, chapters, epub_path.name, jpg_path.name), encoding="utf-8")
    words = sum(len(strip_tags(b).split()) for _, bl in chapters for b in bl)
    print(f"V{vol['num']}: {len(chapters)} capítulos, {words} palavras → {epub_path.relative_to(ROOT)}")
    if EPUBCHECK:
        r = subprocess.run(["java", "-jar", EPUBCHECK, str(epub_path), "-q"], capture_output=True, text=True)
        msg = (r.stdout + r.stderr).strip()
        msg = "\n".join(l for l in msg.splitlines() if "JAVA_TOOL_OPTIONS" not in l)
        if r.returncode != 0 or msg:
            print("  epubcheck:", msg or f"exit {r.returncode}")
        else:
            print("  epubcheck: OK")
    return chapters, images


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("nums", nargs="*", help="números dos volumes (ex.: 05 22). Vazio = todos")
    ap.add_argument("--debug-pdf", action="store_true")
    ap.add_argument("--dump", action="store_true", help="grava os capítulos em XHTML solto em Amazon/_debug/")
    ap.add_argument("--skip-cover", action="store_true")
    args = ap.parse_args()
    reg = json.loads((HERE / "volumes.json").read_text(encoding="utf-8"))
    meta = {k: v for k, v in reg.items() if k != "volumes"}
    wanted = {n.zfill(2) for n in args.nums}
    OUT.mkdir(exist_ok=True)
    (OUT / "LEIA-ME.md").write_text(LEIA_ME, encoding="utf-8")
    for vol in reg["volumes"]:
        if wanted and vol["num"] not in wanted:
            continue
        chapters, images = build_volume(meta, vol, debug=args.debug_pdf, skip_cover=args.skip_cover)
        if args.dump:
            d = OUT / "_debug" / f"V{vol['num']}"
            d.mkdir(parents=True, exist_ok=True)
            css = (ASSETS / "style.css").read_text(encoding="utf-8").replace("../fonts/", "fonts/")
            (d / "style.css").write_text(css, encoding="utf-8")
            if not (d / "fonts").exists():
                shutil.copytree(ASSETS / "fonts", d / "fonts")
            body = "".join(f'<section>{"".join(bl)}</section>' for _, bl in chapters).replace('src="../images/', 'src="images/')
            for name, data in images.items():
                (d / name).parent.mkdir(parents=True, exist_ok=True)
                (d / name).write_bytes(data)
            (d / "livro.html").write_text(
                f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><link rel="stylesheet" href="style.css">'
                f"<style>body{{max-width:640px;margin:2em auto;padding:0 1em}}</style></head><body>{body}</body></html>",
                encoding="utf-8",
            )


if __name__ == "__main__":
    main()
