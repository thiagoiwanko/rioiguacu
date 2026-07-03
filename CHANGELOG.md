# Histórico de versões — Monitor Rio Iguaçu

Cada versão tem um backup completo do código-fonte em `backups/site-vX.Y.zip`, gerado antes de qualquer modificação.

## v1.13 — 2026-07-03

- Corrigida inconsistência no contador de visitas: o usuário percebeu que "hoje" mostrava mais visitas que "na semana" (113 x 112), o que é logicamente impossível já que a semana inclui o dia de hoje. Causa: o Worker `rioiguacu-counter` incrementava os contadores no Workers KV com um padrão ler → somar 1 → gravar, mas o KV não é atômico nem fortemente consistente — quando várias requisições chegam quase ao mesmo tempo (como aconteceu bastante durante os testes desta migração), gravações concorrentes podem se sobrescrever e "perder" incrementos, de forma independente para cada contador. Corrigido migrando o armazenamento de Workers KV para um Durable Object (`VisitCounterDO`), que processa uma requisição de cada vez para o mesmo objeto — o runtime do Cloudflare garante isso — eliminando a corrida de vez. O código-fonte do Worker agora também é versionado neste repositório, em `cloudflare-worker/rioiguacu-counter.js`, para ter backup (antes só existia dentro do painel do Cloudflare). Números de total/semana/dia foram migrados a partir da última leitura consistente disponível, sem perder o histórico.

## v1.12 — 2026-07-03

- Corrigido cache do navegador que impedia o contador novo (v1.11) de aparecer para quem já tinha visitado o site: como `app.js` era referenciado sem versão (`<script src="app.js">`), navegadores guardavam a versão antiga em cache por tempo indefinido e continuavam usando o código velho (com a CountAPI morta) mesmo depois do arquivo ser atualizado no servidor — confirmado testando em aba nova, que ainda executava a função antiga. Corrigido de duas formas: (1) o `index.html` agora referencia `app.js?v=1.12`, forçando o navegador a buscar a versão nova a cada atualização de versão; (2) adicionado arquivo `_headers` instruindo o Cloudflare Pages a nunca cachear `app.js` sem revalidar, prevenindo que o mesmo problema se repita em futuras atualizações mesmo se o número de versão for esquecido.

## v1.11 — 2026-07-03

- Migrado o contador de visitas da CountAPI (terceiro que saiu do ar) para um Worker + KV do próprio Cloudflare (`rioiguacu-counter`, namespace `RIOIGUACU_VISITS`). O Worker calcula a data/semana em horário de Brasília e incrementa os contadores de total, semana e dia direto no KV, retornando os três valores numa única chamada. O `app.js` agora chama só esse endpoint, sem depender de nenhum serviço externo. Configurado manualmente pelo usuário no painel do Cloudflare (Workers e Pages → Associações), já que o painel/API do Clo