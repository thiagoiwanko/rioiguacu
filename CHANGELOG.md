# Histórico de versões — Monitor Rio Iguaçu

Cada versão tem um backup completo do código-fonte em `backups/site-vX.Y.zip`, gerado antes de qualquer modificação.

## v1.11 — 2026-07-03

- Migrado o contador de visitas da CountAPI (terceiro que saiu do ar) para um Worker + KV do próprio Cloudflare (`rioiguacu-counter`, namespace `RIOIGUACU_VISITS`). O Worker calcula a data/semana em horário de Brasília e incrementa os contadores de total, semana e dia direto no KV, retornando os três valores numa única chamada. O `app.js` agora chama só esse endpoint, sem depender de nenhum serviço externo. Configurado manualmente pelo usuário no painel do Cloudflare (Workers e Pages → Associações), já que o painel/API do Cloudflare ficaram instáveis nesta automação durante boa parte do processo.

## v1.10 — 2026-07-03

- Corrigida falha intermitente na coleta automática: cerca de 3% das execuções do GitHub Actions falhavam ao tentar publicar `data.json` ("! [rejected] main -> main (fetch first)"), porque duas execuções do workflow às vezes tentam gravar no repositório quase ao mesmo tempo, e a que termina depois é rejeitada por já não ter a versão mais recente do repositório. O `.github/workflows/update.yml` agora tenta novamente automaticamente (até 5 vezes): ao ser rejeitado, sincroniza com o repositório remoto e reenvia os dados coletados, em vez de simplesmente falhar e gerar o aviso por e-mail.
- Constatado que o contador de visitas (v1.9) parou de funcionar porque o serviço gratuito CountAPI (terceiro, usado para hospedar os números) saiu do ar (passou a responder erro 503 e depois parou de responder). Como o código falha silenciosamente quando a API não responde (para não quebrar o site), o número simplesmente não aparecia. Em investigação uma alternativa mais confiável.

## v1.9 — 2026-07-02

- Adicionado contador de visitas no rodapé, ao lado do número da versão: total de visitas, visitas na semana e visitas no dia. Implementado com a CountAPI (serviço público gratuito e anônimo, sem login/conta) chamado direto pelo navegador do visitante — tentei primeiro montar isso com Worker + KV do próprio Cloudflare (mais privado, sem terceiros), mas o painel do Cloudflare não carregou nesta automação (travava indefinidamente mesmo depois de fechar o Kaspersky). Importante: é contagem de acessos (hits) por carregamento de página, não de visitantes únicos.

## v1.8 — 2026-07-02

- Corrigida a cota de referência da enchente de 2014, de 8,13 m para 8,12 m. O usuário enviou o documento oficial "Reordenamento Territorial" (Prefeitura de União da Vitória, março/2022) para conferência, que confirma na íntegra: "O nível do rio chegou a 8,12 metros de profundid