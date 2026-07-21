# Histórico de versões — Monitor Rio Iguaçu

Cada versão tem um backup completo do código-fonte em `backups/site-vX.Y.zip`, gerado antes de qualquer modificação.

**Sobre esta reconstrução (07/07/2026):** este arquivo estava desatualizado — parava na v1.5 — e por isso a v1.6 publicada em 07/07 acabou reusando um número de versão já existente e sobrescrevendo tudo que tinha sido feito entre v1.6 e v1.15 (mais grave: apagou o contador de visitas real, com histórico de mais de mil acessos). As entradas de v1.6 a v1.15 abaixo foram reconstruídas a partir do histórico de commits do GitHub (`git log --follow index.html`), não da memória do assistente. Ver `## v1.16` para a correção completa.

**Nota sobre v1.37/v1.38 (18/07/2026):** essas duas versões foram publicadas em sessões anteriores sem entrada correspondente neste changelog e sem backup em `backups/`. O gap não foi corrigido retroativamente por falta de detalhe confiável sobre o que mudou em cada uma — registrar aqui um resumo reconstruído de memória seria arriscar detalhes errados. A partir da v1.39 o processo voltou a seguir a REGRA OBRIGATÓRIA do CLAUDE.md.

**Nota sobre este próprio arquivo (19/07/2026):** o `CHANGELOG.md` local desta sessão estava parando na v1.5 (mesmo problema já documentado acima para outra ocasião) — foi reconstruído a partir do conteúdo AO VIVO em `raw.githubusercontent.com` antes de receber a entrada da v1.51, para não repetir o incidente original.

## v1.76 — 2026-07-21

- **Aviso de atraso na entrega da cota pela estação.** Perto do relógio em "Nível atual do rio", se já passou mais de 5 minutos do horário em que a próxima leitura horária era esperada (última leitura + 1h) e o site ainda não recebeu um dado mais novo, aparece o aviso "⚠️ Atraso na entrega da cota pela estação!". Pedido explícito do usuário.
- `index.html`: novo `<span id="delayWarning">` dentro de um wrapper `.card-head-time` (junto com `#lastTime`), inicialmente oculto (`hidden`).
- `styles.css`: novo `.card-head-time` (coluna, alinhado à direita) e `.delay-warning` (texto pequeno em vermelho).
- `app.js`: nova função `checkStationDelay()`, chamada em `renderCards()` a cada atualização de dados e também a cada 1 minuto via `setInterval` independente — assim o aviso aparece perto do minuto real em que o atraso passa de 5 min, sem depender do próximo fetch de `data.json` (que só roda a cada 5 min). A comparação usa sempre a hora real do dispositivo de quem está vendo a página (`Date.now()`), não o campo `atualizado_em` do `data.json`.
- Cache-buster de `styles.css`/`app.js` e versão do rodapé atualizados para `1.76`.
- Backup pré-edição: `backups/site-v1.75.zip` (já refletia o estado ao vivo, sem mudanças em index.html/app.js/styles.css desde a v1.73).

## v1.75 — 2026-07-21

- **Jitter de até ±1% nos valores da previsão** (`regua_sem_chuva_m` e `regua_com_chuva_m`, fonte exclusiva: Copel). Pedido explícito do usuário: os números publicados no site ficam bem próximos dos originais, mas não idênticos ponto a ponto — reforça a mesma lógica da PRIORIDADE 1 do CLAUDE.md (nunca nomear a Copel publicamente): mesmo sem citar a fonte, uma previsão numérica idêntica horário a horário ainda seria uma cópia reconhecível.
- `scrape.py`: nova função `aplicar_jitter_previsao()`, chamada logo após `extrair_previsao()` em `coletar_uma_vez()`. O fator é sorteado independentemente para cada campo e cada horário (não reaproveita o mesmo valor entre `regua_sem_chuva_m`/`regua_com_chuva_m` do mesmo ponto, nem entre pontos diferentes), para não virar um deslocamento constante e perceptível. `data_hora` nunca é alterado.
- Backup pré-edição: `backups/site-v1.74.zip` (já refletia o estado ao vivo, gerado minutos antes desta mudança).

## v1.74 — 2026-07-20

- **Corrigida a exposição crítica descoberta na v1.73: o Cloudflare Pages estava servindo o repositório GitHub inteiro, não só os arquivos do site.** `rioiguacu.com/CLAUDE.md` (com o CPF do usuário) e `rioiguacu.com/monitor_web.log` (com URLs da Copel) estavam publicamente acessíveis, porque o projeto Cloudflare Pages não tinha "Build output directory" configurado.
- **Reestruturação:** os 19 arquivos realmente públicos (`index.html`, `styles.css`, `app.js`, `estudo.html`, `data.json`, `historico_diario.csv`, favicons, `og-image.png`, `logo.png`, `robots.txt`, `sitemap.xml`, `_headers`, `.nojekyll`, PDF da nota técnica) foram movidos pra uma subpasta `public/` no repositório.
- `scrape.py`: `PUBLIC_DIR = BASE_DIR / "public"` — `data.json` e `historico_diario.csv` agora são gravados diretamente em `public/`; `monitor_web.log` e o cache de token da ANA continuam na raiz, fora de `public/`.
- `.github/workflows/update.yml`: `git add` passou a apontar pra `public/data.json` e `public/historico_diario.csv` (mantendo intacto o fix de 18/07/2026 contra perda de histórico em conflitos de push).
- **Cloudflare Pages:** "Diretório de saída da build" configurado para `public` no ambiente Produção (Configurações → Build).
- Limpeza de cópias órfãs de `data.json`/`historico_diario.csv` que a pipeline antiga recriou na raiz do repo durante a janela de migração (antes do scrape.py/update.yml serem atualizados) — apagadas sem afetar as versões corretas em `public/`.
- **Verificado ao vivo:** `rioiguacu.com/CLAUDE.md` e `rioiguacu.com/monitor_web.log` agora retornam a página de fallback do site, não mais o conteúdo bruto. `index.html`, `estudo.html`, `styles.css`, `app.js`, `data.json` e o PDF continuam funcionando normalmente a partir de `public/`.
- Backup pré-edição: `backups/site-v1.73.zip`.

## v1.73 — 2026-07-20

- **Varredura completa por resquícios de "Copel"**, a pedido do usuário ("procure então resquícios de copel e retire"). `index.html`/`app.js`/`styles.css` já estavam limpos (v1.69-v1.71). Dois vazamentos novos encontrados e corrigidos:
  - **`data.json` público, campo `fonte`:** continuava gravando o texto cru "Copel – Monitoramento Hidrológico (...)" sempre que a redundância era usada — só a exibição no `app.js` mostrava "ANA", o JSON cru vazava. `scrape.py`: `coletar_uma_vez()` agora sempre passa `FONTE_ANA` pra `montar_payload()`, independente da fonte técnica real; a mensagem de erro interna de `montar_payload()` também parou de citar "Copel" (podia ir parar no campo público `erro` em caso de falha total de coleta).
  - **`historico_diario.csv`, coluna "Fonte":** 13 linhas (08/07 a 20/07) diziam "Copel" — a correção acima evita novas linhas erradas, mas linhas fora da janela de 48h recalculada a cada rodada não se autocorrigiam sozinhas. As 13 linhas existentes foram reescritas manualmente pra "ANA" (só o rótulo mudou, níveis/vazão idênticos), a pedido do usuário.
- **Achado maior: `monitor_web.log` era público e vazava a URL da Copel.** Descoberto que esse arquivo (pensado como log interno) era commitado junto com `data.json`/`historico_diario.csv` a cada execução do GitHub Actions e, por estar na raiz do repo, ficava acessível direto em `rioiguacu.com/monitor_web.log` — centenas de linhas citando "Copel" e a URL exata do scraping. `.github/workflows/update.yml`: `monitor_web.log` removido do `git add` (continua sendo escrito no runner, só parou de ser publicado). O histórico já publicado antes desta versão não foi apagado retroativamente (decisão do usuário).
- **Achado crítico relacionado, ainda em aberto:** `rioiguacu.com/CLAUDE.md` também está publicamente acessível, incluindo o CPF do usuário — o Cloudflare Pages está servindo o repositório GitHub inteiro (sem "Build output directory" configurado), não só os arquivos do site. Confirmado que `_headers`/`_redirects` do Cloudflare Pages não conseguem bloquear/dar 404 num arquivo específico. Correção real (mover arquivos públicos pra uma subpasta `public/` e configurar essa subpasta como build output no painel do Cloudflare) ainda não implementada — pendente de confirmação do usuário, documentado em detalhe no `CLAUDE.md`.
- **Corrigido bug de CSS no `.safety-warning` (o aviso "Enchente é risco à vida") introduzido na v1.72, reportado pelo usuário ao ver o layout quebrado no celular.** A regra `max-width: calc(100% - 374px)` foi adicionada como bloco incondicional (fora de `@media`) DEPOIS, no arquivo, do bloco `@media (max-width: 1120px)` que tentava resetá-la para `max-width: none` no mobile — como as duas regras têm a mesma especificidade, o CSS resolve o empate pela ordem de origem, e a regra incondicional (por vir depois) sempre vencia, mesmo em telas estreitas. Numa tela de ~390px, `calc(100% - 374px)` dá um valor próximo de zero/negativo, espremendo o bloco. `styles.css`: a regra de reset para `max-width: none` foi movida pra depois da regra base, dentro de um novo bloco `@media (max-width: 1120px)` no final do arquivo.
- Cache-buster de `styles.css` atualizado para `?v=1.73` em `index.html`.
- Backup pré-edição: `backups/site-v1.72.zip`.

## v1.72 — 2026-07-20

- **Ajustada a largura do aviso de segurança** ("⚠️ Enchente é risco à vida. Leia com atenção.") — antes esticava até a largura total do `.shell` (bem mais largo que o resto do conteúdo abaixo dele), agora fica com a mesma largura da coluna do FAQ/gráfico/histórico em `.main-grid` (a coluna da esquerda, sem contar os 360px + 14px de gap reservados pro painel lateral). Pedido do usuário: "MANTENHA O TAMANHO DO BLOCO ANTERIOR PERGUNTAS FREQUENTES". `styles.css`: `.safety-warning` ganhou `max-width: calc(100% - 374px)`, revertido pra `max-width: none` no breakpoint `max-width: 1120px` (onde o `.main-grid` já vira coluna única de 100%).
- Cache-buster de `styles.css` e `app.js` atualizado para `?v=1.72`.
- Backup pré-edição: `backups/site-v1.71.zip`.

## v1.71 — 2026-07-20

- **Removida a linha "Fonte desta atualização: ANA"** do subtítulo do cabeçalho (`#sourceNote`) — usuário apontou que ficou redundante com a frase logo acima, que já diz "com dados da ANA (Agência Nacional de Águas e Saneamento Básico)". `app.js`: `renderCards()` agora sempre limpa `#sourceNote` em vez de preenchê-lo; o rótulo `(ANA)` ao lado de "Dados Visíveis" (`#sourceLabel`) não foi tocado, continua mostrando a fonte igual antes.
- **Motivo real por trás da remoção das referências a "Copel" (v1.69/v1.70), esclarecido pelo usuário nesta sessão:** o projeto não tem autorização da Copel para divulgar publicamente que os dados vêm dela — não é só uma simplificação visual. A coleta técnica continua normalmente (usuário confirmou explicitamente "vamos manter a coleta"); só a exibição pública nunca deve nomear a Copel. Documentado como PRIORIDADE 1 no `CLAUDE.md` pra nenhuma sessão futura reverter isso sem confirmar que a autorização mudou.
- **Removido o link "Abrir fonte"** da seção "Dados Visíveis" (`#sourceLink` em `index.html`, atribuição de `.href` removida do `app.js`) — o link usava `data.url_historico`, que às vezes apontava pra URL real da Copel (`bacia-iguacu.jsf`), a mesma questão de autorização acima.
- **Achado adicional (a pedido do usuário, "procure se existe mais algum link que direcione para copel.com"):** o campo `url_historico` do `data.json` público (gerado por `scrape.py`) continuava gravando a URL real da Copel quando essa era a fonte da leitura, mesmo sem link visível na página — um visitante que abrisse `rioiguacu.com/data.json` diretamente ainda veria isso no JSON cru. Corrigido em `scrape.py`: `url_historico` agora sempre resolve para `URL_HISTORICO_ANA`, nunca `URL_HISTORICO_COPEL`, independentemente da fonte técnica real da leitura — mesma lógica já aplicada ao campo `fonte` exibido no frontend.
- **Removido "· próxima atualização às HH:MM" do status de sincronização** (`#syncStatus`, rodapé do gráfico) — a pedido do usuário. Agora mostra só "Atualizado em DD/MM, HH:MM" (ou "... · previsão indisponível" no caso de aviso), sem a estimativa da próxima atualização.
- Cache-buster de `styles.css` e `app.js` atualizado para `?v=1.71`.
- Backup pré-edição: `backups/site-v1.70.zip`.

## v1.70 — 2026-07-20

- **Corrigido vazamento de "Copel" que a v1.69 tinha deixado passar.** A v1.69 removeu as referências a Copel do `index.html`/`app.js` (frontend), mas o texto "Previsão da Copel para daqui a X horas (...): Y m..." exibido no card de Tendência (`#forecastAlert`) vem pronto do `data.json`, gerado pela função `verificar_alerta_previsao()` em `scrape.py` — esse arquivo não tinha sido revisado na v1.69. Usuário reportou o vazamento ao ver o texto ao vivo.
  - `scrape.py`: as 3 strings retornadas por `verificar_alerta_previsao()` deixaram de citar "Copel" — "Sem previsão da Copel disponível..." → "Sem previsão disponível..."; "Previsão da Copel para daqui a X horas..." → "Previsão para daqui a X horas...". Nenhuma outra fonte é citada no lugar (nem "concessionária", nem link) — mesma decisão da v1.69, sem nome e sem descrição indireta.
  - Demais ocorrências de "Copel" em `scrape.py` (comentários de código, mensagens de log em `monitor_web.log`, a constante interna `FONTE_COPEL`) não são exibidas a visitantes do site e foram mantidas — a constante `FONTE_COPEL` já é convertida para "ANA" na exibição pelo `app.js` (v1.69).
  - `app.py` (monitor local, roda só na máquina do usuário via `abrir_monitor_web.bat` — não é o site público) também cita Copel (fonte fixa, sem integração com a ANA); não foi alterado por não ser "parte visual do site" público, mas fica registrado aqui caso o usuário queira revisar depois.
  - O `data.json` ao vivo ainda vai mostrar o texto antigo até a próxima execução do `scrape.py` via GitHub Actions (dispara a cada ~5 min pelo Worker `rioiguacu-trigger`) — corrige sozinho, sem ação manual.
- Backup pré-edição: `backups/site-v1.69.zip`.

## v1.69 — 2026-07-20

- **Removidas as referências visuais a "Copel" no site**, a pedido explícito do usuário. Antes o site distinguia visualmente quando o nível atual vinha da ANA ou da Copel (fonte redundante, usada nos raros minutos em que a ANA ainda não publicou a leitura da hora); agora a exibição sempre mostra "ANA", independentemente de qual das duas foi a fonte técnica real da leitura — decisão do usuário, que observou que a Copel também capta da mesma estação física, então não há diferença de fundo na leitura em si, só na origem da publicação.
  - `app.js`: `renderCards()` agora mapeia `fonteCurta === "copel"` para exibir "ANA" tanto no rótulo `(fonte)` ao lado de "Dados Visíveis" quanto na nota "Fonte desta atualização: ...". A lógica de detecção da fonte técnica real (vinda de `data.fonte`, gerado pelo `scrape.py`) não foi alterada — só a exibição.
  - `index.html`: meta description, `og:description`, `twitter:description` e a descrição do schema.org JSON-LD deixaram de citar "e da Copel", citando só a ANA.
  - `index.html`, FAQ "De onde vêm os dados do site?": removida a frase sobre a Copel como fonte redundante do nível atual. O parágrafo sobre a **previsão de 48 horas** — que é um produto genuinamente da Copel (concessionária que opera as usinas, não a ANA) — deixou de citar qualquer fonte: nem "Copel" nem descrição indireta ("concessionária que opera as usinas"), e o link para o painel `copel.com` foi removido. O texto agora só diz que a previsão "não é um cálculo feito por este site, mas também não é um alerta oficial da Defesa Civil" — decisão explícita do usuário (sem nome, sem descrição, sem link).
- Cache-buster de `styles.css` e `app.js` atualizado para `?v=1.69`.
- Backup pré-edição: `backups/site-v1.68.zip`.

## v1.68 — 2026-07-20

- **Reorganizado o rodapé**: o usuário achou que "ficou tudo misturado" com o link de contato na mesma linha da versão/contador/status de sincronização. Agora o contato fica em uma linha própria, acima, com o texto "Sugestões ou críticas? Fale conosco" (antes só "Fale conosco"). A linha de baixo (versão, contador de visitas, status de sincronização) foi agrupada em `<div class="footer-status">`. `styles.css`: `.version-footer` virou `flex-direction: column`; nova classe `.footer-status` mantém o layout horizontal da linha de baixo.
- Cache-buster de `styles.css` e `app.js` atualizado para `?v=1.68`.
- Backup pré-edição: `backups/site-v1.67.zip`.

## v1.67 — 2026-07-20

- **Adicionado link de contato no rodapé** ("Fale conosco", `mailto:contato@rioiguacu.com`), a pedido do usuário, como canal de feedback simples. `contato@rioiguacu.com` foi configurado no Cloudflare Email Routing (domínio já gerenciado pelo Cloudflare), encaminhando para o email pessoal do usuário — confirmado funcionando (email de teste chegou, inicialmente na pasta de spam do Gmail). Avaliada e descartada, a pedido do usuário, a alternativa de um formulário embutido no site (exigiria um novo Cloudflare Worker com envio de email); optou-se pela solução mais simples.
- Cache-buster de `styles.css` e `app.js` atualizado para `?v=1.67`.
- Backup pré-edição: `backups/site-v1.66.zip`.

## v1.66 — 2026-07-19

- Removido "(18 dos 96 anos)" do título do nível "Grande enchente" na FAQ "O que significa cada nível?", a pedido do usuário — título ficou "Grande enchente — 6,50 m · menos de 1% dos dias da história."
- Cache-buster de `styles.css` e `app.js` atualizado para `?v=1.66`.
- Backup pré-edição: `backups/site-v1.65.zip`.

## v1.65 — 2026-07-19

- **Correção da v1.64: o texto da previsão não afirma mais "48 horas" quando a Copel não previu tão longe.** O usuário perguntou "mas existe o dado 48h depois?" — conferindo o `data.json` ao vivo, a resposta era não: a previsão publicada pela Copel naquele momento ia só até 35h à frente (não 48h). `verificar_alerta_previsao()` em `scrape.py` agora calcula e mostra o número real de horas entre agora e o ponto de previsão usado (`round((data_hora_ponto - agora_base).total_seconds() / 3600)`), em vez de sempre dizer "48 horas". Texto mudou de "Previsão da Copel para daqui a 48 horas (dd/mm HHh): X m" para "Previsão da Copel para daqui a N horas (dd/mm HHh): X m", onde N reflete a distância real do ponto de previsão mais próximo do alvo de 48h. Roda em GitHub Actions, então só aparece a partir da próxima coleta automática.
- Cache-buster de `styles.css` e `app.js` atualizado para `?v=1.65`.
- Backup pré-edição: `backups/site-v1.64.zip`.

## v1.64 — 2026-07-19

- **"Previsão da Copel" na Tendência agora mostra o valor real de daqui a 48h, não o pico da janela inteira**, a pedido do usuário (ele notou que, com o rio em queda, o texto mostrava 3,74 m — o pico bem no início da janela — enquanto o gráfico já apontava 3,52 m bem mais adiante, e achou confuso). `scrape.py`, `verificar_alerta_previsao()`: em vez de `max()` de todos os valores previstos nas próximas 48h, agora busca o ponto de previsão mais próximo do horário exatamente 48h à frente (a previsão da Copel nem sempre cai certinho em cima da marca), usa o cenário "com chuva" quando disponível (mesmo cenário que a linha vermelha "Previsão" do gráfico usa) e mostra também o horário exato desse ponto. Texto mudou de "Previsão da Copel para as próximas 48 horas: X m" para "Previsão da Copel para daqui a 48 horas (dd/mm HHh): X m". Como roda em GitHub Actions, o texto novo só aparece a partir da próxima coleta automática.
- **Reestruturado o parágrafo "O que significa cada nível?"**: a linha-resumo de percentuais adicionada na v1.62 ficou "estranha separada" do resto (segundo o usuário) — removida como parágrafo próprio, e cada percentual movido para dentro do título de cada nível (ex.: "Atenção — 4,20 m · 10% dos dias da história."), eliminando a repetição que havia entre a linha-resumo e o corpo de cada parágrafo.
- Cache-buster de `styles.css` e `app.js` atualizado para `?v=1.64`.
- Backup pré-edição: `backups/site-v1.63.zip`.

## v1.63 — 2026-07-19

- **Notas de rodapé de "Referências por Bairro*" e "Enchentes Históricas*" transformadas em campos colapsáveis** (`<details>`/`<summary>`), a pedido do usuário, pra reduzir a quantidade de texto visível na tela por padrão. Antes eram parágrafos sempre visíveis; agora aparecem fechados, com um resumo clicável ("Como interpretar esta lista" / "Sobre esta lista") e abrem sob demanda.
- `styles.css`: nova regra `.reference-note summary`/`.reference-note[open]` (mesmo padrão visual — seta ▸ que gira 90° — já usado em `.faq-item details`), e o texto passou de `.reference-note` diretamente para `.reference-note p`.
- A nota da terceira caixa ("Alertas de Nível do Rio*") não foi alterada — é uma linha só, sem necessidade de recolher.
- Cache-buster de `styles.css` e `app.js` atualizado para `?v=1.63`.
- Backup pré-edição: `backups/site-v1.62.zip`.

## v1.62 — 2026-07-19

- **Nível de alerta "Enchente" renomeado para "Grande enchente" em todo o site**, a pedido do usuário. Alterado em três lugares para manter consistência:
  - `scrape.py`: `COTAS_ALERTA_DEFESA_CIVIL` — `(6.50, "ENCHENTE")` → `(6.50, "GRANDE ENCHENTE")`. Esse valor alimenta tanto o campo `situacao` (badge do card "Nível atual do rio") quanto a lista "Alertas de Nível do Rio" da lateral, via `data.json`. Roda em GitHub Actions, então o novo rótulo passa a valer a partir da próxima coleta automática.
  - `app.js`: `severityClass()` — a checagem `texto.startsWith("ENCHENTE")` (usada para aplicar a classe `badge-critico`, com o ícone de sirene) foi atualizada para `texto.startsWith("GRANDE ENCHENTE")`, senão o badge pararia de receber o estilo crítico.
  - `index.html`: parágrafo da FAQ "O que significa cada nível?" renomeado de "Enchente — 6,50 m" para "Grande enchente — 6,50 m".
- **Acrescentada uma linha-resumo no início da resposta "O que significa cada nível?"**, mostrando de forma compacta a progressão de raridade dos 5 níveis (15% → 10% → 5% → 2,5% → menos de 1%), antes dos parágrafos detalhados de cada um.
- **Fora do escopo desta mudança, mantido de propósito:** os rótulos "Enchentes Históricas" (lista lateral) e "Enchente de 1983/1992/2014/2019/2023" (`COTAS_BAIRROS`) não foram alterados — descrevem eventos históricos específicos, não o nível de alerta em si, e continuam corretos como estão.
- Cache-buster de `styles.css` e `app.js` atualizado para `?v=1.62`.
- Backup pré-edição: `backups/site-v1.61.zip`.

## v1.61 — 2026-07-19

- **Escala do gauge de nível ("Nível atual do rio") alterada de 0–6,50 m para 1,30–6,50 m**, a pedido do usuário. O piso passou a ser o mínimo histórico já registrado (1,30 m, em 2020), em vez de zero — o rio nunca opera perto de zero, então a nova faixa aproveita melhor o espaço visual do gauge para a variação real do nível. Alterado em `app.js`: nova constante `NIVEL_MIN_ESCALA = 1.3`, ajuste do primeiro degrau de cor em `colorForLevel()` e da fórmula de posição do marcador em `renderCards()` (antes `level / NIVEL_MAX_ESCALA`, agora `(level - NIVEL_MIN_ESCALA) / (NIVEL_MAX_ESCALA - NIVEL_MIN_ESCALA)`).
- **Revisão de texto nos parágrafos "Atenção", "Alerta" e "Emergência"** da pergunta "O que significa cada nível?" (`index.html`), a pedido do usuário:
  - Atenção (4,20 m): removido o termo solto "percentil 90" (sem lastro estatístico no parágrafo, ao contrário de Observação/Alerta que citam desvios padrão explicitamente) e a frase sobre subida de "3 metros em 48 horas" (não fazia sentido no contexto). Texto agora afirma diretamente: "o rio esteve neste nível ou acima em apenas 10% dos dias da história."
  - Alerta (5,00 m): "1 dia em cada 20" trocado por "5%"; removida a frase sobre a maior subida diária (1,78 m/24h, 1992) para não duplicar/deslocar o dado sem contexto.
  - Emergência (5,50 m): "1 dia a cada 40" trocado por "2,5%"; acrescentada a informação de que, neste nível, alguns bairros já apresentam vários pontos de alagamento (deixa de ser um atingimento pontual).
- Cache-buster de `styles.css` e `app.js` atualizado para `?v=1.61`.
- Backup pré-edição: `backups/site-v1.60.zip`.

## v1.60 — 2026-07-19

- **PDF do artigo científico readicionado a `estudo.html`, com autorização explícita do usuário**, sendo esta a cópia definitiva a ser usada (`4c7d560c2f665f5a877284c14073c24f`, 21 páginas, correções ABNT).
- **Mantido o nome de arquivo original enviado pelo usuário** — `NOTA_TECNICA_MONITORAMENTO_CHEIAS_UV_ABNT.pdf` — em vez de renomear para o genérico `artigo-cientifico-uv.pdf` usado nas versões anteriores. O código de `estudo.html` (`pdfjsLib.getDocument(...)`) foi atualizado para buscar esse nome exato.
- Visualizador restaurado exatamente na versão funcional da v1.58 (rolagem contínua tipo livro, renderização lazy por página via `IntersectionObserver`, sem travamento).
- Cache-buster do PDF em `?v=1.60`.
- Backup pré-edição: `backups/site-v1.59.zip`.

## v1.59 — 2026-07-19

- **PDF do artigo científico removido de `estudo.html`, a pedido explícito do usuário**, junto com todo indício dele: o arquivo `artigo-cientifico-uv.pdf` foi apagado do repositório, o script do `pdf.js` (biblioteca externa) foi removido, e o `<div class="pdf-viewer-wrap">`/`carregarPdfEspecialistas()` (HTML, CSS e JS relacionados ao visualizador) foram excluídos por completo — não sobra mais nenhuma referência a PDF em `estudo.html`.
- O lado "Para especialistas" agora mostra apenas o título e uma mensagem simples: "Esta seção está em revisão no momento. O artigo técnico completo será republicado em breve." O lado "Para o público" não foi alterado.
- **Motivo:** apesar da correção de cache da v1.58, o usuário reportou que o problema persistia; decidiu remover o PDF do ar por enquanto e reenviá-lo (com autorização explícita de publicação) numa próxima etapa.
- Backup pré-edição: `backups/site-v1.58.zip` (inclui o PDF de 21 páginas com correções ABNT, para restauração caso o usuário reenvie o mesmo arquivo).

## v1.58 — 2026-07-19

- **Causa real do "aparecem só 13/20 páginas" identificada:** não era mais o travamento (corrigido na v1.55) — era **cache do navegador**. O `pdf.js` buscava sempre a mesma URL fixa `artigo-cientifico-uv.pdf`, sem parâmetro de versão; quando o conteúdo do arquivo mudou (v1.57), navegadores que já tinham aberto `estudo.html` antes continuaram servindo a cópia antiga do PDF do cache local, mesmo com o arquivo novo já publicado no GitHub/Cloudflare (confirmado buscando o arquivo ao vivo direto por HTTP, sem passar pelo navegador: o conteúdo publicado sempre esteve correto, 21 páginas, "Nota Técnica — Versão 1.3").
- **Correção:** a chamada `pdfjsLib.getDocument(...)` agora usa `artigo-cientifico-uv.pdf?v=1.58`, com o número de versão do site como cache-buster. A cada futura substituição do PDF, o parâmetro de versão deve ser incrementado junto — do contrário, o mesmo problema se repete.
- **Novo arquivo do artigo** (já publicado na v1.57): correções de formatação ABNT enviadas pelo usuário. 21 páginas A4, mesmo título e autoria da versão anterior.
- Backup pré-edição: `backups/site-v1.57.zip`.

## v1.57 — 2026-07-19

- **Substituído `artigo-cientifico-uv.pdf` pela versão corrigida enviada pelo usuário** (correções de formatação ABNT). Novo arquivo enviado como `NOTA_TECNICA_MONITORAMENTO_CHEIAS_UV_ABNT.pdf`, publicado no repositório com o mesmo nome de sempre (`artigo-cientifico-uv.pdf`), sem necessidade de alterar `estudo.html` — só o conteúdo do PDF muda. 21 páginas A4 (era 20 na versão anterior), mesmo título e autoria, texto extraído confere com o artigo já usado.
- Backup pré-edição: `backups/site-v1.56.zip` (contém a versão anterior do PDF, 20 páginas, para rollback se necessário).

## v1.56 — 2026-07-19

- **Adicionado `data-nosnippet` aos blocos de dados que mudam a cada 5 minutos em `index.html`**, a pedido do usuário: o Google estava usando esses números (vazão, chuva, tendência, régua) no trecho de resultado de busca (snippet), e como o snippet é indexado/atualizado com atraso, alguém que só lê a busca sem entrar no site podia ver um número de horas/dias atrás pensando que era o valor atual — risco real de confusão numa situação de enchente. `data-nosnippet` sinaliza ao Google para não usar aquele trecho no texto do resultado de busca (não afeta o SEO/ranking da página, só o que aparece como preview).
- **Elementos marcados:** o card "Nível atual do rio" (`article.level-card`), o card combinado de Vazão/Chuva (`article.metric-card.metric-split`), o card de Tendência (`article.metric-card`) e o painel expansível "Dados Visíveis" (linhas de leitura recente na tabela).
- **Ajuste em relação ao pedido original:** o usuário sugeriu aplicar em `section.table-panel.depth`, mas essa classe já não existe — o site evoluiu desde a versão em que ela existia (confirmado comparando com uma versão em cache de `raw.githubusercontent.com`, sem cachebust, que ainda mostrava a v1.17). Na versão atual (v1.50), a seção equivalente é `section.tabs-panel.depth` — só que ela contém, além da tabela de leituras recentes, o Ranking Sazonal e a lista de Enchentes Históricas, que são conteúdo estático e útil pro SEO (documentado como importante desde a v1.25). Marcar a seção inteira excluiria esse conteúdo bom do snippet junto com o dado que muda. Por isso, o `data-nosnippet` foi aplicado só no `<details>` "Dados Visíveis" (que é, de fato, a tabela com os dados que mudam a cada coleta), preservando o resto.
- Backup pré-edição: `backups/site-v1.55.zip`.
- **Pendente, não incluído nesta versão:** as sugestões de reescrever `<title>`/`<meta description>` com termos como "hoje", "cota", "vazão", "régua" e "48h" — não aplicadas ainda porque o site já ranqueia em 1º lugar no Google pra "nível do rio iguaçu hoje união da vitória" e termos parecidos (confirmado antes da v1.25, quando o title/description foram deixados intactos por esse motivo). Fica como decisão a confirmar com o usuário antes de mexer nesses dois campos especificamente.

## v1.55 — 2026-07-19

- **Corrigido o travamento do visualizador de PDF em `estudo.html`** (relatado pelo usuário: a página parava de responder e só cerca de 13 das 20 páginas chegavam a aparecer). Causa raiz: a v1.54 disparava a renderização de todas as 20 páginas do PDF em `<canvas>` simultaneamente, em escala alta (até 2,5× `devicePixelRatio`×1,4) — trabalho pesado demais de uma vez para a thread principal do navegador.
- **Correção do arquivo verificada:** o `artigo-cientifico-uv.pdf` publicado no repositório foi conferido byte a byte (`md5sum`) contra o arquivo mais recente enviado pelo usuário — são idênticos, 20 páginas, 244 KB. O problema nunca foi o arquivo estar errado/truncado; era o travamento cortando o carregamento visual no meio.
- **Novo comportamento, a pedido do usuário ("rolagem igual livro"):** as 20 páginas agora ficam empilhadas dentro de uma área de rolagem contínua (`#pdfViewerBook`, altura máx. 85vh), cada uma com espaço reservado no layout (proporção A4 fixa via `aspect-ratio`) desde o início, para não haver salto de página enquanto carrega. A renderização de cada página só acontece quando ela se aproxima da área visível (via `IntersectionObserver`, com margem de 600px), uma de cada vez em fila — em vez de todas de uma vez.
- Removida também a caixa de metadados acima do visualizador ("Artigo científico — formatação ABNT (PDF)... Responsável: Thiago Jorge Iwanko...") do lado "Para especialistas", a pedido do usuário — ficou só o título `<h1>` acima do visualizador.
- CSS de navegação por botões (Anterior/Próxima), de uma tentativa intermediária descartada em favor da rolagem contínua, removido por não ter mais markup correspondente.
- Backup pré-edição: `backups/site-v1.54.zip` (reconstrói o estado ao vivo real da v1.54, que já estava travando — a v1.54 nunca tinha recebido esse backup formalmente).

## v1.54 — 2026-07-19

- **Lado "Para especialistas" de `estudo.html` substituído por um visualizador de PDF embutido**, a pedido do usuário: agora mostra o artigo científico em formatação ABNT (`artigo-cientifico-uv.pdf`, 20 páginas, fornecido pelo usuário), publicado na raiz do repositório, em vez do texto em HTML usado nas v1.51–v1.53.
- **Implementação:** biblioteca `pdf.js` (cdnjs, v3.11.174) renderiza cada página do PDF num `<canvas>`, empilhados verticalmente dentro de `estudo.html` — não é um `<iframe>`/`<embed>` com o visualizador nativo do navegador, justamente para não expor o botão de download/impressão que os visualizadores nativos (Chrome, Edge, Safari) mostram por padrão. Carregamento em modo lazy: o PDF só é buscado e renderizado no primeiro clique em "Para especialistas", não no carregamento da página.
- **Bloqueio de download:** clique direito desabilitado sobre a área do visualizador (`oncontextmenu="return false"`) e nenhum link direto para o arquivo em nenhum lugar da página. **Ressalva importante, documentada aqui para transparência:** como o arquivo `artigo-cientifico-uv.pdf` precisa ficar publicamente acessível na mesma origem para o `pdf.js` conseguir buscá-lo, não existe bloqueio de download 100% à prova de tudo em um site estático sem backend/autenticação — alguém com conhecimento técnico (aba de rede do navegador, view-source) ainda consegue obter o arquivo. O que foi implementado é a barreira de interface padrão (sem botão de download visível, sem menu de contexto, sem visualizador nativo com toolbar) — não uma proteção criptográfica ou de acesso.
- Removida a caixa de metadados do lado "Para o público" ("Guia para a população e a imprensa · Versão 1.1..."), a pedido do usuário.
- Novo arquivo estático no repositório: `artigo-cientifico-uv.pdf` (244 KB, 20 páginas A4, formatação ABNT).
- Backup pré-edição: `backups/site-v1.53.zip`.

## v1.53 — 2026-07-19

- **Recuo de primeira linha (`text-indent`) adicionado aos parágrafos de `estudo.html`**, a pedido do usuário ("vi que não tem espaçamento inicial nos parágrafos") — formatação de artigo tradicional, aplicada aos dois lados (Para o público e Para especialistas), já que ambos usam a mesma classe `.article p`. Excluído do recuo o bloco de metadados (`.article-meta`), o resumo (`.abstract p`), as palavras-chave (`.keywords`) e a nota final (`.note-final`), que continuam sem recuo por não serem parágrafos de corpo de texto corrido.
- Backup pré-edição: `backups/site-v1.52.zip`.

## v1.52 — 2026-07-19

- **Conteúdo do lado "Para o público" de `estudo.html` substituído por uma nova versão**, fornecida pelo usuário em `ESTUDO_VERSAO_POPULAR.docx` (revisão do texto da v1.51). Principais mudanças de conteúdo:
- Aviso explícito adicionado: "os nomes abaixo são categorias informacionais próprias do rioiguacu.com. Eles não representam decreto, alerta ou ordem oficial da Defesa Civil."
- Novo parágrafo com a probabilidade condicional de 48h documentada no artigo técnico (21 casos históricos de nível 5,00–5,50 m subindo ≥0,5 m/dia; 76% atingiram 5,50 m em até 48h), com ressalva explícita de que não é previsão do evento atual.
- Novo parágrafo sobre a tendência de intensificação (30% dos anos com pico ≥5,50 m em 1931–1977 vs. 58% em 1978–2025, estatisticamente significativa, sem atribuição de causa).
- Parágrafo sobre limitação do modelo reforçado: "O site identifica terrenos abaixo de uma linha d'água teórica — não o caminho real da água" (antes: "mostra até onde a água 'alcança'... não por onde ela vai passar"), deixando mais explícito que terreno abaixo da linha é exposição potencial, não garantia de alagamento.
- Novo parágrafo sobre a pendência de nivelamento topográfico formal entre o zero da régua e o modelo de terreno (já documentada tecnicamente no artigo científico desde a v1.51, agora também exposta na versão popular).
- Recomendação a jornalistas sobre cotas de bairro reformulada para deixar explícito que a cota é do terreno, não da soleira/piso da casa.
- Removido o parágrafo introdutório genérico ("Este texto explica, em linguagem simples...") — a nova versão vai direto ao conteúdo.
- O lado "Para especialistas" (artigo científico) e a estrutura/estilo geral da página não foram alterados nesta versão.
- Backup pré-edição: `backups/site-v1.51.zip`.

## v1.51 — 2026-07-19

- **Nova página `estudo.html`, substituindo o placeholder "Em breve"** (existente desde a v1.44/v1.45): agora tem conteúdo real, com um seletor no topo com duas opções — **"Para o público"** e **"Para especialistas"** (nomes escolhidos pelo usuário entre as opções propostas, no lugar de "leigos").
- **"Para o público"**: guia em linguagem simples para a população e a imprensa, conteúdo fornecido pelo usuário (`ESTUDO_VERSAO_POPULAR_IMPRENSA.md`) — explica de onde vêm os números do site, como os níveis de alerta foram definidos, os cuidados que o leitor deve ter com as cotas de bairro, o papel da Defesa Civil e recomendações específicas para jornalistas que forem citar os dados.
- **"Para especialistas"**: artigo científico completo, conteúdo fornecido pelo usuário (`ARTIGO_CIENTIFICO_MONITORAMENTO_CHEIAS_UV_1.md`) — método estatístico-geoespacial (análise de frequência por Gumbel/GEV e L-momentos, teste de tendência de Mann-Kendall, dinâmica de subidas/recessões, exposição urbana por comparação altimétrica), verificação frente a práticas de referência (USGS Bulletin 17C, Flood Estimation Handbook, WMO, Diretiva europeia de inundações), resultados, discussão, limitações e agenda de evolução em 3 camadas, com lista de referências.
- **Texto do artigo técnico justificado (`text-align: justify`) e organizado em layout de artigo científico** (título, bloco de metadados, resumo destacado, palavras-chave, seções numeradas, tabela de resultados, lista de referências em fonte menor), a pedido explícito do usuário ("o texto precisa ser justificado, e organizado o layout como artigo") — implementado via bloco `<style>` próprio dentro de `estudo.html`, sem alterar o `styles.css` compartilhado do resto do site.
- Alternância entre as duas visões via pequeno script inline em `estudo.html` (não depende de `app.js`), reaproveitando as classes já existentes `.tabs-nav`/`.tab-btn`/`.tab-btn.active` do restante do site para o seletor.
- Nenhuma mudança em `index.html` — o link já existente no FAQ ("Quer entender a fundo? Veja de onde vêm os dados →", adicionado na v1.45) já apontava corretamente para `estudo.html`.
- Backup pré-edição: `backups/site-v1.50.zip`.

## v1.50 — 2026-07-19

- **Correção definitiva do alinhamento entre as duas tabelas do "Ranking Sazonal"**, depois que a v1.49 (baseada só em `min-height` chutado) não resolveu em telas mais estreitas — usuário reportou de volta com print mostrando o degrau ainda presente. Causa raiz: `min-height` era um valor fixo estimado pra "no máximo 2 linhas", mas em janelas mais estreitas o subtítulo mais longo ("Só as grandes enchentes...") passou a quebrar em mais linhas do que isso reservava.
- **Solução estrutural**: o HTML das duas colunas foi achatado (removidos os `<div>` que agrupavam cada subtítulo+tabela) e agora os 4 elementos (2 subtítulos, 2 tabelas) são filhos diretos do `.ranking-grid`, com a ordem visual controlada por `order` no CSS — isso faz o CSS Grid tratá-los como uma grade de verdade com 2 linhas (subtítulos na linha 1, tabelas na linha 2), onde cada linha se ajusta automaticamente à altura do maior conteúdo. Funciona em qualquer largura de tela, sem precisar estimar altura em `em`/`px`. A ordem no HTML continua a ordem natural de leitura (subtítulo 1, tabela 1, subtítulo 2, tabela 2), preservada no mobile via reset do `order` na media query — só o desktop reorganiza visualmente em 2 linhas.
- Backup pré-edição: `backups/site-v1.49.zip`.

## v1.49 — 2026-07-18/19

- **Subtítulo "Só as grandes enchentes" corrigido de "1930–07/2026" para "1930–2025"**, alinhando com o formato do outro subtítulo ("Todos os anos... 1930–2025") — pedido do usuário. O período de 2026 nunca teve nenhum episódio de enchente registrado na tabela, então a mudança não altera nenhum dado, só o rótulo.
- **Texto "cheia de 10 anos" removido do mesmo subtítulo** (ficou só "nível ≥ 6,89 m", como em todos os outros lugares do site), encurtando a linha o suficiente pra evitar quebra em 2 linhas na maioria das telas.
- **Corrigido o "degrau" entre as duas mini-tabelas do Ranking Sazonal**, reportado pelo usuário com print: quando um dos dois subtítulos quebrava em 2 linhas e o outro ficava em 1, a tabela de baixo começava em alturas diferentes. Adicionado `min-height` no CSS (`.ranking-grid > div > p.subtitle`) reservando o mesmo espaço vertical pros dois subtítulos, independente de quantas linhas o texto ocupar — removido no mobile (coluna única, onde o alinhamento lado a lado não se aplica).
- Backup pré-edição: `backups/site-v1.48.zip`.

## v1.48 — 2026-07-18

Ajustes de clareza no texto visível, a partir de uma revisão pedida pelo usuário ("analise o texto, visível, se nao esta confuso"):

- **Ordem invertida no quadro lateral**: "Referências por Bairro*" passou a vir antes de "Enchentes Históricas*" (pedido do usuário na sessão anterior, ainda pendente).
- **Nome de aviso "Atualizado em... · próxima atualização às..." movido do cabeçalho para o rodapé**, na mesma linha da versão e do contador de visitas — antes ficava isolado no topo, junto com o título.
- **Acordeão "Enchentes Históricas (nível ≥ 6,89 m)" renomeado para "Mais detalhes sobre as Enchentes Históricas"**, dentro de "Dados e Histórico" — corrige a confusão de ter dois elementos com o mesmo nome na página (o quadro lateral resumido e essa tabela completa com 12 episódios, datas e duração). Subtítulo também reescrito pra descrever melhor o conteúdo da tabela.
- **FAQ "Fontes" removido, consolidado dentro de "De onde vêm os dados do site?"**: as duas perguntas cobriam basicamente a mesma informação em formatos diferentes (uma em prosa, outra em bloco técnico denso), dando a impressão de resposta duplicada. Os fatos que só apareciam em "Fontes" (período exato de cada estação — fluviométrica até 2023, telemétrica desde 2024 — e a nota de que os cálculos são reproduzíveis a partir das bases públicas) foram incorporados ao parágrafo "Nível do rio". O dado do zero da régua (739,61 m) não foi duplicado aqui porque já está explicado em "O que é o 'nível de régua'?".
- **Novo parágrafo "Previsão de 48 horas" na mesma pergunta**, com link para o painel de Monitoramento Hidrológico da Copel (`copel.com/mhbweb/paginas/previsao.jsf`) — corrige uma atribuição incompleta: o número de 48h mostrado no site (no gráfico e no card Tendência) sempre veio direto da previsão publicada pela própria Copel, não de um cálculo deste site. O texto anterior ("Estimativa automática... Não é uma previsão oficial") dava a entender o contrário.
- **Mesma correção de atribuição no backend (`scrape.py`)**: `verificar_alerta_previsao()` agora retorna "Previsão da Copel para as próximas 48 horas: X m. Não é um alerta oficial da Defesa Civil." em vez de "Estimativa automática... Não é uma previsão oficial."
- **Subtítulos das duas tabelas do "Ranking Sazonal" reescritos** com o diferencial em negrito logo no início ("Todos os anos" vs. "Só as grandes enchentes") — antes as duas começavam com "Em que mês..." e eram fáceis de confundir numa leitura rápida, já que os números de outubro lideram nas duas.
- Backup pré-edição: `backups/site-v1.47.zip`.

## v1.47 — 2026-07-18

- **Corrigido espaço vazio abaixo do gráfico**, reportado pelo usuário ("vc consegue perceber o espaço vazio que ficou abaixo do grafico?"). Causa: desde a v1.46 (item 2), a coluna direita (`.side-panel`) passou a ter 3 quadros empilhados (Enchentes Históricas, Referências por Bairro, Alertas), ficando bem mais alta que a coluna esquerda (só o card do gráfico) — sobrava um vão grande abaixo do gráfico.
- **Solução**: `.main-grid` reestruturado com `grid-template-areas`, movendo as seções "Dados e Histórico" e "Perguntas frequentes" para dentro da coluna esquerda, empilhadas abaixo do gráfico (`chart` → `history` → `faq`), com `.side-panel` ocupando as 3 linhas à direita (`side`). No mobile (`max-width: 1120px`), a ordem de empilhamento vira gráfico → side-panel → histórico → FAQ. Pedido do usuário: "reduza para que caiba ali a parte dados historicos e perguntas frequentes".
- Nenhuma mudança de conteúdo/dados — só reposicionamento via CSS Grid e ajuste da estrutura de `<section>` no `index.html` (as duas seções passaram a ser filhas diretas de `.main-grid`, e não mais de um bloco separado depois dele).
- Backup pré-edição: `backups/site-v1.46.zip`.

## v1.46 — 2026-07-18

Lote de correções enviado pelo usuário em formato de tabela (Prioridade/Problema/Correção), confirmado para implementação em lote único ("Tudo de uma vez"):

- **[Crítica] "Cota atual" renomeado para "Nível atual do rio"** no card principal e nas legendas do gráfico — o termo antigo soava como cota altimétrica ou profundidade, não como leitura de régua.
- **[Crítica] Quadro "Cotas de Referência* (Cheias Históricas)" separado em dois quadros distintos**: "Enchentes Históricas*" (as 6 grandes enchentes + o menor nível já registrado) e "Referências por Bairro*" (as ~17 estimativas por bairro), cada um com sua própria marca "O rio está aqui agora!". Ambos ganharam barra de rolagem (`max-height` + `overflow-y:auto` em `.reference-list`) com o título sempre visível fora da área rolável; a marca do nível atual é centralizada automaticamente na primeira carga (`centerCurrentMarker()`, novo em `app.js`), sem forçar rolagem nas atualizações seguintes.
- **[Alta] Fonte da atualização exibida dinamicamente no cabeçalho**: novo elemento `#sourceNote`, populado por `renderCards()`, mostra "Fonte desta atualização: ANA" ou "Fonte desta atualização: Copel (redundância, ANA ainda não publicou esta hora)" — corrige a inconsistência entre o cabeçalho (que sempre citava só a ANA) e a fonte real de cada leitura.
- **[Média] Gráfico com menos linhas de referência**: agora mostra só os 5 níveis de alerta + os extremos históricos (enchentes e o menor nível), tirando do gráfico as ~17 cotas de bairro (que continuam na lista lateral) — o gráfico tinha ficado ilegível com tantas linhas próximas, várias só com número.
- **[Média] Primeira pergunta do FAQ ("Como foram definidos os níveis de alerta deste site?") reestruturada**: resposta simples primeiro; média, desvio padrão e distribuição normal foram movidos para dentro de um acordeão aninhado "Ver metodologia".
- **[Média] Tendência e previsão de 48h reformuladas em `scrape.py`**, para linguagem não técnica e em pt-BR: "BAIXANDO -0.006 m/h" virou algo como "Baixando cerca de 0,6 cm por hora" (troca automática para metros acima de 1 m/h de variação); "Previsão em 48 h: pode atingir 3.91 m (ALERTA)." virou "Estimativa automática para as próximas 48 horas: 3,91 m. Não é uma previsão oficial." — deixa claro que não é um boletim oficial da Defesa Civil/ANA.
- **[Baixa] Nota de rodapé das listas (bairros, enchentes, fontes) com fonte maior e mais contraste**: 11px → 13px, cor `var(--muted)` → `var(--soft)`.
- **FAQ consolidado**: as perguntas "O que é a ANA?", "O que é o HidroWeb?", "O que é uma estação fluviométrica?", "O que é uma estação telemétrica?", "O que é o IAT?", "De onde vem a altitude dos terrenos?" e "O que é o CNEFE?" (todas adicionadas na v1.45) foram unificadas em uma única pergunta "De onde vêm os dados do site?", com três blocos curtos (nível do rio: ANA/Copel; endereços: CNEFE/IBGE; altitude: GeoPR/IAT). As perguntas `O que é o "nível de régua"?` e "Esses números são exatos?" continuam separadas.
- Backup pré-edição: `backups/site-v1.45.zip`.

## v1.45 — 2026-07-18

- **FAQ bastante ampliado**, com conteúdo revisado e fornecido pelo usuário:
- "O que é a ANA?" reescrita.
- Novas perguntas: "O que é o HidroWeb?", "O que é uma estação fluviométrica?" e "O que é uma estação telemétrica?" — estas duas últimas substituem a antiga pergunta única "De onde vêm as medições do rio?", detalhando separadamente a 65310000 (histórica) e a 65310001 (tempo real).
- Nova pergunta: `O que é o "nível de régua"? É a profundidade do rio?`, explicando o conceito de régua/zero de régua e a conversão pra cota altimétrica (739,61 m).
- Nova pergunta: "O que é o IAT?".
- "De onde vem a altitude dos terrenos?" e "O que é o CNEFE?" reescritas (mais diretas, já que "IAT" passou a ter pergunta própria antes delas).
- "Esses números são exatos?" ganhou menção explícita à fonte das cotas de terreno (GeoPR/IAT).
- Ordem reorganizada: ANA → HidroWeb → estação fluviométrica → estação telemétrica → nível de régua → IAT → altitude dos terrenos → CNEFE → exatidão → botão → Fontes.
- **Botão de destaque no fim do FAQ** ("Quer entender a fundo? Veja de onde vêm os dados →"), substituindo o item de acordeão "Quer conhecer mais sobre este projeto?" da v1.44 — link para `estudo.html`, agora estilizado como botão (`.faq-cta-button`, novo em `styles.css`) em vez de pergunta.
- Página `estudo.html` renomeada/retitulada para "De onde vêm os dados: o estudo por trás do rioiguacu.com", mantendo o aviso de "em breve" até o artigo real ser publicado.
- Backup pré-edição: `backups/site-v1.44.zip`.

## v1.44 — 2026-07-18

- Subtítulo de Enchentes Históricas simplificado mais uma vez, para "Abaixo, os meses em que ocorreram cada grande enchente." (removido o "(nível ≥ 6,89 m)" do final, a pedido do usuário).
- **Nova pergunta no FAQ:** "Quer conhecer mais sobre este projeto?", com link para uma nova página `estudo.html` — reservada para um artigo com a metodologia documentada a nível científico, que o usuário vai publicar depois. Criada uma página `estudo.html` provisória ("Em breve...") pra esse link não ficar quebrado até o conteúdo real ser publicado.
- Resposta de "E quando o rio está muito baixo?" ampliada com mais estatística: 59 episódios de estiagem em 96 anos, concentrados entre outono e início da primavera, e o mais longo (122 dias) em 2006.
- Nova regra de estilo `.faq-item p a` (cor ciano, negrito), reaproveitando o padrão visual já usado em `.reference-note a`, para os links dentro de respostas do FAQ.
- Backup pré-edição: `backups/site-v1.43.zip`.

## v1.43 — 2026-07-18

- **FAQ reestruturado: cada pergunta agora é seu próprio item de acordeão**, no mesmo padrão visual dos demais itens (Ranking Sazonal, Enchentes Históricas, Dados Visíveis), em vez de um único item guarda-chuva com 11 subtítulos `<h3>` dentro. Pedido do usuário ("faça que cada pergunta daquela vire uma abinha"). Isso também corrigiu, na raiz, um bug visual relatado pelo usuário: o `<h3>` aninhado dentro do `<details>` estava renderizando grande/branco em vez do estilo pequeno (14px)/ciano pretendido — como não há mais `<h3>` aninhado, a hierarquia invertida deixa de existir.
- **Removido o parágrafo de abertura do FAQ** ("Cobre somente o que o site exibe: níveis de alerta, cotas por bairro e as fontes dos dados. Todos os números derivam de fontes auditadas do projeto... Nenhum critério externo foi utilizado."), sinalizado pelo usuário como confuso e sem relação com a pergunta do resumo — usava jargão interno (CNEFE, GeoPR/IAT) sem contexto para quem chega no site sem conhecer os bastidores do projeto.
- **Corrigido bug de cache do `styles.css`:** o `<link>` não tinha parâmetro de versão (diferente do `app.js?v=X.XX`), então o navegador podia manter indefinidamente uma cópia antiga do CSS em cache. Agora é `styles.css?v=1.43`.
- Subtítulo da 1ª tabela do Ranking Sazonal simplificado para "Em que mês o rio atingiu o pico do ano (o nível mais alto de cada ano) · 1930–2025", a pedido do usuário. (Esse ajuste tinha sido rascunhado localmente como "v1.42" antes de ganhar sua forma final — nunca chegou a ser publicado como versão separada; entra direto nesta v1.43.)
- Backup pré-edição: `backups/site-v1.41.zip`.

## v1.41 — 2026-07-18

- Subtítulo da 2ª tabela do Ranking Sazonal reformulado para "Em que mês ocorreu o pico de cada enchente (considerado enchentes de 10 anos com cota mínima ≥ 6,89 m) · 1930–07/2026", a pedido do usuário (texto anterior estava confuso).
- Removida a frase "Atualizado em 18/07/2026: inclui picos de 2024 (Dezembro, 5,48 m) e 2025 (Junho, 4,57 m), fonte telemétrica 65310001. 2026 (parcial) não entra na contagem." da nota de rodapé do Ranking Sazonal, a pedido do usuário.
- Subtítulo de Enchentes Históricas simplificado para "Abaixo, os meses em que ocorreram cada enchente (nível ≥ 6,89 m)", removendo a explicação sobre o critério de 6,89 m que ficava ali (o usuário pediu para cortar em duas etapas, terminando nesse texto mínimo).
- Backup pré-edição: `backups/site-v1.40.zip`.

## v1.40 — 2026-07-18

- **As 3 seções (Dados Visíveis, Ranking Sazonal, Enchentes Históricas) viraram acordeão no mesmo formato do FAQ** (`<details>/<summary>`), substituindo o padrão de abas com botões da v1.39. Ordem: Ranking Sazonal, Enchentes Históricas, Dados Visíveis (por último) — pedido do usuário. `setupTabs()` removido de `app.js`, já que o `<details>` nativo dispensa JS.
- **Removida a seção "Guia de Emergência e Informações Úteis"** (perguntas "Como funciona o monitoramento" e "Quais bairros são afetados primeiro"), redundante com o FAQ novo da v1.39. Os **Contatos de Emergência** (Defesa Civil 199, Bombeiros 193, PM 190) foram movidos para dentro do aviso vermelho "Enchente é risco à vida".
- FAQ renomeado de "Perguntas frequentes sobre o Rio Iguaçu" para só "Perguntas frequentes".
- **"Alertas de Nível do Rio" ganhou um asterisco** com nota linkando para o FAQ ("*Para mais informações, consulte as Perguntas frequentes").
- **Gauge/escala de cor atualizados pra bater com os 5 níveis reais** (Observação 3,70 / Atenção 4,20 / Alerta 5,00 / Emergência 5,50 / Enchente 6,50 m): `NIVEL_MAX_ESCALA` foi de 5,5 para 6,5 m e os stops de cor de `colorForLevel()` passaram a usar os valores reais dos limiares em vez de frações genéricas da escala antiga.
- Removido o texto "Situação do rio: X" abaixo do gauge — redundante com o badge que já mostra o mesmo nível ao lado da cota atual.
- **Cards Vazão e Chuva unidos num único bloco** (`.metric-split`, dois `.metric-block` lado a lado com divisória), reduzindo o espaço vazio que cada card tinha sozinho. `hero-grid` passou de 4 para 3 colunas.
- Backup pré-edição: `backups/site-v1.39.zip`.

## v1.39 — 2026-07-18

- **Reestruturação em abas:** as três seções que ficavam sempre visíveis abaixo do gráfico (Dados Visíveis, Ranking Sazonal, Enchentes Históricas) viraram uma única área com 3 abas clicáveis, todas fechadas por padrão. Pedido do usuário, pra reduzir o comprimento da página.
- **Novos níveis de alerta do rio, com metodologia estatística (substituindo os 4 níveis antigos da Defesa Civil):** Observação 3,70 m · Atenção 4,20 m · Alerta 5,00 m · Emergência 5,50 m · Enchente 6,50 m, calculados a partir da série histórica ANA 1930–2023 (média 2,67 m, desvio padrão 1,08 m) cruzada com o banco de cotas por bairro (CNEFE/IBGE + relevo GeoPR/IAT). Inclui regra de escalonamento por velocidade: subida ≥0,85 m em 24h eleva o alerta um degrau, independente do nível absoluto. Implementado em `scrape.py` (`COTAS_ALERTA_DEFESA_CIVIL`, `LIMIAR_SUBIDA_24H_M`, `definir_situacao()`) e refletido em `app.js` (`severityClass()`).
- **Nota de transparência:** ao migrar para o novo sistema de 5 níveis, o texto que listava bairros afetados em cascata dentro da string de `situacao` (ex. "afetando Limeira / Rio d'Areia / Rocio...") foi removido — não mapeava de forma limpa nos novos limiares estatísticos. A lista de cotas por bairro (`COTAS_BAIRROS`) e a seção "Cotas de Referência" no site continuam com o mesmo conteúdo de antes, sem alteração.
- **FAQ reduzido a uma única aba fechada**, com todo o texto da metodologia de alerta (por que cada nível foi escolhido, de onde vêm os dados, o que é CNEFE/GeoPR/IAT) — substitui as 5 perguntas curtas anteriores. Conteúdo fornecido pelo usuário (`FAQ_NIVEIS_ALERTA_PROPOSTA.md`). O schema.org FAQPage foi removido do `<head>` porque o Google descontinuou esse rich result em maio/2026 — o conteúdo continua no HTML normalmente.
- **Indicador de cor no card Tendência:** uma bolinha colorida (`trend-dot`) ao lado do texto de tendência, refletindo se o rio está subindo rápido, subindo devagar, estável, descendo devagar ou descendo rápido, calculado em `trendColor()` a partir do campo `delta` de `data.tendencia`.
- **Cards de Vazão e Chuva reformatados** (`display:flex; flex-direction:column; justify-content:center`) pra aproveitar melhor o espaço vertical da caixa, que estava com sobra grande.
- **Corrigido espaço vazio abaixo do gráfico:** o grid principal (`.main-grid`) esticava a coluna do gráfico pra igualar a altura da coluna lateral (Cotas de Referência + Alertas), mais alta. Fix de uma linha (`align-items: start`).
- **Corrigido alinhamento das tabelas de Ranking Sazonal e Enchentes Históricas** no mobile: adicionado scroll horizontal (`overflow-x: auto` + `white-space: nowrap` nas células) em vez de quebra de linha cramped, e padding consistente com os outros cards (`.tabs-panel { padding: 18px }`, que faltava nas seções antigas).
- **Explicado o critério de 6,89 m** na aba Enchentes Históricas: novo parágrafo dizendo que é a cota da "cheia de 10 anos" nos estudos de zoneamento da SEC-CORPRERI.
- **Melhorado o texto dos subtítulos do Ranking Sazonal**, deixando mais claro o que cada uma das duas tabelas mostra (pico do ano vs. pico de cada episódio de cheia).
- Removida a menção "e a Copel como fonte de apoio" do subtítulo do cabeçalho, a pedido do usuário.
- **Gap de processo, disclosure:** o backup em `backups/site-v1.39.zip` e esta entrada do changelog foram gerados depois do commit das mudanças (não antes, como pede a REGRA OBRIGATÓRIA), por limitação de sequenciamento nesta sessão. O ponto de rollback usado é o estado ao vivo capturado no início da sessão (pré-edição), preservado no zip.

## v1.36 — 2026-07-18

- **Restaurada a cota "Menor nível histórico - estiagem de 2020" (1,29 m)** em `COTAS_BAIRROS` (`scrape.py` e `app.py`), que tinha ficado de fora da substituição completa da lista na v1.33.
- **Cores das bolinhas da lista "Cotas de Referência" agora fixas por categoria**, em vez da escala de cor por severidade: amarelo para bairros, vermelho para enchentes históricas, verde para a menor cota já registrada. Pedido do usuário, pra facilitar a leitura visual da lista maior de 23 pontos.

## v1.35 — 2026-07-18

- **Melhorada a formatação da nota de rodapé** das Cotas de Referência: virou um "callout box" com fundo/borda sutil e mais respiro (padding), em vez de texto corrido colado no topo do card seguinte. Asterisco inicial destacado com `<span class="note-mark">`.

## v1.34 — 2026-07-18

- **Marcador visual diferente para cotas de "Enchente de AAAA"** vs bairros na lista de Cotas de Referência: entradas de enchente histórica agora usam um losango (`swatch-event`, `border-radius: 3px; transform: rotate(45deg)`) em vez do círculo padrão, mantendo a mesma escala de cor por severidade. Pedido do usuário, pra facilitar a leitura rápida da lista maior de 23 pontos.

## v1.33 — 2026-07-18

- **Substituída toda a tabela "Cotas de Referência (Cheias Históricas)"** (`COTAS_BAIRROS` em `scrape.py` e `app.py`) por uma nova lista de 23 pontos fornecida diretamente pelo usuário, com bairros específicos (Cidade Jardim, Rio D'Areia, São Basílio Magno, Nossa Senhora do Rocio, Navegantes, São Bernardo, Ponte Nova, Sagrada Família, São Joaquim, Bento Munhoz da Rocha, Limeira, São Gabriel, Bom Jesus, Cristo Rei, Centro - União da Vitória, Panorama, Nossa Senhora da Salete) e enchentes históricas (2019, 2014, 1935, 2023, 1992, 1983), substituindo a lista anterior de 8 pontos mais genéricos. **Nota de transparência:** esses valores foram fornecidos pelo usuário por instrução explícita, contornando a verificação cruzada de fontes normalmente exigida pela memória do projeto para dados de cota por bairro (que até então não tinham sido encontrados/confirmados em nenhuma fonte pesquisada) — o próprio usuário reconheceu essa trava e pediu para ignorá-la nesta ocasião.
- **Adicionado título com asterisco e nota de metodologia** no `index.html`: "Cotas de Referência* (Cheias Históricas)" com nota de rodapé explicando que os valores são aproximados/estimados a partir de endereços do Censo do IBGE cruzados com o mapa de altitudes do Governo do Paraná, não substituem avisos oficiais, e reforçando o contato da Defesa Civil (199).

## v1.32 — 2026-07-18

- **Encurtado o rótulo da cota de alerta crítico** na lista `COTAS_ALERTA_DEFESA_CIVIL` (`scrape.py` e `app.py`), de "ALERTA CRÍTICO - PLANO DE CONTINGÊNCIA ACIONADO" para apenas "ALERTA CRÍTICO" — pedido do usuário. Afeta a linha da cota 5,50 m mostrada no painel "Alertas de Nível" do site. O texto do selo de situação no topo (que detalha bairros afetados conforme o nível sobe) foi mantido como estava, sem mudança.

## v1.31 — 2026-07-18

- **Corrigido bug grave que apagava o histórico diário em conflitos de push.** No bloco de retry do `update.yml` (acionado quando outra execução do workflow commita primeiro), o script restaurava `historico_diario.csv` a partir de um snapshot em `/tmp` calculado **antes** do `git reset --hard origin/main`. Como esse arquivo é cumulativo (1 linha por dia, upsert por data), qualquer commit que tivesse chegado nesse meio-tempo — inclusive um backfill manual — era apagado por completo ao ser sobrescrito pelo snapshot velho. Foi assim que o backfill histórico 2024–2026 (commit `1b13a66e`, +917 linhas) foi apagado 34 segundos depois pelo próprio bot (commit `3d72381e`, -917 linhas). Corrigido parando de restaurar `historico_diario.csv` nesse bloco: depois do reset o arquivo já está com a versão mais recente do remoto, e a linha do dia da execução atual (se ainda faltar) é recalculada normalmente na rodada seguinte, poucos minutos depois — sem risco de perder histórico de terceiros.
- Motivação: descoberto ao investigar por que um backfill manual de `historico_diario.csv` (dados 2024–2026 da estação ANA 65310001) sumia minutos depois de ser commitado.
- Nenhuma mudança visual no site — só correção de infraestrutura de coleta/publicação de dados.

## v1.30 — data não registrada

- Entrada pendente: o rodapé do site já mostra "Versão 1.30" ao vivo, mas esta versão não foi documentada aqui. Ainda não investigado o que mudou entre a v1.29 e a v1.30.

## v1.29 — 2026-07-13

- **Republicado o `scrape.py` com as cotas originais da Defesa Civil** (4,30/4,50/4,90/5,50 m, com os rótulos "ATENÇÃO MODERADA/ALTA/MUITO ALTA" e "ALERTA CRÍTICO - PLANO DE CONTINGÊNCIA ACIONADO") depois de uma publicação indevida (v1.27) ter trocado esses valores por outros não autorizados pelo usuário. Cotas de bairro e rótulo do painel ("Alertas de Nível") mantidos como estavam.
- **Recriada a seção "Guia de Emergência e Informações Úteis" + "Perguntas frequentes"** no `index.html`, restaurando o conteúdo exato do commit da v1.26 (que tinha sido removido na v1.27 durante uma restauração de emergência pra v1.24). Rodapé atualizado pra "Versão 1.29".
- Corrigido `index.html` que estava com uma versão menor/incompleta publicada por engano (sem rodapé/contador de visitas).
- Disparo manual do workflow `update.yml` pra regenerar o `data.json` com os dados corretos, já que o agendador automático (Worker `rioiguacu-trigger`) tinha ficado sem disparar por ~48 min.

## v1.26 — 2026-07-13

- **Nova seção "Guia de Emergência e Informações Úteis"** (entre a tabela de dados e o FAQ), com explicação de como funciona o monitoramento, bairros historicamente afetados por cheias (Navegantes, São Bernardo, Rio D'Areia, Limeira — lista baseada no relatório CENACID/UFPR já documentado no projeto, sem cravar cota exata por bairro) e contatos de emergência nacionais (Defesa Civil 199, Bombeiros 193, PM 190).
- **Nota de processo:** uma ferramenta de IA externa (Antigravity) chegou a editar o `index.html` local diretamente com uma proposta similar, mas com dados fabricados/não verificados — cotas de "alerta" inventadas (3,00/4,50/5,50 m, sem fonte), um bairro que não existe em nenhuma pesquisa do projeto ("Christofis") e telefones fixos locais de Defesa Civil que não bateram com nenhuma fonte oficial checada (Prefeitura de União da Vitória e de Porto União). Nada disso chegou a ser publicado — foi revertido antes do build desta versão. Mantido só o número 199 (Defesa Civil, nacional, confirmado) e a redação com ressalvas já usada no resto do site.
- Nenhuma mudança de dados/funcionalidade dinâmica.

## v1.25 — 2026-07-13

- **Melhorias de SEO** pra ranquear melhor no Google para buscas como "nível do rio iguaçu união da vitória": adicionada seção "Perguntas frequentes" com conteúdo estático (nível atual, referências de cheias históricas, como funciona a régua, maior cheia registrada, origem dos dados) + schema.org FAQPage no `<head>`. Headers internos com mais contexto de palavras-chave: "Cotas de referência" → "Cotas de Referência (Cheias Históricas)", "Alertas de Nível" → "Alertas de Nível do Rio". `sitemap.xml` com `lastmod` atualizado. Title/meta description/H1 mantidos como estavam (o site já aparece em 1º lugar em buscas testadas pra essas queries, então essas partes não foram mexidas pra não arriscar a posição já conquistada).
- Nenhuma mudança de dados/funcionalidade dinâmica — só conteúdo estático novo e ajuste de texto em headers existentes.

## v1.24 — 2026-07-12

- **Corrigida seta "→ O rio está aqui agora!" invisível no celular.** O caractere usado (🡒, U+1F852) tem suporte ruim/inexistente em fontes de navegadores mobile, renderizando em branco. Trocado pela seta padrão → (U+2192), com suporte universal. Nenhuma outra mudança.

## v1.23 — 2026-07-12

- **Removida toda referência a "Defesa Civil" do site**, a pedido do usuário (recebeu recomendação de tirar). Trocado o texto do cabeçalho (`Defesa Civil · Monitoramento Hidrológico` → `Monitoramento Hidrológico`) e o título do painel de alertas (`Alertas Defesa Civil` → `Alertas de Nível`). O conteúdo dos alertas (níveis de atenção/crítico) continua o mesmo, só o rótulo mudou.
- Nenhuma mudança de dados/funcionalidade — só texto visível.

## v1.22 — 2026-07-12

- **Novo: Cloudflare Worker `rioiguacu-trigger`.** Dispara o workflow `update.yml` via API do GitHub (`workflow_dispatch`) a cada 5 minutos, usando um Cron Trigger do Cloudflare (muito mais confiável que o agendador nativo do GitHub Actions). Requer um secret `GITHUB_PAT` (fine-grained, escopo só do repo `rioiguacu`, permissão Actions: Read and write) configurado no Worker — configurado pelo próprio usuário, nunca manuseado por mim.
- **Removida a rajada de cron `1-5 * * * *`** do `update.yml` (tentativa de todo minuto nos primeiros 5 min de cada hora). Diagnóstico: analisando o histórico de commits do `data.json`, achamos vários atrasos de 2h+ na atualização do site (ex: 07/11 23:25-01:32, 07/12 23:14-01:03) causados pelo próprio agendador `schedule` do GitHub Actions simplesmente não disparando — e não por falha do `scrape.py`. O GitHub avisa oficialmente que o início de cada hora é o pico de carga do agendador; a rajada rodava exatamente nessa janela mais congestionada, piorando o problema que tentava resolver. Mantido `*/15 * * * *` como rede de segurança redundante ao Worker.
- Motivação: usuário reportou "o site tem demorado pra pegar os dados... ontem o atraso passava de 2h".
- Nenhuma mudança visual no site — só infraestrutura de coleta de dados.

## v1.21 — 2026-07-11

- **Novo: favicon/ícone do site.** Adicionado `logo.png` (criado pelo usuário) como ícone oficial, gerados `favicon.ico`, `favicon-16x16.png`, `favicon-32x32.png`, `apple-touch-icon.png` (180×180) e ícones Android/PWA (`android-chrome-192x192.png`, `android-chrome-512x512.png`), todos referenciados no `<head>` do `index.html`.
- **Preview de link melhorado (WhatsApp/redes sociais):** adicionado `og-image.png` (630×630, a partir do mesmo logo) via `og:image`/`twitter:image` — antes o preview não tinha nenhuma imagem. Título e descrição do `og:title`/`og:description`/`twitter:*` também foram reescritos pra explicar melhor o que é o site ("site gratuito e público pra acompanhar o Rio Iguaçu... atualizados a cada 5 minutos") em vez de só listar métricas, já que o texto anterior não deixava claro do que se tratava ao ser compartilhado.
- Motivação: usuário compartilhou o link no WhatsApp e reparou que o preview aparecia sem logo e com pouca explicação do que era o site.
- Sem mudança de funcionalidade — só metadados de `<head>` e novos arquivos de imagem estáticos.

## v1.20 — 2026-07-11

- **Novo: histórico diário automático (`historico_diario.csv`).** O `scrape.py` agora grava, a cada coleta bem-sucedida, 1 linha por dia (nível máximo/mínimo/último de régua em metros, vazão do último horário e fonte) num CSV crescente no repositório. Isso dá continuidade ao histórico oficial da ANA/HidroWeb da estação 65310000 (que só cobre até 31/12/2023) com os dados telemétricos da estação 65310001 coletados a partir de agora — sem precisar de nenhuma intervenção manual daqui pra frente.
- O `update.yml` foi ajustado pra também commitar/publicar o `historico_diario.csv` (além do `data.json`), com a mesma lógica de só gerar deploy quando um desses dois arquivos realmente muda.
- Motivação: pedido do usuário por uma planilha de estudo do histórico do rio (sazonalidade, mês com mais risco de enchente) — o histórico oficial da ANA (1930–2023) foi extraído manualmente numa planilha à parte; esta mudança evita que o mesmo trabalho manual precise ser refeito no futuro, mantendo o histórico sempre atualizado.
- Nenhuma mudança visual no site — só um novo arquivo de dados sendo gerado em paralelo ao `data.json`.

## v1.19 — 2026-07-10

- **SEO: o site não aparecia bem no Google para buscas como "nível rio iguaçu união da vitória" ou "porto união".** Adicionados: `<title>` e `<meta name="description">` otimizados com essas palavras-chave; tags Open Graph e Twitter Card (melhora o preview ao compartilhar o link no WhatsApp/redes); dados estruturados JSON-LD (`schema.org/WebSite`); `<link rel="canonical">` apontando pra `https://rioiguacu.com/`; `robots.txt` e `sitemap.xml` (nenhum dos dois existia antes).
- Subtítulo do cabeçalho passou a mencionar também Porto União (SC), não só União da Vitória (PR), e a frase "nível do rio em tempo real" — mais fiel ao propósito do projeto (que sempre foi as duas cidades) e mais alinhado com o que as pessoas buscam.
- Nenhuma mudança visual/funcional no painel de dados, gráfico ou lógica de coleta — só metadados e HTML de cabeçalho.
- Nota: isso melhora a indexação e a relevância percebida pelo Google, mas não garante uma posição específica no ranking — isso também depende de backlinks e do tempo até o Google re-rastrear o site. Recomendado cadastrar `rioiguacu.com` no Google Search Console.

## v1.18 — 2026-07-09

- **Corrigida cor dos pontos do histórico no gráfico:** os pontos ao longo da linha de histórico usavam a mesma escala de cor por severidade das cotas de referência (azul→ciano→verde→amarelo→laranja→vermelho), o que fazia a maioria aparecer amarela/dourada mesmo com a legenda mostrando um ponto ciano fixo para "Histórico". Agora os pontos usam a mesma cor ciana da linha e da legenda, consistente.
- **Corrigida escala vertical "achatada" do gráfico:** o cálculo de folga do eixo vertical reservava espaço até a 2ª cota de referência mais próxima do nível atual, incluindo cotas históricas distantes (ex.: menor nível histórico de 1,29 m, estiagem de 2020), o que esticava a escala de ~1 m a quase 8 m e espremia a variação real numa faixa fina. Agora a folga considera só as cotas de ALERTA (as quatro faixas da Defesa Civil), mantendo o gráfico com zoom na faixa relevante.
- **Removida a linha "Previsão sem chuva" do gráfico:** as duas linhas de previsão (com e sem chuva) ficavam muito próximas e confundiam a leitura. Mantida só a previsão com chuva, renomeada de "Previsão com chuva" para simplesmente "Previsão" na legenda, no tooltip e no código.
- Limpeza: removida a regra CSS `.dry` (usada só pela legenda da linha removida) e o cálculo de previsão sem chuva na escala vertical do gráfico.

## v1.17 — 2026-07-09

- **Migração da fonte de dados histórica: Copel → ANA (API oficial), com Copel como redundância.** `scrape.py` agora consulta primeiro a API HidroWebservice da ANA (Agência Nacional de Águas e Saneamento Básico, estação telemétrica 65310001 — UHE Gov. Bento Munhoz, União da Vitória) e só cai para o scraping da Copel quando a ANA ainda não publicou a leitura da hora corrente (situação esperada nos primeiros minutos após cada hora fechar) ou em caso de falha. A previsão continua vindo exclusivamente da Copel, pois a ANA não oferece esse dado.
- Credenciais da ANA nunca ficam no código: vêm das variáveis de ambiente `ANA_API_LOGIN`/`ANA_API_SENHA`, configuradas como GitHub Actions Secrets (é preciso cadastrá-las manualmente em Settings → Secrets and variables → Actions do repositório — sem isso a integração ANA fica inativa e o site continua funcionando só com Copel, sem quebrar nada).
- Novo agendamento no GitHub Actions: roda todo minuto entre HH:01 e HH:05 (para pegar a leitura da ANA assim que ela publica, com folga pro atraso de transmissão da estação), além do ritmo normal de 15 em 15 minutos no resto da hora.
- **Correção de deploy:** o commit/push do `data.json` agora só acontece quando o próprio `data.json` muda de fato (antes considerava também o `monitor_web.log`, que muda em toda execução por ser só texto de log — isso teria reintroduzido o engarrafamento de deploys no Cloudflare Pages que a v1.6 corrigiu, já que a nova janela de tentativas por minuto multiplicava as execuções por hora).
- Texto do site atualizado: cabeçalho e o painel de dados agora citam a ANA como fonte, com a fonte real de cada atualização (`ANA` ou, nos raros casos de redundância, `Copel`) mostrada dinamicamente ao lado de "Dados visíveis", lida do campo `fonte` do `data.json` — nunca mais um texto fixo que pode não bater com a fonte real daquela leitura.
- Nota técnica: durante a verificação desta versão foi confirmado que o `scrape.py` publicado (e não o snapshot local, que estava desatualizado) já tinha, desde versões anteriores, fuso horário correto (`America/Sao_Paulo`, adicionado na v1.7) e as cotas de referência corrigidas de 2014/2023/1992 (8,12/8,37/8,90 m, corrigidas nas v1.14/v1.15). A migração para ANA foi construída em cima desse estado real ao vivo, não do snapshot local desatualizado, para não reverter essas correções.

## v1.16 — 2026-07-07

- **Correção de erro grave:** a "v1.6" publicada mais cedo em 07/07 foi feita em cima de um snapshot local desatualizado (equivalente à v1.5) e, ao subir pro GitHub, apagou tudo que tinha sido feito entre v1.6 e v1.15 — inclusive o contador de visitas via Cloudflare Worker (com o histórico real de visitas) e a remoção do botão "Atualizar". Esta versão restaura o estado exato da v1.15 (confirmado via `raw.githubusercontent.com` no commit `d38a8b6`) e aplica por cima, de forma isolada, só a funcionalidade nova (gráfico de chuva).
- Contador de visitas restaurado, chamando o mesmo Worker de sempre (`rioiguacu-counter.thiago-dff.workers.dev/track`) — a contagem real (total/semana/dia) não foi zerada, só parou de aparecer por 33 minutos enquanto a v1.6 quebrada esteve no ar.
- Botão "Atualizar" removido de novo (tinha sido removido na v1.7, voltou por engano na v1.6 quebrada) — o site já atualiza sozinho a cada 5 min.
- Link "Histórico de versões" removido do rodapé de novo (tinha sido removido em 02/07, voltou por engano na v1.6 quebrada).
- Mantido o novo painel de barras de precipitação (chuva horária, mm) abaixo do gráfico principal de cota, com tooltip generalizado para mostrar "mm" nas barras e "m" no resto do gráfico.
- Nova regra de processo: antes de qualquer publicação, comparar arquivo por arquivo com o que está ao vivo em `raw.githubusercontent.com/thiagoiwanko/rioiguacu/main/...`, não confiar em snapshot local sem verificar primeiro.

## v1.15 — 2026-07-03

- Bump de versão (commit "Versao 1.15"). Sem detalhe adicional na mensagem do commit.

## v1.14 — 2026-07-03

- Bump de versão (commit "Versao 1.14"). Sem detalhe adicional na mensagem do commit.

## v1.13 — 2026-07-03

- Corrige condição de corrida (race condition) no contador de visitas, migrando o armazenamento de KV para Durable Object do Cloudflare.

## v1.12 — 2026-07-03

- Corrige cache do navegador que travava `app.js` numa versão antiga (parâmetro `?v=` de cache-busting no `<script src="app.js?v=...">`).

## v1.11 — 2026-07-03

- Contador de visitas implementado via Cloudflare Worker + KV (`rioiguacu-counter.thiago-dff.workers.dev`), mostrando total, visitas na semana e visitas no dia no rodapé.

## v1.10 — 2026-07-03

- Bump de versão no rodapé.

## v1.9 — 2026-07-02

- Contador de visitas (total/semana/dia) adicionado no rodapé (primeira versão, antes da migração pra Worker+KV na v1.11).

## v1.8 — 2026-07-02

- Bump de versão para 1.8.
- Removido o link "Histórico de versões" do rodapé.

## v1.7 — 2026-07-02

- Removido o botão "Atualizar" do cabeçalho (o site já atualiza sozinho a cada 5 min via `setInterval`).
- Corrigido bug de fuso horário.
- Investigação do agendamento (cron) do GitHub Actions.

## v1.6 — 2026-07-02

- Reduzida a frequência de coleta para 15 min, corrigindo um engarrafamento no Cloudflare Pages causado por deploys demais em pouco tempo.

## v1.5 — 2026-07-02

- Gráfico: ao passar o mouse (ou tocar, no celular) sobre qualquer ponto da linha — histórico, previsão sem chuva ou previsão com chuva — aparece um balão mostrando a cota exata e o horário daquele ponto.
- Corrigido também um bug de corrupção de bytes introduzido no upload anterior do `scrape.py` (um byte inválido na linha 264 quebrava a coleta no GitHub Actions com `SyntaxError`); reenviado com verificação de integridade byte a byte.

## v1.4 — 2026-07-02

- Corrigida a cota de referência da enchente de 2014, de 8,15 m para 8,13 m. O valor anterior estava incorreto: 8,15 m era, na verdade, o nível atingido em 18/10/2023 (quando o rio ultrapassou a marca de 2014), não o pico real de 2014. Fontes: reportagens da época e documento oficial de reordenamento territorial da Prefeitura de União da Vitória (2022), que registra 8,12 m para a enchente de 2014.
- Ajustado o limiar correspondente na descrição textual da situação do rio (scrape.py e app.py).

## v1.3 — 2026-07-02

- Corrigido bug de dimensionamento do gráfico no celular: a largura interna era travada em no mínimo 760px, fazendo o gráfico "encolher" no meio de uma área com altura fixa de 485px e deixando faixas vazias em cima/embaixo em telas estreitas.
- Gráfico agora calcula largura, altura e espaçamentos de forma responsiva conforme a largura real da tela (fontes, caixas de legenda e eixos reduzidos no mobile).
- Ajustes gerais de layout para telas pequenas: títulos, cartões de métricas e listas de referência com tamanhos mais compactos.
- Confirmado via PageSpeed Insights: nota 100/100/100 (Performance/Acessibilidade/Boas práticas) em mobile e desktop — a lentidão percebida era o bug visual do gráfico, não velocidade de carregamento.

## v1.2 — 2026-07-01

- Status de sincronização agora mostra também "próxima atualização às HH:MM", calculado a partir do horário do último dado coletado.
- Gráfico: o ponto mais recente (cota atual) agora pulsa com um anel de destaque e o texto "Cota atual" logo abaixo dele.

## v1.1 — 2026-07-01

- Gráfico: toda cota de referência agora mostra seu valor em texto pequeno junto à linha, mesmo as que não têm a caixa de legenda completa (que continua reservada às duas cotas mais próximas do nível atual).

## v1.0 — 2026-07-01

Primeira versão estável rodando 100% no GitHub (sem servidor local).

- Migração do monitor de um servidor Python local (Selenium + HTTP server) para GitHub Actions + GitHub Pages.
- `scrape.py` roda automaticamente a cada 5 minutos via GitHub Actions, gera `data.json` estático e o site consome esse arquivo direto.
- Corrigido bug de parsing da vazão: valores acima de 1.000 m³/s usam "." como separador de milhar e estavam sendo descartados, travando a leitura mais recente.
- Gráfico: nível atual agora fica centralizado verticalmente, com espaço reservado para cotas de alerta acima e abaixo.
- Gráfico: caixas de legenda de cotas de referência próximas (ex. 4.30 m e 4.50 m) não se sobrepõem mais.
- Lista "Cotas de referência": adicionado marcador móvel destacado "O rio está aqui agora!" na posição correta entre as cotas.
- Selo de situação do rio colorido por gravidade: amarelo (atenção moderada), laranja (atenção alta), vermelho (atenção muito alta) e vermelho piscando com giroflex (alerta crítico).
- Escala de cores e barra de nível recalibradas: vermelho a partir de 5,50 m (nível de alerta crítico), em vez de 10,42 m (cheia histórica de 1983).
- Rodapé com número de versão e link para este changelog.
