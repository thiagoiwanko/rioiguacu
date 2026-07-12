# CLAUDE.md - Memoria do projeto Rio Iguacu

## Hospedagem e Infraestrutura

**URL:** https://rioiguacu.com (também: https://www.rioiguacu.com)  
**Hospedagem:** Cloudflare Pages  
**Cloudflare Pages project:** `rioiguacu` → `rioiguacu.pages.dev`  
**Cloudflare account ID:** `dffb378e10f41dbfc75aeeb686e0f95c`  
**DNS (gerenciado pelo Cloudflare):**

| Tipo  | Nome            | Conteúdo             | Proxy      |
|-------|-----------------|----------------------|------------|
| CNAME | rioiguacu.com   | rioiguacu.pages.dev  | Com proxy  |
| CNAME | www.rioiguacu.com | rioiguacu.pages.dev | Com proxy  |

**Pasta do projeto (Windows):** `C:\MD\OneDrive\Claude\Sites\enchente` — migrada em 07/07/2026 do caminho antigo `C:\Claude\Sites\enchente` (o usuário moveu a pasta pra dentro do OneDrive como camada extra de backup). **Se em alguma sessão futura o Read/Write falhar em `C:\Claude\Sites\enchente` com "outside this session's connected folders", é porque a pasta mudou de lugar — chamar `request_cowork_directory` sem path pra abrir o seletor e reconectar no caminho certo, não assumir que ainda é o caminho antigo.**

**Caminho bash desta pasta muda a cada sessão** (nome do sandbox é gerado por sessão, ex. `/sessions/jolly-stoic-sagan/mnt/enchente/`) — sempre confirmar com `ls` no início da sessão, nunca fixar o nome do sandbox de uma sessão anterior.

**Nota sobre OneDrive:** a pasta agora é sincronizada pelo OneDrive. Isso é transparente pro Read/Write/Edit (que sempre funcionam), mas o bash só enxerga arquivos que já estão baixados em disco — se um comando bash der erro "No such file" num arquivo que existe, é provável que esteja "somente na nuvem" ainda; usar Read nele primeiro (isso baixa o arquivo) antes de tentar de novo via bash.

### Disparo confiável do scrape (Cloudflare Worker `rioiguacu-trigger`, desde v1.22, 12/07/2026)

**Problema descoberto:** o agendador `schedule` nativo do GitHub Actions falha silenciosamente com frequência — não é o `scrape.py` que trava, é o GitHub que simplesmente não dispara o job na hora. Confirmado cruzando o histórico de commits do `data.json` (via API do GitHub) com o histórico de execuções do workflow: em várias janelas de mais de 2h sem nenhuma atualização, só rodaram 2-3 execuções quando deveriam ter rodado ~16 (a cada 15 min). O GitHub avisa oficialmente que o início de cada hora é o pico de carga do agendador `schedule` — e a antiga rajada `1-5 * * * *` (removida na v1.22) rodava exatamente nessa janela mais congestionada.

**Solução:** Worker `rioiguacu-trigger` (`rioiguacu-trigger.thiago-dff.workers.dev`, mesmo account Cloudflare `dffb378e10f41dbfc75aeeb686e0f95c`) com Cron Trigger a cada 5 min (`*/5 * * * *`, muito mais confiável que o `schedule` do GitHub), que chama `POST https://api.github.com/repos/thiagoiwanko/rioiguacu/actions/workflows/update.yml/dispatches` com `{"ref":"main"}`. Requer secret `GITHUB_PAT` (fine-grained, escopo só do repo `rioiguacu`, permissão Actions: Read and write) configurado nas variáveis do Worker — **gerado e configurado pelo próprio usuário**, nunca por mim (não manuseio tokens/credenciais). Endpoint `/run` no Worker permite testar o dispatch manualmente sem esperar o cron. O `schedule: */15 * * * *` do `update.yml` continua ativo como rede de segurança redundante, caso o Worker ou o PAT parem de funcionar.

**Nota técnica sobre automação do editor Cloudflare:** o editor "Quick Edit" do dashboard Cloudflare (`quick-edit-workers.devprod.cloudflare.dev`, carregado num iframe cross-origin) não aceita digitação simulada via automação de navegador (Claude-in-Chrome) — cliques não focam o Monaco editor interno, e `Ctrl+A`/digitação acabam atingindo a página pai em vez do editor. Se precisar editar o código de um Worker no futuro, ou (a) peça pro usuário colar o código manualmente, ou (b) tente outra via (ex: GitHub integration/CI do próprio Worker, se configurada). Cron Triggers e outras configurações em `Configurações` (fora do iframe do editor) funcionam normalmente via automação.

### Arquitetura do projeto (importante)
O diretório local contém dois componentes distintos:
- **Frontend estático** (`index.html`, `styles.css`, `app.js`) — é o que está publicado no Cloudflare Pages em `rioiguacu.com`
- **Backend local** (`app.py`, `scrape.py`, `requirements.txt`) — scripts Python que rodam **localmente** para raspar dados da Copel/ANA. O `monitor_web.log` confirma execução local. O `abrir_monitor_web.bat` abre o monitor local.

Fluxo atual presumido: `scrape.py` busca dados → atualiza o `index.html` → push para GitHub → Cloudflare Pages auto-deploys o HTML atualizado.

**Histórico diário automático (`historico_diario.csv`, desde v1.20, 11/07/2026):** a cada coleta bem-sucedida, `scrape.py` grava/atualiza 1 linha por dia (nível máximo/mínimo/último de régua em metros, vazão do último horário do dia e fonte) num CSV crescente na raiz do repo. Dá continuidade ao histórico oficial da ANA/HidroWeb da estação 65310000 (que só cobre até 31/12/2023) com os dados telemétricos da estação 65310001 coletados a partir de 11/07/2026 em diante — sem depender de download manual. Publicado junto com `data.json` pelo `update.yml` (mesma lógica de só gerar deploy quando um dos dois muda).

---

## REGRA OBRIGATÓRIA: backup, verificação e log a cada modificação

**Incidente de 07/07/2026 (por que esta regra existe e foi reforçada):** uma publicação de "v1.6" (gráfico de chuva) foi feita em cima de um snapshot local desatualizado (equivalente à v1.5), sem checar o que estava realmente no ar. Isso sobrescreveu 10 versões de trabalho real (v1.6 a v1.15) que só existiam no GitHub, incluindo o contador de visitas com histórico de mais de mil acessos, a remoção do botão "Atualizar" e a remoção do link de changelog — tudo isso voltou por engano. Foi corrigido na v1.16 reconstruindo o estado exato a partir do commit `d38a8b6` (a v1.15 real) via `raw.githubusercontent.com`, e não de memória. **Isso não pode se repetir.** A partir de agora:

1. **Antes de editar qualquer arquivo do site** (`index.html`, `app.js`, `styles.css`, `app.py`, `scrape.py`): buscar o conteúdo AO VIVO no GitHub (`raw.githubusercontent.com/thiagoiwanko/rioiguacu/main/<arquivo>`, via Claude-in-Chrome — o sandbox bash/web_fetch não alcança github.com) e comparar com o snapshot local (`Read` do arquivo local). **Se houver qualquer diferença que não seja a mudança pretendida, parar e investigar antes de editar** — não presumir que o snapshot local está atualizado, mesmo que pareça óbvio.
2. Gerar um backup completo do código-fonte do estado ATUAL AO VIVO (não do estado já editado) em `backups/site-vX.Y.zip` (incluir pelo menos `index.html`, `styles.css`, `app.js`, `app.py`, `scrape.py`, `requirements.txt`, `CHANGELOG.md`, `CLAUDE.md`, `.github/workflows/update.yml`, `abrir_monitor_web.bat`, `monitor_web.log`), **antes** de editar os arquivos. Esse backup é o ponto de rollback — precisa refletir o que estava no ar, não uma versão já modificada.
3. Editar os arquivos localmente.
4. **Antes de publicar (rodar `publicar_github.py`):** comparar cada arquivo local, campo a campo / linha a linha, contra o conteúdo ao vivo já buscado no passo 1 — confirmar que a única diferença é exatamente a mudança pretendida (nenhum elemento de cabeçalho, rodapé, botão, contador ou estrutura pode desaparecer sem ter sido pedido). Rodar `node --check app.js` pra sintaxe. Conferir que todo `id` referenciado no JS existe no HTML. **Repetir essa comparação quantas vezes for preciso até bater 100% — não existe limite de tentativas aceitável pra pular essa checagem.**
5. Depois da mudança E da verificação, registrar uma entrada nova no `CHANGELOG.md` (padrão já usado: `## vX.Y — AAAA-MM-DD`, com bullets descrevendo o que mudou) e numerar a versão como a PRÓXIMA depois da última versão real confirmada ao vivo (não a última versão que o CLAUDE.md/CHANGELOG.md local documentava — esses arquivos podem estar desatualizados).
6. Só depois de tudo isso, pedir pro usuário rodar `publicar_github.py`.
7. Nunca pular esses passos, mesmo para mudanças pequenas.
8. **Também subir um zip da versão pra `backups/site-vX.Y.zip` dentro do próprio repositório GitHub** (pasta `backups/`, já tem histórico de v1.0 até v1.15 lá) — não só guardar local. Esse zip deve incluir pelo menos os mesmos arquivos do passo 2, já no estado publicado.

---

## Funcionalidades do index.html

### Favicon / ícone e imagem de preview social (desde v1.21, 11/07/2026)

O usuário criou `logo.png` (1254×1254, RGB, quadrado com fundo branco/quase-branco, "U" estilizado em gradiente azul/verde representando o rio) e colocou na raiz do projeto. A partir dele foram gerados (Pillow, `Image.resize`/`Image.save(format="ICO")`) e commitados na raiz do repo:

- `favicon.ico` (16/32/48px), `favicon-16x16.png`, `favicon-32x32.png`
- `apple-touch-icon.png` (180×180)
- `android-chrome-192x192.png`, `android-chrome-512x512.png`
- `og-image.png` (630×630, usado em `og:image`/`twitter:image` pra preview de link no WhatsApp/redes sociais — antes não existia nenhuma imagem de preview)

Todos referenciados no `<head>` do `index.html`. Se o usuário substituir o `logo.png` no futuro, regenerar todos esses arquivos a partir do novo original (mesmo processo) e re-publicar.

### Contador de visitas (Cloudflare Worker + Durable Object) — versão correta/atual desde a v1.16

O contador **não é** hits.sh nem qualquer serviço de terceiro — é um Worker próprio do Cloudflare, implementado originalmente na v1.11 (02-03/07/2026) e restaurado na v1.16 depois do incidente de sobrescrita descrito na "REGRA OBRIGATÓRIA" acima. **Não trocar por hits.sh ou qualquer outro serviço externo sem o usuário pedir explicitamente** — já aconteceu uma vez (commit `24a9c02`, um remendo temporário) e não é o que deve ficar.

- Worker: `rioiguacu-counter.thiago-dff.workers.dev`, conta `rioiguacu-counter`, binding de Durable Object chamado `COUNTER` (classe `VisitCounterDO`), no account Cloudflare `dffb378e10f41dbfc75aeeb686e0f95c`.
- Endpoint usado pelo site: `GET https://rioiguacu-counter.thiago-dff.workers.dev/track` → retorna JSON `{ total, week, day }`. CORS restrito a `https://rioiguacu.com`.
- No `index.html`, rodapé (`<footer class="version-footer">`):
  ```html
  <footer class="version-footer">
    <span>Versão X.Y</span>
    <span id="visitCounter" class="visit-counter"></span>
  </footer>
  ```
- No `app.js`, função `trackVisit()` faz o fetch, preenche `#visitCounter` com `· {total} visitas · {week} na semana · {day} hoje` (formatado via `Intl.NumberFormat("pt-BR")`), falha silenciosamente se o Worker estiver fora do ar, e é chamada uma vez no carregamento da página (não em cada `refresh()`).
- Não tem link "Histórico de versões" no rodapé — foi removido de propósito na v1.8/v1.9 (02/07/2026) porque o usuário não queria isso ali.
- Não tem botão "Atualizar" no cabeçalho — removido de propósito na v1.7 (02/07/2026); a atualização já é automática a cada 5 min via `setInterval` em `app.js`.

Isso vale para qualquer sessão futura, não só para quem está com a memória ativa agora.

## Contexto

O usuario e Thiago Jorge Iwanko, responsavel pelo projeto Rio Iguacu: https://rioiguacu.com.

Objetivo do projeto: criar um site simples, publico e acessivel para acompanhar os niveis do Rio Iguacu na regiao de Uniao da Vitoria/PR e Porto Uniao/SC, especialmente em periodos de cheia/enchente. O site deve ajudar moradores, comerciantes, imprensa local, voluntarios e familias em areas de risco a entenderem rapidamente o nivel atual do rio, historico recente e referencias de risco.

O usuario esta pesquisando dados historicos oficiais, cotas altimetricas, referencias de enchentes e possiveis formas de traduzir nivel do rio em impacto urbano.

## Fontes locais e tecnicas ja analisadas

### ANA / HidroWeb

Arquivos analisados da estacao `65310000`:

- `65310000_Cotas.csv`
- `65310000_Vazoes.csv`
- `65310000_CurvaDescarga.csv`
- `65310000_PerfilTransversal.csv`
- `65310000_ResumoDescarga.csv`
- `65310000_QualAgua.csv`
- `65310000_Sedimentos.csv`

Conclusao:

- Os CSVs sao dados oficiais da ANA/HidroWeb.
- `Cotas` contem nivel diario do rio em centimetros de regua.
- Serie analisada: 22/05/1930 a 31/12/2023.
- `Vazoes` contem vazao diaria.
- `CurvaDescarga` contem equacoes oficiais para converter cota de regua em vazao.
- `PerfilTransversal` contem perfil do leito/secao da estacao, nao cota de ruas.
- Estes dados servem para historico oficial do rio, mas nao dao cota por rua diretamente.

Picos principais no HidroWeb/ANA, estacao 65310000:

| Evento | Data | Regua |
|---|---:|---:|
| 1983 | 18/07/1983 | 10,42 m |
| 1992 | 08/06/1992 | 8,90 m |
| 2023 | 20/10/2023 | 8,37 m |
| 1935 | 17/10/1935 | 8,16 m |
| 2014 | 17/06/2014 | 8,12 m |
| 2019 | 08/06/2019 | 7,82 m |
| 1957 | 20/08/1957 | 7,28 m |
| 1993 | 06/10/1993 | 7,25 m |
| 1998 | 12/10/1998 | 7,19 m |
| 2010 | 08/05/2010 | 7,00 m |

Arquivos de resumo ja gerados:

- `outputs/analise_estacao_65310000.md`
- `outputs/analise_estacao_65310000.json`

### Webnode / Mais Uniao / Porto Uniao

Site pesquisado:

- https://portouniao.webnode.com.br/
- https://portouniao.webnode.com.br/not/enchentes/
- https://portouniao.webnode.com.br/conhecendo%20porto%20uni%C3%A3o/conhecendo-e-convivendo-com-enchentes/

Material principal: texto tecnico/local chamado "Conhecendo e Convivendo com Enchentes", assinado por Dago Woehl em 27/12/1999. O texto republica/explica estudos relacionados a SEC-CORPRERI, JICA, COPEL, Tucci, Villanueva, CEHPAR/CERPAR e monitoramento do Rio Iguacu.

Arquivos extraidos:

- `outputs/extracao_webnode_enchentes.txt`
- `outputs/varredura_portouniao_webnode_enchentes.md`
- `outputs/varredura_portouniao_webnode_enchentes.json`

Dados importantes do Webnode:

| Referencia | Cota altimetrica | Regua aprox. |
|---|---:|---:|
| Zero da regua ANEEL/ex-DNAEE na ponte ferroviaria | 739,61 m | 0,00 m |
| Area de preservacao / area desapropriada pela COPEL | <= 744,50 m | ate 4,89 m |
| Cheia padrao ordinaria | 744,70 m | 5,09 m |
| Cenario com Foz do Areia operando em 741,50 m | 744,43 m | 4,82 m |
| Cenario com vazao de 2.000 m3/s e rebaixamento para 740,00 m | 745,74 m | 6,13 m |
| Cota-alvo de reassentamento/dique | 746,50 m | 6,89 m |
| Cheia de 1993 | 746,88 m | 7,27 m |
| Cheia de 1935 | 747,80 m | 8,19 m |
| Cheia de 1992 | 748,50 m | 8,89 m |
| Area condicional | 746,50 m a 748,50 m | 6,89 m a 8,89 m |
| Area de baixa densidade | 746,50 m a 750,00 m | 6,89 m a 10,39 m |
| Cheia de 1983 | 750,03/750,04 m | 10,42 m |
| Cota minima recomendada para piso/equipamentos em projetos | acima de 750,00 m | acima de 10,39 m |
| Cenario extremo citado com Foz do Areia em 743,50 m | 750,30 m | 10,69 m |
| Cenario com Foz do Areia em 740,00 m | 750,06 m | 10,45 m |

Formula consolidada:

```text
cota altimetrica = nivel da regua + 739,61 m
nivel da regua = cota altimetrica - 739,61 m
```

Exemplos:

- 5,00 m na regua = cota 744,61 m.
- 8,89 m na regua = cota 748,50 m.
- 10,42 m na regua = cota 750,03 m.

### Zoneamento e cotas de risco

Segundo o texto local/SEC-CORPRERI/JICA/Tucci e Villanueva:

- `<= 744,50 m`: area de preservacao e seguranca, terras desapropriadas pela COPEL para operacao de Foz do Areia. Usos sugeridos: parques, horto florestal, viveiros, uso agricola, areas ecologicas/turisticas.
- `ate 746,50 m`: area de protecao de recursos hidricos, linha associada a cheia de 10 anos. Imoveis dentro desta cota teriam probabilidade anual de 10% de inundacao.
- `746,50 m a 748,50 m`: area condicional. Nao deveria permitir novos predios/habitacoes. Protecao contra enchentes deve ser definida quando necessario.
- `746,50 m a 750,00 m`: area de baixa densidade, ocupacao com restricoes.
- `> 750,00 m`: referencia de seguranca para pelo menos um piso, equipamentos eletricos e adaptacoes construtivas.

### Regra pratica para moradores

O texto do Webnode da uma regra pratica muito util:

Se em 1992 a agua chegou em uma marca conhecida da casa, use a marca de 1992 como referencia.

Exemplo:

```text
marca de 1992 = 8,89 m
distancia da marca ate o piso = 0,80 m
nivel que pega o piso = 8,89 - 0,80 = 8,09 m
```

Isto pode virar funcionalidade do site:

- "Tenho uma marca de 1992 na parede; quantos cm abaixo dela fica meu piso?"
- O site calcula em que nivel de regua a agua chega no piso.

### SEC-CORPRERI

Nome completo encontrado:

```text
Sociedade de Estudos Contemporaneos - Comissao Regional Permanente de Prevencao Contra Enchentes do Rio Iguacu
```

Tambem apareceu como SEC-CORPRERI.

Pessoa citada pelo usuario:

```text
RICARDO DRAGONI
Representante da Comissao Regional Permanente de Prevencao Contra Enchentes do Rio Iguacu - SEC CORPRERI
```

Programa proposto:

- "Programa Uniao da Vitoria", horizonte de 20 anos.
- Defendia convivencia harmonica com o rio, zoneamento, defesa civil, previsao de cheia, seguros, reassentamento e desenvolvimento urbano em areas mais altas.

Premissas citadas:

- Condicionantes hidrologicas.
- Restricoes topograficas.
- Divisa de estados.
- Cidade polo.
- Entroncamento rodoviario e ferroviario.
- Rota de integracao com o Mercosul.
- Riqueza hidrica e paisagistica.
- Potencial historico-cultural/turistico.
- Reserva florestal remanescente.

Medidas previstas:

- Sistema de previsao de cheia e alerta.
- Organizacao da Defesa Civil.
- Mobilizacao popular.
- Seguro para areas sem protecao.
- Plano Diretor com zoneamento de enchentes.
- Reassentamento abaixo da cota 746,50 m.
- Desenvolvimento urbano no eixo Sao Cristovao x Sao Sebastiao, em areas acima da cota 750,00 m.
- Estagnacao de areas inundaveis abaixo de 746,50 m.
- Uso das areas abaixo de 744,50 m para uso agricola, parques ambientais e reservas.

### JICA / obras e alternativas

JICA 1995 analisou medidas estruturais e nao estruturais.

Alternativas:

- Reservatorio de contencao.
- Modificacao do leito do Rio Iguacu.
- Dique de protecao.
- Zoneamento.
- Relocacao/reassentamento.
- Seguro.
- Protecoes localizadas.
- Previsao em tempo real/curto prazo.

Dados:

- Prejuizos nas cheias de 1983, 1992 e 1993: US$ 89,9 milhoes.
- Dano anual provavel: US$ 9,8 milhoes/ano.
- Sistema de diques: 17 km, 8 conjuntos de drenagem, 1,4 milhao m3 de material, cota 746,50 m, custo estimado US$ 86 milhoes.
- Escavacao 1: remover 2 milhoes m3 de rocha, custo US$ 130 milhoes, reducao de 30 cm na cheia de 1983.
- Escavacao 2: remover 7 milhoes m3 de rocha, custo US$ 430 milhoes, reducao de 60 cm na cheia de 1983.
- Curva da Ressaca: reducao de 3 a 8 cm em Uniao da Vitoria.
- Fazenda Brasil: reducao de cerca de 20 cm.
- Ressaca + Fazenda Brasil: cerca de 30 cm, mas ainda insuficiente.

Conclusao local: obras de escavacao/retificacao reduzem pouco em relacao ao custo; zoneamento, previsao, defesa civil e reassentamento sao caminhos importantes.

### Foz do Areia / COPEL

O texto informa que:

- Estudos COPEL, COPEL/SPIDVHI, Tucci, JICA, HG-79/CEHPAR discutiram o efeito de remanso de Foz do Areia.
- Niveis altos em Foz do Areia podem aumentar cotas em Uniao da Vitoria, mas o efeito depende da vazao e do nivel operacional do reservatorio.
- Com vazao de 1000 m3/s, operar Foz do Areia em 742,00 m ou rebaixar para 740,00 m geraria diferenca de apenas 3 cm em Uniao da Vitoria.
- Com vazao de 2000 m3/s, se o reservatorio for mantido em 742,00 m, a influencia seria de 8 cm.
- Com Foz do Areia em 741,50 m, o nivel seria 744,43 m, regua 4,82 m.
- Com Foz do Areia em 743,50 m, o nivel citado chega a 750,30 m.
- Com Foz do Areia em 740,00 m, nivel citado em Uniao da Vitoria 750,06 m.
- Em dezembro de 1997 a SEC-CORPRERI apresentou tabela de restricao de operacao de Foz do Areia para vazoes entre 1200 e 1600 m3/s.
- Em 1998/1999 houve novas medicoes ADCP e discussao COPEL/SEC-CORPRERI para definir tabela de operacao que nao aumentasse niveis de enchente em Uniao da Vitoria.
- COPEL teria se comprometido a manter medicoes e disponibilizar dados por instrumento publico.

### ABRH214

PDF:

https://files.abrhidro.org.br/Eventos/Trabalhos/149/ABRH214.pdf

Conteudo:

- Artigo "Mapeamento automatico de areas inundaveis atraves de geoprocessamento - aplicacao a cidade de Uniao da Vitoria".
- Confirma existencia de base cartografica digital, escala 1:2.000, com:
  - pontos cotados;
  - curvas de nivel;
  - sistema viario;
  - eixos de vias;
  - edificacoes;
  - rios/alagados.
- Confirma digitalizacao do mapa de inundacao da CORPRERI com curvas para tempos de recorrencia de 5, 10, 50 e 100 anos.
- Cita curvas das cheias de junho de 1992 e janeiro de 1995 cedidas pela COPEL.
- Nao publica tabela rua por rua, nem shapefile/DXF/GIS, nem pontos cotados.

Conclusao:

- Este PDF e uma pista para pedir os dados originais.
- A cota por rua depende de obter a base cartografica/curvas de nivel/mapas de inundacao da COPEL/CORPRERI/JICA/Prefeituras.

Pedido formal sugerido:

```text
Solicito acesso ao estudo "Controle de Enchentes de Uniao da Vitoria e Porto Uniao", de Tucci e Villanueva, 1997, elaborado para a CORPRERI, incluindo mapas de inundacao, curvas de recorrencia de 5, 10, 50 e 100 anos, base cartografica, pontos cotados, curvas de nivel, sistema viario, arquivos digitais em formato GIS/shapefile/DXF, ou copia digitalizada dos mapas em escala 1:2.000.
```

### CENACID/UFPR

PDF:

https://cenacid.ufpr.br/wp-content/uploads/2017/10/Avalia%C3%A7%C3%A3o-das-%C3%A1reas-atingidas-pelas-inunda%C3%A7%C3%B5es-e-alagamentos-em-Uni%C3%A3o-da-Vit%C3%B3ria-PR..pdf

Conteudo:

- Relatorio de avaliacao das areas atingidas por inundacoes/alagamentos em Uniao da Vitoria.
- Lista bairros atingidos em 2014.
- Cita que em 2014 o Rio Iguacu passou de 5,75 m e comecou a invadir casas, chegando a 8,13/8,15 m.
- Cita cerca de 40% da cidade submersa e cerca de 12 mil pessoas afetadas.

Bairros principais atingidos em Uniao da Vitoria segundo o relatorio:

Margem esquerda do Rio Iguacu:

- Limeira
- Rio de Areia / Rio D'Areia
- Sao Basilio
- Rocio
- Monte Castelo
- Sao Bernardo
- Ponte Nova
- Navegantes
- Sao Gabriel

Margem direita / Sao Cristovao:

- Sagrada Familia
- Nossa Senhora Salete
- Cidade Jardim
- Sao Joaquim
- Sao Bras
- Panorama
- Cristo Rei

Cotas/eventos citados pelo CENACID:

| Evento | Regua/nivel citado | Cota altimetrica citada |
|---|---:|---:|
| 1935 | nao informa regua | 747,8 m |
| 1970 | nao informa regua | 746,0 m |
| 1983 | 10,42 m | 750,04 m |
| 1992 | 9,8 m | nao informa |
| 2014 | 8,15 m | nao informa |

Importante:

- O valor 9,8 m para 1992 no CENACID provavelmente e erro de digitacao/transcricao.
- HidroWeb/ANA indica 8,90 m.
- Webnode local indica 8,89 m e cota 748,50 m.
- O proprio padrao de conversao do CENACID para 1983 usa zero 739,62 m, consistente com o zero 739,61 m. Se 1992 fosse 9,8 m, a cota seria 749,41/749,42 m, divergindo do material local.

Texto recomendado:

```text
Algumas fontes secundarias citam 9,8 m para 1992, mas a serie consistida da ANA/HidroWeb e material tecnico local indicam 8,89/8,90 m. Por isso, adotamos 8,90 m como referencia.
```

### Gazeta do Povo

URL:

https://www.gazetadopovo.com.br/vida-e-cidadania/sob-a-agua-uniao-da-vitoria-teme-repeticao-da-cheia-de-92-9ku7d0uit4umewjpbon482p1q/

Uso:

- Materia de 2014 compara a cheia de 2014 com a grande cheia de 1992.
- Cita que Dago Woehl tinha anotado os niveis de 1983 e 1992 para comparar.
- Cita explicitamente 1983 = 10,42 m.
- Nao confirma 9,8 m para 1992.

### Colmeia, Vvale, UBPlay

Colmeia:

- Lista de areas/ruas em alerta quando a previsao era de 6,79 m.
- Cita Limeira, Rio D'Areia, Navegantes, trechos abaixo de Bento Munhoz, Joaquim Tavora, Padre Saporiti etc.

Vvale:

- Em 12/10/2023 publicou relatorio:
  - Cota Rio Iguacu: 746,484 m.
  - Nivel na regua: 6,874 m.
- Isto confirma conversao aproximada: 746,484 - 6,874 = 739,610 m.
- Em 18/10/2023 registrou enchente de 2023 acima de 2014.

UBPlay:

- Materia sobre postes com marcas historicas de cheias.
- Diz que havia cerca de 300 postes com marcacoes de diferentes cotas de inundacao, feitas por engenheiros da CORPRERI, com base em 1983 e 1992.
- Nao traz tabela das cotas nem bairros especificos.

## Divergencia 1992

Conclusao consolidada:

| Fonte | Valor 1992 |
|---|---:|
| ANA/HidroWeb estacao 65310000 | 8,90 m |
| Webnode / texto tecnico local | 8,89 m, cota 748,50 m |
| CENACID/UFPR | 9,8 m, sem cota |

Interpretacao:

- O valor correto/mais defensavel e 8,89/8,90 m.
- O 9,8 m do CENACID parece erro de digitacao.
- Para o site, usar: "1992: 8,89/8,90 m na regua, cota aproximada 748,50 m."

## Cota por rua

Ainda nao foi encontrada tabela "rua -> cota".

O que existe:

- Cotas de zoneamento.
- Cotas de eventos historicos.
- Mapas de inundacao citados em estudos.
- Base cartografica e pontos cotados citados no ABRH214.

Para obter cota por rua, e necessario cruzar nivel do rio/cotas com topografia urbana:

- curvas de nivel;
- MDT/LiDAR;
- base cartografica 1:2.000;
- pontos cotados;
- sistema viario;
- mapas de inundacao CORPRERI/JICA/COPEL/Tucci e Villanueva.

Orgaos/locais para pedir:

- COPEL / hidrologia / acervo tecnico.
- Lactec / CEHPAR.
- Prefeitura de Uniao da Vitoria.
- Prefeitura de Porto Uniao.
- Defesa Civil Municipal/Estadual.
- IAT / antigo Instituto das Aguas.
- Arquivo Publico do Parana.
- ANA, para series hidrologicas, mas provavelmente nao cota de rua.

## Email para ANA / API HidroWeb

Foi elaborado email para telemetria@ana.gov.br pedindo acesso a API HidroWeb.

Dados do usuario:

- Nome: Thiago Jorge Iwanko
- CPF: 059.339.459-35
- Email: thiagoiwanko@gmail.com
- Projeto: https://rioiguacu.com

**Status:** acesso liberado pela ANA (resposta recebida em 07/07/2026). Identificador de login = CPF sem pontuacao (05933945935). A senha em si NAO fica registrada aqui nem em nenhum arquivo do repo, pois `rioiguacu` e publico no GitHub (github.com/thiagoiwanko/rioiguacu) com Actions rodando a cada 5 minutos. Se for automatizar a coleta via API, guardar a senha como GitHub Actions Secret (ex: `ANA_API_PASSWORD`), nunca em texto no codigo.

**Nota sobre dois cadastros/sistemas:**

- Primeiro e-mail (resposta generica) deu 401 "Usuario sem permissao de acesso ao modulo" ao testar `/EstacoesTelemetricas/OAUth/v1` no Swagger (`hidrowebservice`).
- Segundo cadastro veio da `telemetria@ana.gov.br`, em resposta ao pedido enviado em 03/07/2026 (assunto "Solicitacao de acesso a API do HidroWeb"). Esse cadastro e vinculado ao portal HidroTelemetria: https://www.snirh.gov.br/hidrotelemetria (login: https://www.snirh.gov.br/hidrotelemetria/Login2.aspx, recuperacao de senha pela opcao "Esqueceu sua senha?"). O e-mail confirma explicitamente que essa credencial da acesso tambem a API Hidrowebservice (`https://www.ana.gov.br/hidrowebservice/swagger-ui.html`), com tutorial na aba "Documentos" do portal.
- Identificador continua sendo o CPF sem pontuacao (05933945935); a senha foi trocada (nova senha recebida em 07/07/2026, nao registrada aqui).
- **Confirmado em 07/07/2026:** a segunda credencial resolve o erro 401 de permissao de modulo. Chamada `/EstacoesTelemetricas/OAUth/v1` retornou 200 OK com token valido (validade 60 min). Chamada `/EstacoesTelemetricas/HidroinfoanaSerieTelemetricaDetalhada/v1` para a 65310000 retornou 200 OK mas `"items": []` ("Nao houve retorno de registros"), mesmo com `RangeIntervaloDeBusca` variando.
- **Causa raiz encontrada via `/EstacoesTelemetricas/HidroInventarioEstacoes/v1` (codigoestacao=65310000):** a estacao 65310000 (Uniao da Vitoria, responsavel COPEL, operadora IAT-PR, rio 65100000/Rio Iguacu, bacia 65) tem `"Tipo_Estacao_Telemetrica": "0"` e `"Data_Periodo_Telemetrica_Inicio"/"Fim": null`. Ou seja, **nunca foi cadastrada como estacao telemetrica** — e por isso a rota `EstacoesTelemetricas` sempre retorna vazio pra ela, independente da janela de data. E' consistente com o que ja se sabia: escala/regua manual parou em 1999-09, descarga liquida vai ate 2020-07, serie historica (Cotas.csv) analisada vai ate 2023-12-31.
- **Implicacao pratica:** a API `hidrowebservice` (modulo EstacoesTelemetricas) NAO serve pra automatizar o nivel atual/tempo-real do rio via a 65310000, porque essa estacao especifica nao tem telemetria. Precisa: (a) achar outra estacao telemetrica na mesma bacia/rio proxima a Uniao da Vitoria/Porto Uniao (`Tipo_Estacao_Telemetrica: "1"`), OU (b) manter a fonte atual do `scrape.py` (Copel/SIMEPAR local) pra tempo real e usar a API da ANA só pra dados historicos/consistidos da 65310000 (que e o que ela realmente oferece).
- **Candidatas telemetricas testadas em 07/07/2026** (via `/EstacoesTelemetricas/HidroInventarioEstacoes/v1`, busca no portal HidroTelemetria por estacoes proximas a Uniao da Vitoria):
  - `65309900` ETA UNIAO DA VITORIA — SANEPAR — Tipo_Estacao_Telemetrica: 0 (nao serve).
  - `65310000` UNIAO DA VITORIA — COPEL/IAT-PR — Tipo_Estacao_Telemetrica: 0 (a que ja sabiamos, nao serve).
  - `65310001` **UHE GOV. BENTO MUNHOZ UNIAO DA VITORIA** — responsavel F.D.A. — Tipo_Estacao_Telemetrica: **1** (telemetrica desde 1997-06, ainda ativa, Operando: 1). Mesmo prefixo `653` da 65310000 → **RIO IGUACU**, mesma localizacao/trecho. **Melhor candidata pra tempo real.**
  - `65415000` FAZENDA MARACANA — COPEL/IAT-PR — Tipo_Estacao_Telemetrica: 0.
  - `65415001` PALMITAL DO MEIO — COPEL/SIMEPAR — Tipo_Estacao_Telemetrica: 1 (telemetrica), mas prefixo `6541` = **RIO PALMITAL** (afluente), fora de escopo — nao e o Rio Iguacu.
  - Proximo passo: confirmar que `65310001` retorna cota/vazao reais via `HidroinfoanaSerieTelemetricaAdotada/v1` antes de trocar o `scrape.py` pra usar essa fonte.
- **Erro 417 EXPECTATION_FAILED em 07/07/2026:** apos varias autenticacoes seguidas (Swagger + reexecucoes do script em poucos minutos), o `/OAUth/v1` passou a retornar 417. Bate com o aviso do manual: "Requisicoes de autenticacao em alta frequencia sao monitoradas e podem resultar no bloqueio automatico do IP". **Licao pra automacao futura:** cachear o token entre execucoes (validade 60 min) — nunca re-autenticar a cada chamada, especialmente rodando a cada 5 min via GitHub Actions. Esperar alguns minutos antes de retestar apos esse erro.
- **Nota tecnica sobre a rota `HidroinfoanaSerieTelemetricaDetalhada/v1`:** funciona manualmente pelo Swagger UI (retornando 200) mas retorna 400 Bad Request quando chamada via `requests` do Python com os mesmos parametros. Suspeita: a biblioteca `requests` codifica espaco como `+` nos nomes dos parametros (`Tipo Filtro Data`, `Range Intervalo de busca` — nomes com espaco, um quirk da definicao v2 do Swagger da ANA), enquanto o navegador manda `%20`; a rota pode exigir `%20` especificamente. Nao resolvido ainda — precisa investigar mais se for automatizar via essa rota especifica.
- **Confirmado via portal (nao via API) em 07/07/2026:** a estacao 65310001 (UHE Gov. Bento Munhoz Uniao da Vitoria) TEM dado real e recente. Fonte: portal "Sistema HIDRO - Telemetria" (`snirh.gov.br/hidrotelemetria`) → menu "Visualizar Dados" → "Ultimos Dados" → filtro por Municipio "Uniao da Vitoria" → Tipo de Informacao "Nivel". Resultado as 07/07/2026 15:00: **Nivel = 459,4 cm** (ultimo), com serie de tendencia: 4h atras 460,1 cm / 8h 461,8 cm / 12h 463,0 cm / 24h 465,6 cm / 96h 473,7 cm — ou seja, em queda lenta, classificado pelo painel como "Estado normal". Dados parecem atualizar a cada ~15-60 min.
- **Zero de regua CONFIRMADO em 07/07/2026, cruzando com o proprio site da Copel (bacia-iguacu.jsf, a mesma pagina que o `scrape.py` ja raspa):** os valores de "Leitura da regua (m)" publicados pela Copel batem EXATAMENTE, hora a hora, com o "Nivel adotado (cm)" da estacao 65310001 na API/portal da ANA. Exemplos do mesmo dia 07/07/2026: 15h Copel=4,594 m / ANA=459,40 cm; 14h Copel=4,594/ANA=459,40; 13h Copel=4,598/ANA=459,80; 12h Copel=4,602/ANA=460,20; 11h Copel=4,601/ANA=460,10; 10h Copel=4,610/ANA=461,00; 09h Copel=4,612/ANA=461,20 — match perfeito em todos os horarios. Alem disso a Copel mostra tambem "Nivel de agua (m)" (cota altimetrica) = 744,199 quando regua = 4,589 → 744,199 - 4,589 = 739,610 m, confirmando que e o MESMO zero historico (739,61 m) ja usado no projeto. **Conclusao definitiva: a estacao 65310001 da ANA e a fonte oficial telemetrica equivalente ao que a Copel publica pra Uniao da Vitoria — mesmo datum, mesma leitura, dado confiavel pra usar no site.**
- Ha tambem uma segunda estacao no mesmo relatorio do portal HidroTelemetria, `02651084 - PZ_UNIAO DA VITORIA`, com valores negativos (ex: -462,0 cm) e sem vazao — e piezometro (medicao de agua subterranea), fora de escopo, nao serve como nivel do rio.
- O portal "Ultimos Dados" tem um botao de exportar (icone verde tipo planilha) — pode ser fonte alternativa mais estavel que a API REST pra automatizar, se a API continuar com os problemas de parametro/rate-limit acima.
- **Confirmacao final em 07/07/2026 via "Serie Historica" do portal:** a 65310001 tem coluna "Vazao (m3/s)" preenchida (~1256-1276 m3/s no periodo observado), consistente com estacao fluviometrica de verdade. A 02651084 (PZ_UNIAO DA VITORIA) NAO tem vazao (coluna vazia) — confirma que e piezometro, fora de escopo pro nivel do rio. A 65310001 tambem expoe Bateria (V) e Temperatura Interna do equipamento (util pra monitorar saude do sensor numa automacao futura) e os dados vem qualificados como "Aprovado" (verde). **Conclusao: 65310001 e a estacao correta pra automatizar o nivel do Rio Iguacu em Uniao da Vitoria.** Falta so confirmar o zero de regua dela com a COPEL/ANA antes de publicar valores absolutos no site.
- Script de teste local: `teste_api_ana.py` (fora do repo, na pasta de trabalho) — nao commitar, contem credenciais.
- Servico antigo `telemetriaws1.ana.gov.br` (SOAP, sem login) esta sendo descontinuado; prazo estendido ate 30/06/2026, ja vencido na data de hoje (07/07/2026) — nao usar como alternativa, migrar definitivamente para o `hidrowebservice` REST.

Motivacao:

- Uso de fonte oficial, padronizada e confiavel.
- Atualizacao automatica dos niveis do Rio Iguacu.
- Utilidade publica para Uniao da Vitoria/Porto Uniao em periodos de enchente.

## Recomendacoes para o site Rio Iguacu

### Escala de risco proposta

Usar cota/regua:

| Nivel regua | Cota | Mensagem sugerida |
|---:|---:|---|
| 5,09 m | 744,70 m | cheia padrao ordinaria |
| 6,89 m | 746,50 m | limite importante de zoneamento / cheia de 10 anos |
| 7,27 m | 746,88 m | referencia de 1993 |
| 8,89/8,90 m | 748,50 m | cheia de 1992 |
| 10,42 m | 750,03/750,04 m | cheia de 1983 |

### Alertas de transparencia

Nao afirmar "rua X alaga com Y" sem mapa/topografia.

Usar linguagem:

```text
Esta regua mostra niveis historicos e referencias de zoneamento. A situacao real em cada rua depende da cota do terreno, drenagem local, aterros, remanso e mapas de inundacao.
```

### Funcionalidade util

Calculadora de marca historica:

- Perguntar: "Em 1992, ate onde a agua chegou na sua casa?"
- Perguntar: "Quantos centimetros abaixo/acima dessa marca fica seu piso?"
- Calcular nivel estimado em que a agua chega ao piso.

Formula:

```text
nivel_piso = 8,89 m - distancia_marca_1992_ate_piso
```

Se a marca for 2014 ou 1983, usar o evento correspondente.

## Links importantes

- HidroWeb/SNIRH: https://www.snirh.gov.br/hidroweb/serieshistoricas
- ANA Monitoramento Hidrologico: https://www.gov.br/ana/pt-br/assuntos/monitoramento-e-eventos-criticos/monitoramento-hidrologico
- ABRH214: https://files.abrhidro.org.br/Eventos/Trabalhos/149/ABRH214.pdf
- CENACID/UFPR: https://cenacid.ufpr.br/wp-content/uploads/2017/10/Avalia%C3%A7%C3%A3o-das-%C3%A1reas-atingidas-pelas-inunda%C3%A7%C3%B5es-e-alagamentos-em-Uni%C3%A3o-da-Vit%C3%B3ria-PR..pdf
- Webnode - Conhecendo e Convivendo com Enchentes: https://portouniao.webnode.com.br/conhecendo%20porto%20uni%C3%A3o/conhecendo-e-convivendo-com-enchentes/
- Webnode - Represa de Foz do Areia: https://portouniao.webnode.com.br/conhecendo%20porto%20uni%C3%A3o/conhecendo-e-convivendo-com-enchentes/newscbm_151720/4/
- Webnode - Zoneamento: https://portouniao.webnode.com.br/conhecendo%20porto%20uni%C3%A3o/conhecendo-e-convivendo-com-enchentes/newscbm_151720/6/
- Webnode - Programa SEC-CORPRERI: https://portouniao.webnode.com.br/conhecendo%20porto%20uni%C3%A3o/conhecendo-e-convivendo-com-enchentes/newscbm_151720/10/
- Webnode - Conclusao: https://portouniao.webnode.com.br/conhecendo%20porto%20uni%C3%A3o/conhecendo-e-convivendo-com-enchentes/newscbm_151720/11/
- Webnode - Enchentes: https://portouniao.webnode.com.br/not/enchentes/
- Gazeta do Povo 2014: https://www.gazetadopovo.com.br/vida-e-cidadania/sob-a-agua-uniao-da-vitoria-teme-repeticao-da-cheia-de-92-9ku7d0uit4umewjpbon482p1q/

## Planilha de estudo histórico (11/07/2026)

Gerada `dados-historicos/rio_iguacu_historico_65310000.xlsx` a partir do CSV oficial da ANA/HidroWeb (estação 65310000, série "Cotas", baixada sem login em `snirh.gov.br/hidroweb/serieshistoricas`, aba "Dados Convencionais"). Cobre 34.150 dias, 22/05/1930 a 31/12/2023 (reorganizado do formato "largo" original — 1 linha/mês, colunas Cota01-31 — para 1 linha/dia). Os 10 maiores picos foram conferidos contra a tabela já documentada acima (1983, 1992, 2023, 1935, 2014, 2019, 1957, 1993, 1998, 2010) e batem exatamente.

Abas: Série Diária, Resumo Mensal (com fórmulas COUNTIFS/AVERAGEIF/_xlfn.MAXIFS/MINIFS que recalculam se os dados mudarem), Picos Anuais, Ranking Sazonal, Episódios de Cheia (nível ≥ 6,89 m), Leia-me.

Achado principal: outubro e junho concentram a maioria das cheias (outubro teve o pico anual em 20 dos 94 anos e o maior número de episódios de cheia ≥6,89 m; junho é o 2º). Fevereiro a abril são historicamente os meses mais tranquilos.

**Buraco de dados 2024–hoje:** a série oficial "Cotas" da 65310000 termina em 31/12/2023 (é onde a ANA parou de publicar essa série revisada pra essa estação, não uma limitação da extração). Pra cobrir 2024 em diante seria preciso a estação telemétrica 65310001, mas o portal público limita a 90 dias por download e exige reCAPTCHA a cada requisição — não é automatizável (não resolvo captcha). Decisão do usuário em 11/07/2026: (a) automatizar só daqui pra frente via `historico_diario.csv` (ver acima, v1.20); (b) usuário faz o backfill manual 2024–hoje ele mesmo (~11 downloads de até 90 dias cada, estação 65310001, aba "Dados Telemétricos" do portal) e envia os arquivos pra mesclar na planilha depois. Backfill ainda não recebido/mesclado nesta sessão.

## Cuidados ao continuar

- Nao tratar o valor 9,8 m de 1992 como correto sem ressalva.
- Nao confundir cota altimetrica com nivel de regua.
- Converter sempre usando zero 739,61 m, salvo fonte explicita diferente.
- Nao prometer cota por rua ate obter mapa/topografia urbana.
- Distinguir dado oficial ANA/HidroWeb de fonte historica/local.
- Manter as fontes e incertezas visiveis no site.

