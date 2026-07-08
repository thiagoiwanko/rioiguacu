# Histórico de versões — Monitor Rio Iguaçu

Cada versão tem um backup completo do código-fonte em `backups/site-vX.Y.zip`, gerado antes de qualquer modificação.

**Sobre esta reconstrução (07/07/2026):** este arquivo estava desatualizado — parava na v1.5 — e por isso a v1.6 publicada em 07/07 acabou reusando um número de versão já existente e sobrescrevendo tudo que tinha sido feito entre v1.6 e v1.15 (mais grave: apagou o contador de visitas real, com histórico de mais de mil acessos). As entradas de v1.6 a v1.15 abaixo foram reconstruídas a partir do histórico de commits do GitHub (`git log --follow index.html`), não da memória do assistente. Ver `## v1.16` para a correção completa.

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
