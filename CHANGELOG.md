# Histórico de versões — Monitor Rio Iguaçu

Cada versão tem um backup completo do código-fonte em `backups/site-vX.Y.zip`, gerado antes de qualquer modificação.

## v1.12 — 2026-07-03

- Corrigido cache do navegador que impedia o contador novo (v1.11) de aparecer para quem já tinha visitado o site: como `app.js` era referenciado sem versão (`<script src="app.js">`), navegadores guardavam a versão antiga em cache por tempo indefinido e continuavam usando o código velho (com a CountAPI morta) mesmo depois do arquivo ser atualizado no servidor — confirmado testando em aba nova, que ainda executava a função antiga. Corrigido de duas formas: (1) o `index.html` agora referencia `app.js?v=1.12`, forçando o navegador a buscar a versão nova a cada atualização de versão; (2) adicionado arquivo `_headers` instruindo o Cloudflare Pages a nunca cachear `app.js` sem revalidar, prevenindo que o mesmo problema se repita em futuras atualizações mesmo se o número de versão for esquecido.

## v1.11 — 2026-07-03

- Migrado o contador de visitas da CountAPI (terceiro que saiu do ar) para um Worker + KV do próprio Cloudflare (`rioiguacu-counter`, namespace `RIOIGUACU_VISITS`). O Worker calcula a data/semana em horário de Brasília e incrementa os contadores de total, semana e dia direto no KV, retornando os três valores numa única chamada. O `app.js` agora chama só esse endpoint, sem depender de nenhum serviço externo. Configurado manualmente pelo usuário no painel do Cloudflare (Workers e Pages → Associações), já que o painel/API do Cloudflare ficaram instáveis nesta automação durante boa parte do processo.

## v1.10 — 2026-07-03

- Corrigida falha intermitente na coleta automática: cerca de 3% das execuções do GitHub Actions falhavam ao tentar publicar `data.json` ("! [rejected] main -> main (fetch first)"), porque duas execuções do workflow às vezes tentam gravar no repositório quase ao mesmo tempo, e a que termina depois é rejeitada por já não ter a versão mais recente do repositório. O `.github/workflows/update.yml` agora tenta novamente automaticamente (até 5 vezes): ao ser rejeitado, sincroniza com o repositório remoto e reenvia os dados coletados, em vez de simplesmente falhar e gerar o aviso por e-mail.
- Constatado que o contador de visitas (v1.9) parou de funcionar porque o serviço gratuito CountAPI (terceiro, usado para hospedar os números) saiu do ar (passou a responder erro 503 e depois parou de responder). Como o código falha silenciosamente quando a API não responde (para não quebrar o site), o número simplesmente não aparecia. Em investigação uma alternativa mais confiável.

## v1.9 — 2026-07-02

- Adicionado contador de visitas no rodapé, ao l