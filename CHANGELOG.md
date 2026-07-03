# Histórico de versões — Monitor Rio Iguaçu

Cada versão tem um backup completo do código-fonte em `backups/site-vX.Y.zip`, gerado antes de qualquer modificação.

## v1.10 — 2026-07-03

- Corrigida falha intermitente na coleta automática: cerca de 3% das execuções do GitHub Actions falhavam ao tentar publicar `data.json` ("! [rejected] main -> main (fetch first)"), porque duas execuções do workflow às vezes tentam gravar no repositório quase ao mesmo tempo, e a que termina depois é rejeitada por já não ter a versão mais recente do repositório. O `.github/workflows/update.yml` agora tenta novamente automaticamente (até 5 vezes): ao ser rejeitado, sincroniza com o repositório remoto e reenvia os dados coletados, em vez de simplesmente falhar e gerar o aviso por e-mail.
- Constatado que o contador de visitas (v1.9) parou de funcionar porque o serviço gratuito CountAPI (terceiro, usado para hospedar os números) saiu do ar (passou a responder erro 503 e depois parou de responder). Como o código falha silenciosamente quando a API não responde (para não quebrar o site), o número simplesmente não aparecia. Em investigação uma alternativa mais confiável.

## v1.9 — 2026-07-02

- Adicionado contador de visitas no rodapé, ao lado do número da versão: total de visitas, visitas na semana e visitas no dia. Implementado com a CountAPI (serviço público gratuito e anônimo, sem login/conta) chamado direto pelo navegador do visitante — tentei primeiro montar isso com Worker + KV do próprio Cloudflare (mais privado, sem terceiros), mas o painel do Cloudflare não carregou nesta automação (travava indefinidamente mesmo depois de fechar o Kaspersky). Importante: é contagem de acessos (hits) por carregamento de página, não de visitantes únicos.

## v1.8 — 2026-07-02

- Corrigida a cota de referência da enchente de 2014, de 8,13 m para 8,12 m. O usuário enviou o documento oficial "Reordenamento Territorial" (Prefeitura de União da Vitória, março/2022) para conferência, que confirma na íntegra: "O nível do rio chegou a 8,12 metros de profundidade" na enchente de 2014. Ajustado em `scrape.py` e `app.py` (COTAS_BAIRROS e limiar em `definir_situacao`). As cotas de 1992 (9,80 m) e 1983 (10,42 m) não constam nesse documento (que só cita o número de mortes por enchente), então não foram alteradas.
- Removido o link "Histórico de versões" do rodapé, mantendo apenas o texto "Versão 1.8".

## v1.7 — 2026-07-02

- Removido o botão "Atualizar" do topo do site. Como a coleta agora é automática (a cada 5 min no scraper, publicada pelo Pages a cada 15 min) e a página já se atualiza sozinha em segundo plano, o botão de atualização manual havia perdido a função.
- Corrigi