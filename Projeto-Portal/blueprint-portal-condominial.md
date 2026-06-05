# Blueprint do Portal — Revista Digital do Mercado Condominial

> Plano-mestre de produto para um portal de notícias e comunicação do mercado condominial: uma **junção melhorada** do que SindicoNet, SindicoLab e Condomínio Interativo fazem separadamente — em formato de **revista digital moderna e interativa**, com **área de membros**, **portal de colunistas** com fluxo editorial, e **monetização desde o lançamento**.
>
> Documento vivo · junho/2026 · baseado na análise competitiva em `analise-concorrentes-portais-condominiais.md`

---

## 1. Visão e posicionamento

**A síntese do que cada concorrente faz de melhor — sem os defeitos de cada um:**

| Pegar de… | O quê | Sem o defeito de… |
|---|---|---|
| **SindicoNet** | Escala, amplitude de conteúdo, multicanal, marketplace/serviços | …ser raso, frio e com conflito mídia×anúncio |
| **SindicoLab** | Comunidade, educação, voz autêntica, receita recorrente | …ficar preso ao nicho de só síndico profissional |
| **Condomínio Interativo** | Guia comercial, cobertura segmentada, app | …ficar limitado a uma região / ser braço de fornecedora |
| **uCondo (radar)** | Dado proprietário (censo/índice) como autoridade | …conteúdo apenas como isca para vender software |
| **Folha do Condomínio (radar)** | Experiência editorial diferenciada (cara de revista) | …formato que atrapalha mobile/SEO |

**Posicionamento proposto:** *A revista digital independente do mundo condominial* — jornalismo de qualidade + experiência de leitura premium + comunidade + educação, servindo **síndicos (profissionais e amadores), administradoras, conselheiros e moradores**, com **independência editorial declarada**.

**Frase-guia (rascunho):** "Tudo o que move o seu condomínio — com profundidade, design e independência."

---

## 2. Públicos-alvo (personas)

1. **Síndico profissional** — quer aprofundamento, dados, networking, atualização jurídica/técnica. Paga por valor.
2. **Síndico amador / morador-síndico** — quer orientação prática, "como fazer", segurança. Entra pelo gratuito.
3. **Administradora / gestor predial** — quer tendências, mercado, ferramentas, exposição de marca.
4. **Conselheiro / morador engajado** — quer entender direitos, conflitos, vida em condomínio.
5. **Fornecedor / anunciante** — quer alcançar os públicos acima (é quem paga a mídia/guia).
6. **Colunista / especialista** — advogado, engenheiro, contador, síndico-referência (produz conteúdo).

> Atender os **dois lados** (gestor + morador) é a lacuna nº 5 da análise — diferencial frente a todos.

---

## 3. Pilares de produto (os 5 "produtos" dentro do portal)

1. **Revista / Conteúdo editorial** — notícias, reportagens, colunas, vídeos, podcast, edições especiais.
2. **Área de membros** — perfis, conteúdo premium, newsletter, comunidade.
3. **Portal do colunista + redação** — produção, revisão e agendamento de matérias (fluxo editorial).
4. **Guia comercial / Marketplace de fornecedores** — diretório monetizável (fase 2).
5. **Educação & eventos** — cursos, ebooks, webinars, eventos (fase 2/3).

---

## 4. Arquitetura da informação (mapa do site)

```
HOME (capa de revista: destaques, últimas, mais lidas, vídeo, newsletter)
│
├── EDITORIAS (seções de conteúdo)
│   ├── Notícias / Mercado
│   ├── Jurídico & Legislação
│   ├── Gestão & Administração
│   ├── Manutenção & Engenharia Predial
│   ├── Finanças & Inadimplência
│   ├── Segurança & Tecnologia (proptech)
│   ├── Vida em Condomínio (morador, conflitos, convivência)
│   ├── Sustentabilidade & ESG
│   └── Carreira do Síndico (profissionalização)
│
├── COLUNISTAS (página de cada colunista + arquivo de artigos)
├── EDIÇÕES ESPECIAIS / REVISTA (PDF/flipbook + dossiês temáticos)
├── MULTIMÍDIA (Podcast · Vídeos · Webinars)
├── DADOS & INTELIGÊNCIA (índice/censo proprietário, infográficos)  ← autoridade
├── GUIA DE FORNECEDORES (diretório — fase 2)
├── EDUCAÇÃO (cursos / ebooks / eventos — fase 2/3)
│
├── ÁREA DE MEMBROS (login)
│   ├── Meu perfil / assinatura
│   ├── Conteúdo premium / salvos / histórico
│   ├── Newsletter & preferências
│   └── Comunidade (fórum/grupos)
│
├── PORTAL DO COLUNISTA (login restrito)
│   └── Painel de redação (enviar/editar matéria, acompanhar status)
│
├── PAINEL EDITORIAL / ADMIN (interno)
│   └── Revisão, agendamento, publicação, gestão de usuários e anúncios
│
└── INSTITUCIONAL (Quem somos · Anuncie · Seja colunista · Contato · Política de privacidade/LGPD · Selo de independência)
```

---

## 5. Funcionalidades — site público (revista digital, moderna e interativa)

**Experiência de revista digital:**
- Home em formato de **capa editorial** (não lista cronológica genérica) — curadoria de destaques.
- **Modo de leitura** limpo, tipografia premium, tempo de leitura, barra de progresso.
- **Edições especiais em flipbook/PDF** (cara de revista) + dossiês temáticos navegáveis.
- Design **mobile-first**, rápido (Core Web Vitals) e acessível.

**Interatividade & engajamento:**
- **Comentários** (moderados), reações, **salvar/ler depois**, compartilhar.
- **Enquetes e quizzes** ("Seu condomínio está em dia com a NR-1?"), calculadoras (fundo de reserva, rateio, reajuste).
- **Newsletter** com captura em pontos estratégicos (lead magnet: ebook/checklist).
- **Busca** inteligente + filtros por editoria, autor, tag, formato.
- **Conteúdo relacionado** e trilhas ("Síndico de primeira viagem", "Trilha jurídica").
- **Áudio do artigo** (text-to-speech) e **podcast** integrado.
- **Selo de transparência** distinguindo conteúdo editorial de branded content/publicidade.

**SEO & distribuição (para crescer sem depender de pagar mídia):**
- SEO técnico forte, sitemap, dados estruturados (Article/NewsArticle), Google News/Discover.
- Compartilhamento social automatizado, RSS, integração com WhatsApp/Telegram.

---

## 6. Área de membros e modelo de assinatura (capitalização)

**Níveis sugeridos (freemium):**

| Nível | Preço | O que inclui |
|---|---|---|
| **Visitante** | grátis | Conteúdo aberto, newsletter básica, comentários |
| **Membro (cadastro grátis)** | grátis | Salvar artigos, comentar, newsletter segmentada, acesso parcial |
| **Premium** (B2C) | mensal/anual | Conteúdo aprofundado/exclusivo, edições da revista, dados/relatórios, sem anúncios, comunidade |
| **Pro / Profissional** | mensal/anual | Tudo do Premium + trilhas de educação, certificados, descontos em eventos, networking |
| **Corporativo** (administradoras/fornecedores) | sob consulta | Múltiplos acessos, branded content, destaque no guia, relatórios de marca |

**Mecânica:** **paywall flexível** (metered — X artigos grátis/mês, ou por marcação de conteúdo premium), checkout com pagamento recorrente, gestão de assinatura, cupons, período de teste, área "minha conta".

**Por que freemium e não tudo pago:** preserva tráfego/SEO e o público de morador (escala) enquanto monetiza o profissional (valor). Combina o melhor do SindicoNet (escala) e do SindicoLab (recorrência).

---

## 7. Portal do colunista + fluxo editorial ⭐ (requisito central)

### 7.1 Papéis e permissões (RBAC)

| Papel | Pode… | Não pode… |
|---|---|---|
| **Colunista / Autor** | Criar, editar, **enviar** suas próprias matérias; salvar rascunho; anexar imagens; ver status e feedback | Publicar, agendar, editar matéria de outro, mexer em config |
| **Revisor / Editor** | Ler, **revisar**, comentar, solicitar ajustes, **aprovar**, **agendar** publicação, editar texto | Gerir faturamento/usuários admin (depende) |
| **Editor-chefe** | Tudo do Editor + **publicar imediato**, definir capa/destaques, gerir editorias | — |
| **Admin** | Tudo + gestão de usuários, anúncios, assinaturas, configurações | — |

### 7.2 Fluxo da matéria (máquina de estados)

```
[Rascunho] ──(colunista envia)──► [Enviado / Em revisão]
     ▲                                   │
     │                          ┌────────┴─────────┐
     │              (editor pede ajuste)     (editor aprova)
     │                          │                  │
     └──────[Ajustes solicitados]◄┘          [Aprovado]
                                                  │
                                        (editor agenda data/hora)
                                                  │
                                            [Agendado]
                                                  │
                                        (chega a data → automático)
                                                  │
                                           [Publicado] ──► (pode ir a [Arquivado])
```

**Regras-chave do fluxo:**
- O colunista **só carrega e envia** — nunca publica direto. ✔ (seu requisito)
- **Nada vai ao ar sem aprovação** de um revisor/editor da equipe. ✔
- **Agendamento** de data/hora de publicação pela equipe. ✔
- Notificações automáticas em cada transição (e-mail/painel): "sua matéria foi aprovada e agendada para 12/06 às 9h", "ajustes solicitados", etc.
- **Histórico de versões** e trilha de comentários entre colunista e editor.
- **Editor de texto rico** (negrito, links, imagens com crédito/legenda, citações, embeds de vídeo/Instagram), capa, resumo (dek), categorias, tags, SEO (título/meta), autor e coautor.
- **Checklist de publicação** (imagem de capa, alt text, fonte, revisão jurídica se aplicável).
- **Biblioteca de mídia** com direitos/créditos.
- Opcional: **calendário editorial** (kanban: Pauta → Em produção → Em revisão → Agendado → Publicado).

### 7.3 Página pública do colunista
Bio, foto, especialidade, redes, arquivo de artigos, "seguir colunista" (notifica membros). Reforça a **voz/autoria** — diferencial frente ao conteúdo anônimo do SindicoNet.

---

## 8. Monetização / capitalização (as fontes de receita)

| Fonte | Descrição | Fase |
|---|---|---|
| **Publicidade / branded content** | Banners, native ads, conteúdo patrocinado (com selo), newsletter patrocinada | MVP |
| **Assinatura Premium/Pro** | Recorrência B2C/B2P (área de membros) | MVP/V1 |
| **Guia de fornecedores** | Listagem paga, destaque, geração de leads | V1/V2 |
| **Educação** | Cursos, ebooks, webinars pagos | V2 |
| **Eventos** | Online e presenciais, patrocínio, ingressos | V2/V3 |
| **Dados & inteligência** | Relatórios/índice proprietário (venda B2B, patrocínio de estudo) | V2 |
| **Planos corporativos** | Administradoras/fornecedores (multi-acesso + mídia) | V1/V2 |

**Princípio de independência:** publicidade sempre identificada; muralha entre redação e comercial (evita o problema percebido no SindicoNet).

---

## 9. Stack tecnológica — opções e recomendação

Há três caminhos. A escolha define orçamento, prazo e flexibilidade:

| Caminho | Como | Prós | Contras | Indicado se… |
|---|---|---|---|---|
| **A) WordPress + plugins** | WP + tema revista + Memberships (MemberPress/Paid Memberships Pro) + WooCommerce + plugins de fluxo editorial (PublishPress) | Rápido, barato, fluxo editorial e paywall **prontos**, enorme ecossistema | Menos "único", performance exige cuidado, customização interativa limitada | Quer **lançar rápido e barato**, validar o negócio |
| **B) Headless CMS + front moderno** | CMS (Strapi/Sanity/WordPress headless) + Next.js + Stripe + Auth | Performance e design premium, muito flexível/interativo, ótimo SEO | Mais caro, precisa de devs, fluxo editorial pode exigir build | Quer **experiência diferenciada** e escala, com time técnico |
| **C) Plataforma de publishing** | Substack/Ghost/Memberful etc. | Newsletter+assinatura nativas, simplicíssimo | Pouco flexível p/ revista+guia+colunistas múltiplos+fluxo | Só para validar newsletter/assinatura inicial |

**Recomendação:** começar no **Caminho A (WordPress)** para o **MVP** — entrega o fluxo editorial, paywall e área de membros com baixo custo e rapidez — e **migrar para B (headless)** quando o produto/receita justificarem o investimento em experiência premium. (O WordPress já entrega 90% do seu requisito de portal do colunista com PublishPress + papéis nativos.)

> ⚙️ *Decisão necessária com você: orçamento e se há/haverá time técnico. Isso define A vs B.*

---

## 10. Integrações necessárias

- **Pagamentos/assinatura recorrente:** Stripe, ou nacionais (Pagar.me, Asaas, Vindi, Hotmart para infoprodutos).
- **E-mail marketing/newsletter:** RD Station, Mailchimp, Brevo, Beehiiv.
- **Analytics:** GA4 + Search Console + (Hotjar/Clarity para comportamento).
- **Comunidade:** fórum nativo, ou WhatsApp/Telegram/Discord/Circle.
- **Comentários/moderação**, **antispam**, **CDN**, **busca** (Algolia opcional).
- **Notificações** (e-mail transacional: Resend/SendGrid) para o fluxo editorial.
- **Push/PWA ou app** (fase posterior — como o Condomínio Interativo).

---

## 11. Requisitos não-funcionais

- **SEO técnico** (dados estruturados, performance, Google News) — motor de crescimento orgânico.
- **Performance / Core Web Vitals** — essencial para revista mobile.
- **LGPD** — consentimento de cookies, política de privacidade, gestão de dados de membros, base legal para newsletter.
- **Acessibilidade** (WCAG) — leitura para todos + bônus de SEO.
- **Segurança** — papéis/permissões, 2FA no admin, backups, proteção do paywall.
- **Escalabilidade** e **observabilidade** (uptime, erros).

---

## 12. Roadmap por fases

### MVP (lançar e começar a capitalizar) — ~"Fase 1"
- Site editorial com editorias + home de revista + páginas de colunista.
- **Portal do colunista + fluxo revisão/agendamento/publicação** (requisito central). ✔
- Cadastro de membros + **newsletter** + **1 nível de assinatura Premium** (paywall metered).
- Publicidade/branded content básico.
- SEO, analytics, LGPD.

### V1 — consolidação
- Níveis Pro/Corporativo, comunidade, comentários avançados, multimídia (podcast/vídeo).
- **Guia de fornecedores** (monetização B2B).
- Edições especiais em flipbook, calculadoras/quizzes.

### V2 — expansão
- **Dados/índice proprietário** (autoridade — lição uCondo).
- Educação (cursos/ebooks) e eventos.
- App/PWA, regionalização (cadernos locais — lição Jornal do Síndico/Cond. Interativo).

---

## 13. Métricas / KPIs

- **Audiência:** usuários únicos, pageviews, tempo de leitura, tráfego orgânico.
- **Engajamento:** assinantes de newsletter, taxa de abertura, comentários, salvamentos.
- **Receita:** assinantes pagos, MRR, churn, ticket de anúncio, leads do guia.
- **Editorial:** nº de matérias/semana, tempo médio rascunho→publicação, colunistas ativos.

---

## 14. Equipe mínima

- **Editor-chefe** (curadoria, aprovação, agenda) + **revisor(es)**.
- **Rede de colunistas** (parceria/cachê/permuta).
- **Comercial / mídia** (anúncios, guia, patrocínios).
- **Social media / newsletter**.
- **Técnico** (dev/manutenção — interno ou agência, conforme caminho A/B).

---

## 15. Riscos & mitigação

| Risco | Mitigação |
|---|---|
| SindicoNet domina SEO | Competir em profundidade/voz/nicho, não em volume genérico |
| Dependência de publicidade pressiona independência | Diversificar (assinatura + educação + eventos) desde cedo |
| Fluxo editorial travar produção | Calendário editorial + papéis claros + automações de notificação |
| Conteúdo escala mas não converte em pago | Paywall calibrado + lead magnets + segmentação de newsletter |
| Custo técnico alto cedo demais | Começar no WordPress (A) e migrar quando houver receita |

---

### Próximas decisões para destravar a execução
1. **Orçamento e time técnico** → define Caminho A (WordPress) vs B (headless).
2. **Prioridade de monetização no lançamento** → assinatura, publicidade ou guia primeiro?
3. **Escopo do MVP** → enxuto (conteúdo + colunistas + newsletter) ou já com assinatura paga?
4. **Marca/nome e identidade visual** da revista.
