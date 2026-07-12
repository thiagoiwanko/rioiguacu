# Histórico de versões — Monitor Rio Iguaçu

Cada versão tem um backup completo do código-fonte em `backups/site-vX.Y.zip`, gerado antes de qualquer modificação.

**Sobre esta reconstrução (07/07/2026):** este arquivo estava desatualizado — parava na v1.5 — e por isso a v1.6 publicada em 07/07 acabou reusando um número de versão já existente e sobrescrevendo tudo que tinha sido feito entre v1.6 e v1.15 (mais grave: apagou o contador de visitas real, com histórico de mais de mil acessos). As entradas de v1.6 a v1.15 abaixo foram reconstruídas a partir do histórico de commits do GitHub (`git log --follow index.html`), não da memória do assistente. Ver `## v1.16` para a correção completa.

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
