# Mapa de Telas & Wireframes — Portal/Revista Condominial

> Inventário completo de telas (público, área de membros, portal do colunista, painel editorial) com wireframes em baixa fidelidade (ASCII). Base para design e desenvolvimento.

---

## 1. Inventário de telas

### A. Público (sem login)
1. Home (capa de revista)
2. Página de editoria (lista filtrável)
3. Artigo / matéria (leitura)
4. Página do colunista (perfil + arquivo)
5. Edições especiais / Revista (flipbook)
6. Multimídia (podcast/vídeo)
7. Dados & Inteligência (índice/infográficos)
8. Guia de fornecedores (busca + ficha)
9. Educação (cursos/ebooks/eventos)
10. Busca / resultados
11. Institucional (Quem somos, Anuncie, Seja colunista, Contato, Privacidade)
12. Login / Cadastro / Recuperar senha
13. Planos & Assinatura (pricing) + Checkout

### B. Área de membros (login)
14. Dashboard do membro
15. Meu perfil & conta
16. Minha assinatura / pagamento
17. Salvos / histórico de leitura
18. Preferências de newsletter
19. Comunidade (fórum/grupos)

### C. Portal do colunista (login restrito)
20. Painel do colunista (minhas matérias + status)
21. Editor de matéria (criar/editar/enviar)
22. Detalhe da matéria (feedback do editor / versões)

### D. Painel editorial / Admin (interno)
23. Fila de revisão (kanban/lista)
24. Revisão da matéria (aprovar/ajustar/agendar)
25. Calendário editorial
26. Gestão de usuários & papéis
27. Gestão de anúncios / patrocínios
28. Gestão de assinaturas & relatórios
29. Gestão do guia de fornecedores

---

## 2. Wireframes (baixa fidelidade)

### 1. Home (capa de revista)
```
┌───────────────────────────────────────────────┐
│ LOGO    Editorias ▾  Dados  Guia  Educação   🔍 [Entrar][Assinar] │
├───────────────────────────────────────────────┤
│ ┌───────────────── DESTAQUE ─────────────────┐ │
│ │  [IMG grande]   MANCHETE PRINCIPAL          │ │
│ │                 dek/resumo · Coluna · 5 min │ │
│ └─────────────────────────────────────────────┘ │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│ │ Sec.dest │ │ Sec.dest │ │ Sec.dest │          │
│ └──────────┘ └──────────┘ └──────────┘          │
│ ─ ÚLTIMAS ─────────────────  ─ MAIS LIDAS ─     │
│ • matéria ...                1. ...             │
│ • matéria ...                2. ...             │
│ ┌── NEWSLETTER ──┐  ┌── PODCAST ──┐  [Banner ad]│
│ │ e-mail [Assinar]│  │ ▶ ep. atual │            │
│ └────────────────┘  └─────────────┘             │
├───────────────────────────────────────────────┤
│ Footer: editorias · institucional · LGPD · redes│
└───────────────────────────────────────────────┘
```

### 3. Artigo / matéria
```
┌───────────────────────────────────────────────┐
│ [breadcrumb] Editoria > Título                 │
│ ████ Selo: CONTEÚDO INDEPENDENTE / PATROCINADO │
│ TÍTULO DA MATÉRIA                              │
│ dek/resumo                                     │
│ [foto autor] Por COLUNISTA · 10/06 · 6 min ▶Áudio│
│ ┌─────────── [IMAGEM DE CAPA] ──────────────┐  │
│ └─────────────────────────────────────────┘   │
│ Corpo do texto.......... [barra progresso ▸]   │
│ > citação destacada                            │
│ .................. [🔒 paywall p/ não-assinante]│
│ ───────────────────────────────────────────   │
│ Tags · Compartilhar · Salvar · Comentar        │
│ ── Sobre o colunista ──  ── Relacionados ──    │
│ ── Comentários (moderados) ──                  │
└───────────────────────────────────────────────┘
```

### 13. Planos & Assinatura
```
┌───────────────────────────────────────────────┐
│           Escolha seu plano                    │
│ ┌ Grátis ┐ ┌ Premium ⭐┐ ┌ Pro ┐ ┌Corporativo┐ │
│ │ R$0    │ │ R$/mês    │ │R$/mês│ │sob consulta│ │
│ │ • ...  │ │ • ...     │ │•...  │ │ • ...      │ │
│ │[Criar] │ │[Assinar]  │ │[Assin]│ │[Falar]    │ │
│ └────────┘ └───────────┘ └──────┘ └───────────┘ │
│ Comparativo de recursos (tabela) ▾             │
└───────────────────────────────────────────────┘
```

### 20. Painel do colunista
```
┌───────────────────────────────────────────────┐
│ Olá, [Colunista]            [+ Nova matéria]   │
├───────────────────────────────────────────────┤
│ Minhas matérias            filtro: [Status ▾]  │
│ ┌─────────────────────────────────────────────┐│
│ │ Título            │ Status        │ Data     ││
│ │ Reforma da NR-1   │ 🟡 Em revisão │ —        ││
│ │ Fundo de reserva  │ 🟠 Ajustes    │ —        ││
│ │ Inadimplência 2026│ 🔵 Agendado   │ 12/06 9h ││
│ │ Convivência pets  │ 🟢 Publicado  │ 02/06    ││
│ └─────────────────────────────────────────────┘│
│ (clicar abre detalhe c/ feedback do editor)    │
└───────────────────────────────────────────────┘
```

### 21. Editor de matéria (colunista)
```
┌───────────────────────────────────────────────┐
│ Título: [_______________________]             │
│ Resumo/dek: [__________________]              │
│ Editoria: [▾]   Tags: [____]                  │
│ Capa: [⬆ upload imagem] (crédito/alt)         │
│ ┌── Editor rico ───────────────────────────┐  │
│ │ B I “ ” • link 🖼 ▶embed  H2 H3           │  │
│ │ [corpo do texto...]                       │  │
│ └──────────────────────────────────────────┘  │
│ SEO: título/meta [____]                        │
│ [Salvar rascunho]   [Enviar para revisão ▶]    │
└───────────────────────────────────────────────┘
   (Enviar => status muda para "Em revisão";
    colunista NÃO publica nem agenda)
```

### 24. Revisão da matéria (editor)
```
┌───────────────────────────────────────────────┐
│ [Texto do colunista]        │ Painel do editor │
│  ......................      │ ◦ Comentar trecho│
│  ......................      │ ◦ Histórico vers.│
│                             │ ─────────────────│
│                             │ Ações:           │
│                             │ [Solicitar ajuste]│
│                             │ [Aprovar]         │
│                             │ Agendar: [data/hora]│
│                             │ [Agendar publicação]│
│                             │ [Publicar agora]  │
└───────────────────────────────────────────────┘
```

### 25. Calendário editorial (kanban)
```
┌─ Pauta ─┐ ┌ Em produção ┐ ┌ Em revisão ┐ ┌ Agendado ┐ ┌ Publicado ┐
│ card    │ │ card        │ │ card       │ │ card 12/6│ │ card      │
│ card    │ │ card        │ │ card       │ │ card 13/6│ │ card      │
└─────────┘ └─────────────┘ └────────────┘ └──────────┘ └───────────┘
(arrastar entre colunas; visão semana/mês)
```

---

## 3. Fluxos principais (jornadas)
1. **Leitor → assinante:** Home → artigo → atinge paywall → Planos → Checkout → membro.
2. **Colunista → publicação:** login → +Nova matéria → escreve → Enviar → (recebe feedback) → ajusta → aprovado/agendado → publicado (notificado).
3. **Editor:** notificação de nova submissão → Fila de revisão → revisa → aprova/ajusta → agenda → publica.
4. **Fornecedor:** Anuncie → contato/checkout → ficha no guia + campanha.

> Próximo nível de fidelidade: posso converter estes wireframes em design real no **Figma** (há integração disponível) ou direto em **código (componentes React/Tailwind)**.
