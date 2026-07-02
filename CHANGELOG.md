# Histórico de versões — Monitor Rio Iguaçu

Cada versão tem um backup completo do código-fonte em `backups/site-vX.Y.zip`, gerado antes de qualquer modificação.

## v1.9 — 2026-07-02

- Adicionado contador de visitas no rodapé, ao lado do número da versão: total de visitas, visitas na semana e visitas no dia. Implementado com a CountAPI (serviço público gratuito e anônimo, sem login/conta) chamado direto pelo navegador do visitante — tentei primeiro montar isso com Worker + KV do próprio Cloudflare (mais privado, sem terceiros), mas o painel do Cloudflare não carregou nesta automação (travava indefinidamente mesmo depois de fechar o Kaspersky). Importante: é contagem de acessos (hits) por carregamento de página, não de visitantes únicos.

## v1.8 — 2026-07-02

- Corrigida a cota de referência da enchente de 2014, de 8,13 m para 8,12 m. O usuário enviou o documento oficial "Reordenamento Territorial" (Prefeitura de União da Vitória, março/2022) para conferência, que confirma na íntegra: "O nível do rio chegou a 8,12 metros de profundidade" na enchente de 2014. Ajustado em `scrape.py` e `app.py` (COTAS_BAIRROS e limiar em `definir_situacao`). As cotas de 1992 (9,80 m) e 1983 (10,42 m) não constam nesse documento (que só cita o número de mortes por enchente), então não foram alteradas.
- Removido o link "Histórico de versões" do rodapé, mantendo apenas o texto "Versão 1.8".

## v1.7 — 2026-07-02

- Removido o botão "Atualizar" do topo do site. Como a coleta agora é automática (a cada 5 min no scraper, publicada pelo Pages a cada 15 min) e a página já se atualiza sozinha em segundo plano, o botão de atualização manual havia perdido a função.
- Corrigido bug de fuso horário: o `scrape.py` gravava "atualizado_em" com `datetime.now()` rodando em UTC (horário do servidor do GitHub Actions), sem converter para o horário de Brasília. Isso fazia o rótulo "Atualizado em / próxima atualização" aparecer cerca de 3h adiantado em relação ao horário real. A cota, o gráfico e a tabela não eram afetados (usam o horário que vem direto da Copel). Corrigido usando `zoneinfo` para gravar sempre em horário de Brasília (America/Sao_Paulo).
- Investigado por que a coleta não roda de forma confiável a cada 15 min: o `schedule` (cron) do GitHub Actions roda numa fila compartilhada de baixa prioridade com todo o GitHub, sem garantia de horário — medimos atrasos reais de 1h a 4h entre execuções, mesmo com o cron configurado corretamente. Isso é uma limitação da plataforma do GitHub, não um erro de configuração. Site migrado para hospedagem no Cloudflare Pages (domínio rioiguacu.com) e um Cloudflare Worker com Cron Trigger está sendo configurado para disparar a coleta via API do GitHub de forma confiável, contornando essa fila.

## v1.6 — 2026-07-02

- Corrigido o motivo real do site "parar de atualizar": os deploys do GitHub Pages estavam levando 8–10 min para publicar, mas a coleta fazia commit a cada 5 min — os deploys se atropelavam e nenhum terminava de publicar, deixando o site visível travado em uma versão antiga mesmo com o repositório sempre atualizado por trás. Frequência de coleta reduzida de 5 em 5 min para 15 em 15 min para dar tempo do Pages publicar cada versão.

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
