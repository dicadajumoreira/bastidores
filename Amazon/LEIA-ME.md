# Amazon KDP · e-books Bastidores da Sindicatura

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

## Se a KDP não deixar avançar

A mensagem "Corrija o(s) erro(s) destacado(s) para continuar" aparece no fim da página, mas o campo com problema fica mais acima. A causa mais comum aqui é a descrição: cole só o texto da ficha, sem nenhum `<p>`. Cada ficha tem, no fim, a lista completa do que conferir.

## Ordem sugerida de publicação

Publique primeiro um volume, confira como ficou na loja, e só depois suba os demais. A série fica ligada automaticamente pelo nome e pelo número informados no cadastro.

## Como estes arquivos foram gerados

Os EPUBs e as capas saem de `_skill/kdp/build_kdp.py`, a partir dos HTMLs em `Ebooks/` (o mesmo template que gera os PDFs do site). Os metadados de cada volume ficam em `_skill/kdp/volumes.json`. Pra regerar tudo:

```
python3 _skill/kdp/build_kdp.py
```

Os volumes 11 (quiz, que é uma ferramenta interativa) e 19 (guia do MBA, que é material de divulgação da formação) não entram na coleção da Amazon.
