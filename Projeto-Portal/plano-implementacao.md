# Plano de Implementação — Portal/Revista Condominial

> Como vamos construir, com qual stack, em que ordem e em quanto tempo. Premissa: **caminho headless/sob medida**, com o desenvolvimento conduzido por mim (Claude Code) neste repositório.

---

## 1. Arquitetura recomendada

```
┌──────────────────────────────────────────────────────────┐
│                    NAVEGADOR (leitor/membro)               │
└───────────────┬───────────────────────────┬───────────────┘
                │ (site público SSR/SSG)     │ (área logada)
        ┌───────▼─────────┐         ┌────────▼────────┐
        │   Next.js (App  │◄────────│  Payload CMS     │
        │   Router) +     │  API    │  (admin + API +  │
        │   Tailwind +    │         │  RBAC + fluxo    │
        │   React         │         │  editorial)      │
        └───────┬─────────┘         └────────┬─────────┘
                │                            │
   ┌────────────┼──────────────┬────────────┼───────────┐
   ▼            ▼              ▼            ▼           ▼
Stripe/Asaas  Resend        PostgreSQL   Storage     GA4 /
(assinatura)  (e-mails      (Neon/        (S3/UploadThing  Search
              transac.)     Supabase)     mídia)      Console)
```

**Stack:**
- **Frontend:** Next.js (App Router) + TypeScript + Tailwind CSS + React. SSG/ISR para SEO e velocidade (revista).
- **CMS / Backend:** **Payload CMS** (Node/TS) — entrega nativamente: autenticação, **papéis/permissões (RBAC)**, **drafts + versões**, **publicação agendada**, **access control** por documento, editor rich text, upload de mídia, hooks (notificações). É o coração do **fluxo do colunista**.
- **Banco:** PostgreSQL gerenciado (Neon ou Supabase).
- **Pagamentos:** Stripe (cartão internacional/assinatura) + **Asaas/Pagar.me** (Pix/boleto, mercado BR). Webhooks → libera acesso.
- **E-mail:** Resend (transacional: fluxo editorial, recuperação de senha) + ferramenta de newsletter (Brevo/Beehiiv/RD).
- **Mídia/CDN:** storage de imagens + CDN da Vercel.
- **Hospedagem:** Vercel (app) + Neon (DB) — baixo custo inicial, escala sob demanda.
- **Analytics:** GA4 + Search Console + Clarity (mapa de calor).

**Por que Payload:** o requisito do colunista (enviar → revisar → ajustar → aprovar → agendar → publicar, com papéis e notificações) é praticamente *nativo* no Payload, reduzindo muito o código sob medida e o tempo de entrega — mantendo 100% de customização.

---

## 2. Modelo de dados (coleções principais)

- **Users** (papel: colunista/editor/editor-chefe/admin; bio, foto, especialidade).
- **Members** (assinantes: plano, status de assinatura, salvos, preferências). *(pode ser extensão de Users)*
- **Articles** (título, dek, corpo rich text, capa, autor, coautor, editoria, tags, SEO, **status**, dataAgendada, dataPublicação, flag premium, flag patrocinado/selo, versões).
- **Categories/Editorias**, **Tags**.
- **Comments** (moderação).
- **Suppliers** (guia: categoria, região, plano, contato, leads).
- **Ads/Patrocínios** (posição, peça, período, anunciante).
- **Subscriptions/Plans** (níveis, preços, gateway, status).
- **Events/Courses/Ebooks** (fase 2).
- **MediaLibrary** (créditos/alt).

**Estados do Article (workflow):** `rascunho · em_revisao · ajustes_solicitados · aprovado · agendado · publicado · arquivado` — com regras de transição por papel e hooks de notificação.

---

## 3. Estratégia de entrega em ONDAS (capitalizar cedo)

Você escolheu MVP **Completo** + 4 monetizações. Para não esperar "tudo pronto", construo em **ondas curtas — cada uma já no ar e gerando valor:**

### 🌊 Onda 0 — Fundação (semana 1–2)
- Setup repo, Next.js + Payload + Postgres, deploy na Vercel, CI.
- Design tokens (cores/tipografia da marca), layout base, componentes.
- Coleções: Users, Articles, Categories, MediaLibrary.
- **Entregável:** ambiente no ar, admin funcionando, 1 artigo publicado de teste.

### 🌊 Onda 1 — Revista pública + SEO (semana 3–4)
- Home (capa), editorias, artigo, página do colunista, busca, newsletter.
- SEO técnico, performance, LGPD (cookies/política), GA4.
- **Entregável:** portal editorial público no ar — já pode publicar conteúdo e crescer audiência.
- **💰 Monetização ligada:** publicidade/branded content básico (Épico 7) + captação de newsletter.

### 🌊 Onda 2 — Portal do colunista + fluxo editorial ⭐ (semana 5–7)
- Painel do colunista, editor de matéria, envio.
- Fila de revisão, solicitar ajustes, aprovar, **agendar/publicar**, notificações.
- Calendário editorial (kanban), versões, checklist.
- **Entregável:** sua redação distribuída operando — colunistas produzem, equipe revisa/agenda.

### 🌊 Onda 3 — Contas, área de membros e assinatura (semana 8–10)
- Cadastro/login, dashboard do membro, salvos, perfil (LGPD).
- Planos, checkout recorrente (Stripe + Asaas/Pix), paywall, gestão de assinatura.
- **Entregável:** área de membros + assinatura no ar.
- **💰 Monetização ligada:** assinatura Premium/Pro (receita recorrente).

### 🌊 Onda 4 — Guia de fornecedores + comunidade (semana 11–13)
- Diretório, fichas, busca, solicitação de orçamento (leads), planos de fornecedor.
- Comunidade (fórum/grupos) + comentários.
- **Entregável:** guia comercial no ar.
- **💰 Monetização ligada:** guia/leads + planos corporativos.

### 🌊 Onda 5 — Educação, eventos & dados (semana 14+)
- Ebooks/cursos/eventos com checkout; índice/relatório proprietário.
- **💰 Monetização ligada:** educação/eventos + autoridade (dados).

> Cronograma é estimativa de ritmo de desenvolvimento assistido por IA; depende de validações suas, definição de marca/conteúdo e criação de contas (pagamento/hospedagem). As ondas 1–3 já entregam um produto que **publica conteúdo e fatura**.

---

## 4. Pré-requisitos que dependem de você (paralelo ao desenvolvimento)
- [ ] **Decisão de nome/marca** + cor principal (destrava design tokens).
- [ ] **Domínio** registrado (registro.br).
- [ ] Contas: **Vercel**, **Neon/Supabase**, **Stripe** e/ou **Asaas/Pagar.me**, **Resend**, ferramenta de **newsletter**.
- [ ] Conteúdo inicial: textos institucionais, 5–10 matérias de lançamento, cadastro de colunistas.
- [ ] Definição de **preços** dos planos e categorias do guia.
- [ ] Política de privacidade/termos (LGPD) — posso redigir um rascunho.

---

## 5. Custos aproximados (ordem de grandeza, início)
- Hospedagem/infra: faixa **gratuita a baixa** no começo (Vercel/Neon têm planos free; crescem com tráfego).
- Pagamentos: sem mensalidade, **taxa por transação** (Stripe/Asaas).
- E-mail/newsletter: free até X contatos, depois mensalidade por volume.
- Domínio: anual baixo.
- **Desenvolvimento do núcleo:** conduzido por mim (sem custo de agência).
- *Custos sobem com escala (tráfego, e-mails, armazenamento) — previsível e proporcional à receita.*

---

## 6. Riscos técnicos & mitigação
| Risco | Mitigação |
|---|---|
| Escopo "Completo" atrasar lançamento | Ondas curtas — publicar a cada onda, não esperar o todo |
| Pagamento recorrente no BR (Pix) | Usar gateway nacional (Asaas/Pagar.me) além de Stripe |
| Performance da revista (mídia pesada) | ISR/SSG, otimização de imagem, CDN |
| Migração futura/complexidade | Payload + Postgres são portáveis e padrão de mercado |
| Dependência de uma pessoa (eu) no código | Código limpo, documentado e versionado no Git (qualquer dev assume) |

---

## 7. Próximo passo imediato (quando você der o "vai")
1. Você confirma **nome + cor de marca** (ou escolhemos juntos da lista de identidade).
2. Eu inicio a **Onda 0**: scaffolding do projeto (Next.js + Payload + Postgres) neste repositório, com deploy de demonstração.
3. A partir daí, entrego onda a onda, mostrando cada parte funcionando para sua validação.
