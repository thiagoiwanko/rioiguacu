# Histórico de versões — Monitor Rio Iguaçu

Cada versão tem um backup completo do código-fonte em `backups/site-vX.Y.zip`, gerado antes de qualquer modificação.

**Sobre esta reconstrução (07/07/2026):** este arquivo estava desatualizado — parava na v1.5 — e por isso a v1.6 publicada em 07/07 acabou reusando um número de versão já existente e sobrescrevendo tudo que tinha sido feito entre v1.6 e v1.15 (mais grave: apagou o contador de visitas real, com histórico de mais de mil acessos). As entradas de v1.6 a v1.15 abaixo foram reconstruídas a partir do histórico de commits do GitHub (`git log --follow index.html`), não da memória do assistente. Ver `## v1.16` para a correção completa.

**Nota sobre v1.37/v1.38 (18/07/2026):** essas duas versões foram publicadas em sessões anteriores sem entrada correspondente neste changelog e sem backup em `backups/`. O gap não foi corrigido retroativamente por falta de detalhe confiável sobre o que mudou em cada uma — registrar aqui um resumo reconstruído de memória seria arriscar detalhes errados. A partir da v1.39 o processo voltou a seguir a REGRA OBRIGATÓRIA do CLAUDE.md.

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
