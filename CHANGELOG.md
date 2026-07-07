# Histórico de versões — Monitor Rio Iguaçu

Cada versão tem um backup completo do código-fonte em `backups/site-vX.Y.zip`, gerado antes de qualquer modificação.

## v1.6 — 2026-07-07

- Novo painel pequeno de barras de precipitação (mm), anexado logo abaixo do gráfico principal de cota, compartilhando o mesmo eixo de tempo.
- Cada barra representa a chuva horária (`chuva_mm`) já coletada da Copel; passar o mouse (ou tocar) mostra o valor exato e o horário, igual ao gráfico de régua.
- Tooltip do gráfico generalizado para suportar unidades diferentes (m para régua, mm para chuva).
- Nova legenda "Chuva horária (mm)" no cabeçalho do gráfico.

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
