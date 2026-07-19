import json
import os
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import quote
from zoneinfo import ZoneInfo

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


APP_VERSION = "GitHub Actions 1.0"
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data.json"
LOG_PATH = BASE_DIR / "monitor_web.log"
ANA_TOKEN_CACHE_PATH = BASE_DIR / ".ana_token_cache.json"
HISTORICO_DIARIO_PATH = BASE_DIR / "historico_diario.csv"
HISTORICO_DIARIO_CABECALHO = "Data;NivelMaximo_m;NivelMinimo_m;NivelUltimo_m;VazaoUltimo_m3s;Fonte\n"

URL_HISTORICO_COPEL = "https://www.copel.com/mhbweb/paginas/bacia-iguacu.jsf"
URL_HISTORICO_ANA = "https://www.snirh.gov.br/hidrotelemetria/"
URL_PREVISAO = "https://www.copel.com/mhbweb/paginas/previsao.jsf"

# API oficial da ANA (HidroWebservice). Estação 65310001 = UHE Gov. Bento Munhoz
# União da Vitória, confirmada em 07/2026 batendo hora a hora com o que a Copel
# publica (mesmo datum, zero 739,61 m). Não tem previsão -- só dado medido real,
# por isso a previsão continua vindo da Copel independentemente disso funcionar.
# Credenciais NUNCA ficam neste arquivo: vêm de variável de ambiente
# (ANA_API_LOGIN / ANA_API_SENHA), configuradas como GitHub Actions Secret em
# produção ou exportadas manualmente pra teste local. Se não estiverem
# configuradas, ou se a chamada falhar por qualquer motivo, cai automaticamente
# pro scraping da Copel (comportamento original, inalterado).
ANA_BASE = "https://www.ana.gov.br/hidrowebservice"
ANA_CODIGO_ESTACAO = 65310001
ANA_ZERO_REGUA_M = 739.61

JANELA_HISTORICO_HORAS = 48
JANELA_PREVISAO_HORAS = 48
TIMEOUT_COLETA_SEGUNDOS = 90
FUSO_BR = ZoneInfo("America/Sao_Paulo")


def agora_br():
    return datetime.now(FUSO_BR).replace(tzinfo=None)


ESPERA_NOVA_TENTATIVA_SEGUNDOS = 30

COTAS_BAIRROS = [
    (1.29, "Menor nível histórico - estiagem de 2020"),
    (4.67, "Cidade Jardim"),
    (5.08, "Rio D'Areia"),
    (5.20, "São Basílio Magno"),
    (5.26, "Nossa Senhora do Rocio"),
    (5.39, "Navegantes"),
    (5.39, "São Bernardo"),
    (5.39, "Ponte Nova"),
    (5.45, "Sagrada Família"),
    (5.54, "São Joaquim"),
    (6.31, "Bento Munhoz da Rocha"),
    (6.39, "Limeira"),
    (6.39, "São Gabriel"),
    (6.39, "Bom Jesus"),
    (6.42, "Cristo Rei"),
    (7.39, "Centro - União da Vitória"),
    (7.82, "Enchente de 2019"),
    (8.12, "Enchente de 2014"),
    (8.16, "Enchente de 1935"),
    (8.37, "Enchente de 2023"),
    (8.39, "Nossa Senhora da Salete"),
    (8.84, "Panorama"),
    (8.90, "Enchente de 1992"),
    (10.42, "Enchente de 1983"),
]

# Níveis de alerta definidos por análise estatística da série histórica ANA
# (65310000, 1930-2023): média 2,67 m, desvio padrão 1,08 m, modelo de
# distribuição normal validado por contagem direta de frequência real na
# série. Ver proposta completa em FAQ_NIVEIS_ALERTA_PROPOSTA.md (18/07/2026).
#   Observação  3,70 m = média + 1 desvio padrão (P85)
#   Atenção     4,20 m = percentil 90
#   Alerta      5,00 m = média + 2 desvios padrão (P95)
#   Emergência  5,50 m = P97,5
#   Enchente    6,50 m = ~1 em cada 10 endereços da cidade abaixo da régua
COTAS_ALERTA_DEFESA_CIVIL = [
    (3.70, "OBSERVAÇÃO"),
    (4.20, "ATENÇÃO"),
    (5.00, "ALERTA"),
    (5.50, "EMERGÊNCIA"),
    (6.50, "ENCHENTE"),
]

# Escalada por velocidade: a série histórica mostra subidas abruptas (1,78 m
# em 24h em 1992; 3,34 m em 48h em 2014). Quando o rio sobe LIMIAR_SUBIDA_24H_M
# ou mais em 24 horas -- taxa superada em ~1% de todas as subidas desde 1930 --
# o alerta é elevado em um degrau, independentemente do nível absoluto da régua.
LIMIAR_SUBIDA_24H_M = 0.85


def log(mensagem):
    linha = f"[{agora_br().strftime('%d/%m/%Y %H:%M:%S')}] {mensagem}\n"
    try:
        LOG_PATH.write_text(
            (LOG_PATH.read_text(encoding="utf-8") if LOG_PATH.exists() else "") + linha,
            encoding="utf-8",
        )
    except Exception:
        pass


def iso(dt):
    return dt.isoformat(timespec="minutes")


def parse_numero(valor):
    return float(valor.replace(",", "."))


def _ana_query_string(params):
    # A API da ANA exige espaço codificado como %20 nos NOMES dos parâmetros
    # ("Código da Estação", "Range Intervalo de busca" etc). requests.get(params=dict)
    # usa '+' por padrão (estilo application/x-www-form-urlencoded), que a API
    # rejeita com 400 Bad Request -- por isso a URL é montada manualmente aqui.
    return "&".join(f"{quote(k, safe='')}={quote(str(v), safe='')}" for k, v in params.items())


def _ana_token_valido():
    try:
        cache = json.loads(ANA_TOKEN_CACHE_PATH.read_text(encoding="utf-8"))
        expira_em = datetime.fromisoformat(cache["expira_em"])
        if datetime.now() < expira_em:
            return cache["token"]
    except Exception:
        pass
    return None


def _ana_autenticar(identificador, senha):
    token = _ana_token_valido()
    if token:
        return token

    resp = requests.get(
        f"{ANA_BASE}/EstacoesTelemetricas/OAUth/v1",
        headers={"Identificador": identificador, "Senha": senha},
        timeout=20,
    )
    resp.raise_for_status()
    token = resp.json()["items"]["tokenautenticacao"]

    # Cacheia por 55 min (validade real é 60 min) pra nunca reautenticar a
    # cada execução do GitHub Actions -- autenticação em alta frequência é
    # monitorada pela ANA e pode resultar em bloqueio de IP (417).
    try:
        ANA_TOKEN_CACHE_PATH.write_text(
            json.dumps({
                "token": token,
                "expira_em": iso(datetime.now() + timedelta(minutes=55)),
            }),
            encoding="utf-8",
        )
    except Exception:
        pass

    return token


def _parse_data_hora_ana(valor):
    valor = valor.split(".")[0]
    return datetime.strptime(valor, "%Y-%m-%d %H:%M:%S")


def coletar_via_ana():
    """Busca o histórico via API oficial da ANA (estação 65310001). Retorna None
    (sem lançar exceção) se as credenciais não estiverem configuradas ou se
    qualquer etapa falhar -- nesses casos coletar_uma_vez() cai pro scraping
    da Copel automaticamente, sem afetar a previsão (que é Copel-only)."""
    identificador = os.environ.get("ANA_API_LOGIN")
    senha = os.environ.get("ANA_API_SENHA")
    if not identificador or not senha:
        log("ANA: credenciais não configuradas (ANA_API_LOGIN/ANA_API_SENHA); usando Copel.")
        return None

    try:
        token = _ana_autenticar(identificador, senha)
        query = _ana_query_string({
            "Código da Estação": ANA_CODIGO_ESTACAO,
            "Tipo Filtro Data": "DATA_LEITURA",
            "Range Intervalo de busca": "DIAS_2",
        })
        resp = requests.get(
            f"{ANA_BASE}/EstacoesTelemetricas/HidroinfoanaSerieTelemetricaAdotada/v1?{query}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=20,
        )
        resp.raise_for_status()
        payload = resp.json()
        itens = payload.get("items") or []
        if payload.get("code") != 200 or not itens:
            log(f"ANA: resposta sem itens utilizáveis ({payload.get('message')}); usando Copel.")
            return None

        itens = sorted(itens, key=lambda item: item["Data_Hora_Medicao"])
        historico = []
        chuva_acumulada = 0.0
        for item in itens:
            regua_m = round(float(item["Cota_Adotada"]) / 100, 3)
            chuva_mm = round(float(item.get("Chuva_Adotada", 0) or 0), 1)
            chuva_acumulada = round(chuva_acumulada + chuva_mm, 1)
            historico.append({
                "data_hora": iso(_parse_data_hora_ana(item["Data_Hora_Medicao"])),
                "regua_m": regua_m,
                "nivel_agua_m": round(regua_m + ANA_ZERO_REGUA_M, 3),
                "vazao_m3s": int(float(item.get("Vazao_Adotada", 0) or 0)),
                "chuva_mm": chuva_mm,
                "chuva_acumulada_mm": chuva_acumulada,
            })

        if not historico:
            return None
        log(f"ANA: {len(historico)} medições obtidas com sucesso (estação {ANA_CODIGO_ESTACAO}).")
        return historico
    except Exception as exc:
        log(f"ANA: falha na coleta ({exc}); usando Copel.")
        return None


def abrir_navegador():
    opcoes = Options()
    opcoes.add_argument("--headless=new")
    opcoes.add_argument("--window-size=1600,1000")
    opcoes.add_argument("--disable-gpu")
    opcoes.add_argument("--no-sandbox")
    opcoes.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=opcoes)
    driver.set_page_load_timeout(TIMEOUT_COLETA_SEGUNDOS)
    return driver


def clicar_uniao_da_vitoria_se_existir(driver):
    xpaths = [
        "//*[contains(text(),'União da Vitória')]",
        "//*[contains(text(),'UNIAO DA VITORIA')]",
        "//*[contains(text(),'UNIÃO DA VITÓRIA')]",
    ]

    for xp in xpaths:
        try:
            for elemento in driver.find_elements(By.XPATH, xp):
                if elemento.is_displayed():
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elemento)
                    time.sleep(0.5)
                    elemento.click()
                    time.sleep(4)
                    return True
        except Exception:
            pass

    return False


def extrair_medicoes(texto):
    dados = []
    padrao = re.compile(
        r"(\d{2}/\d{2}/\d{2})\s+(\d{2})h\s+"
        r"([\d,]+)\s+([\d,]+)\s+([\d.]+)\s+([\d,]+)\s+([\d,]+)"
    )

    for linha in texto.splitlines():
        m = padrao.search(linha.strip())
        if not m:
            continue
        data, hora, regua, nivel_agua, vazao, chuva, chuva_acum = m.groups()
        try:
            data_hora = datetime.strptime(f"{data} {hora}:00", "%d/%m/%y %H:%M")
            dados.append({
                "data_hora": iso(data_hora),
                "regua_m": parse_numero(regua),
                "nivel_agua_m": parse_numero(nivel_agua),
                "vazao_m3s": int(vazao.replace(".", "")),
                "chuva_mm": parse_numero(chuva),
                "chuva_acumulada_mm": parse_numero(chuva_acum),
            })
        except Exception:
            pass

    unicos = {item["data_hora"]: item for item in dados}
    return sorted(unicos.values(), key=lambda item: item["data_hora"])


def _parse_data_hora(data_txt, hora_txt):
    hora_txt = hora_txt.replace("h", ":00")
    formato = "%d/%m/%y %H:%M" if len(data_txt.split("/")[-1]) == 2 else "%d/%m/%Y %H:%M"
    return datetime.strptime(f"{data_txt} {hora_txt}", formato)


def extrair_previsao(texto):
    dados = []
    padrao_data_hora = re.compile(r"(\d{2}/\d{2}/(?:\d{2}|\d{4}))\s+(\d{2}(?::\d{2}|h))")
    padrao_numero = re.compile(r"(?<!\d)(\d{1,2},\d{1,3})(?!\d)")

    for linha in texto.splitlines():
        linha = linha.strip()
        m = padrao_data_hora.search(linha)
        if not m:
            continue

        numeros = [parse_numero(n) for n in padrao_numero.findall(linha)]
        numeros = [n for n in numeros if 0 <= n <= 20]
        if not numeros:
            continue

        try:
            dados.append({
                "data_hora": iso(_parse_data_hora(m.group(1), m.group(2))),
                "regua_sem_chuva_m": numeros[0],
                "regua_com_chuva_m": numeros[1] if len(numeros) >= 2 else None,
            })
        except Exception:
            pass

    unicos = {item["data_hora"]: item for item in dados}
    return sorted(unicos.values(), key=lambda item: item["data_hora"])


def coletar_texto(url):
    log(f"Iniciando coleta: {url}")
    driver = abrir_navegador()
    try:
        driver.get(url)
        time.sleep(7)
        clicar_uniao_da_vitoria_se_existir(driver)
        texto = driver.find_element(By.TAG_NAME, "body").text
        log(f"Coleta concluída: {url} ({len(texto)} caracteres)")
        return texto
    finally:
        try:
            driver.quit()
        except Exception:
            pass


# Degraus de situação, do mais baixo ao mais alto. O primeiro (0.0) é a
# linha de base "normal" -- não faz parte de COTAS_ALERTA_DEFESA_CIVIL porque
# não é um nível de alerta, é a ausência de alerta.
NIVEIS_SITUACAO = [(0.0, "NÍVEL NORMAL - monitoramento diário")] + COTAS_ALERTA_DEFESA_CIVIL


def _tier_por_nivel(regua):
    tier = 0
    for i, (limite, _) in enumerate(NIVEIS_SITUACAO):
        if regua >= limite:
            tier = i
    return tier


def definir_situacao(regua, historico=None):
    tier = _tier_por_nivel(regua)

    # Escalada por velocidade: se a subida nas últimas 24h já atingiu o
    # limiar, eleva um degrau mesmo que o nível absoluto ainda não justifique.
    if historico:
        try:
            agora_dt = datetime.fromisoformat(historico[-1]["data_hora"])
            ref_24h = agora_dt - timedelta(hours=24)
            niveis_24h = [
                item["regua_m"] for item in historico
                if datetime.fromisoformat(item["data_hora"]) >= ref_24h
                and isinstance(item.get("regua_m"), (int, float))
            ]
            if niveis_24h:
                subida_24h = regua - min(niveis_24h)
                if subida_24h >= LIMIAR_SUBIDA_24H_M and tier < len(NIVEIS_SITUACAO) - 1:
                    tier += 1
        except Exception:
            pass

    return NIVEIS_SITUACAO[tier][1]


def calcular_tendencia(historico):
    if len(historico) < 2:
        return {"texto": "Sem dados suficientes para tendência.", "delta": 0, "direcao": "estavel"}
    delta = historico[-1]["regua_m"] - historico[-2]["regua_m"]
    if delta == 0:
        return {"texto": "Estável", "delta": 0, "direcao": "estavel"}
    direcao = "subindo" if delta > 0 else "baixando"
    verbo = "Subindo" if delta > 0 else "Baixando"
    abs_delta_m = abs(delta)
    # Abaixo de 1 m/h (a grande maioria do tempo), mostra em cm -- mais fácil
    # de ler que um decimal de metro ("0,6 cm" em vez de "0.006 m"). Taxas
    # raras/extremas acima disso continuam em metros.
    if abs_delta_m < 1:
        valor = f"{abs_delta_m * 100:.1f}".replace(".", ",")
        texto = f"{verbo} cerca de {valor} cm por hora"
    else:
        valor = f"{abs_delta_m:.2f}".replace(".", ",")
        texto = f"{verbo} cerca de {valor} m por hora"
    return {"texto": texto, "delta": delta, "direcao": direcao}


def verificar_alerta_previsao(historico, previsao):
    if not historico or not previsao:
        return "Sem estimativa disponível para as próximas 48 horas."
    agora_base = datetime.fromisoformat(historico[-1]["data_hora"])
    limite = agora_base + timedelta(hours=JANELA_PREVISAO_HORAS)
    valores = []
    for item in previsao:
        data_hora = datetime.fromisoformat(item["data_hora"])
        if agora_base < data_hora <= limite:
            valores.append(item["regua_sem_chuva_m"])
            if item.get("regua_com_chuva_m") is not None:
                valores.append(item["regua_com_chuva_m"])
    if not valores:
        return "Sem estimativa disponível para as próximas 48 horas."
    maior = max(valores)
    valor_fmt = f"{maior:.2f}".replace(".", ",")
    # Linguagem deliberadamente não-oficial: isto é uma projeção simples a
    # partir do histórico recente + chuva, não uma previsão hidrológica
    # validada -- não deve soar como um boletim oficial da Defesa Civil/ANA.
    return f"Estimativa automática para as próximas 48 horas: {valor_fmt} m. Não é uma previsão oficial."


def montar_payload(historico, previsao, fonte_historico, url_historico):
    if not historico:
        raise RuntimeError("nenhuma medição foi encontrada (nem ANA, nem Copel)")

    ultima = historico[-1]
    regua = float(ultima["regua_m"])
    return {
        "versao": APP_VERSION,
        "fonte": fonte_historico,
        "url_historico": url_historico,
        "atualizado_em": iso(agora_br()),
        "historico": historico,
        "previsao": previsao,
        "ultima": ultima,
        "situacao": definir_situacao(regua, historico),
        "tendencia": calcular_tendencia(historico),
        "alerta_previsao": verificar_alerta_previsao(historico, previsao),
        "previsao_disponivel": bool(previsao),
        "cotas_bairros": [{"nivel": nivel, "descricao": desc} for nivel, desc in COTAS_BAIRROS],
        "cotas_alerta": [{"nivel": nivel, "descricao": desc} for nivel, desc in COTAS_ALERTA_DEFESA_CIVIL],
        "janela_historico_horas": JANELA_HISTORICO_HORAS,
        "janela_previsao_horas": JANELA_PREVISAO_HORAS,
    }


# Nomes de fonte exibidos no site (campo "fonte" do data.json). O app.js lê
# esse texto e mostra dinamicamente, então quando a redundância da Copel
# entra em ação (raro, só nos minutos em que a ANA ainda não fechou a hora)
# o site mostra a fonte real daquela leitura, nunca uma informação fixa/errada.
FONTE_ANA = "ANA – Agência Nacional de Águas e Saneamento Básico (estação telemétrica UHE Gov. Bento Munhoz, União da Vitória)"
FONTE_COPEL = "Copel – Monitoramento Hidrológico (fonte redundante, usada quando a ANA ainda não publicou a leitura da hora)"


def mesclar_historico(historico_novo, historico_anterior):
    """Une o histórico recém-coletado (via ANA ou Copel) com o histórico já
    salvo no data.json da execução anterior, preenchendo por data_hora.

    Sem isso, uma coleta cuja fonte responde com sucesso mas devolve uma
    janela incompleta (ex.: ANA retornando só as horas de hoje, sem ontem)
    substituía o histórico inteiro e "esquecia" horas que já tinham sido
    coletadas com sucesso antes -- mesmo a Copel nunca era chamada pra
    completar, porque tecnicamente a ANA "funcionou" (só que incompleta).

    Com a mesclagem, o histórico do site é cumulativo: uma hora só some da
    janela de JANELA_HISTORICO_HORAS quando fica velha demais, nunca porque
    a coleta desta rodada não trouxe ela de novo. Em caso de conflito no
    mesmo horário, o dado desta execução tem prioridade (mais recente)."""
    por_hora = {item["data_hora"]: item for item in historico_anterior}
    por_hora.update({item["data_hora"]: item for item in historico_novo})
    limite = agora_br() - timedelta(hours=JANELA_HISTORICO_HORAS)
    itens = [item for item in por_hora.values() if datetime.fromisoformat(item["data_hora"]) >= limite]
    return sorted(itens, key=lambda item: item["data_hora"])


def coletar_uma_vez(ultima_anterior=None, historico_anterior=None):
    historico_anterior = historico_anterior or []
    historico = coletar_via_ana()
    fonte_historico = None
    url_historico = URL_HISTORICO_COPEL
    if historico:
        nova_ultima_ana = historico[-1]["data_hora"]
        if ultima_anterior is None or nova_ultima_ana != ultima_anterior:
            fonte_historico = FONTE_ANA
            url_historico = URL_HISTORICO_ANA
        else:
            # A ANA respondeu, mas ainda é o mesmo dado de antes (a hora ainda
            # não fechou lá) -- usa Copel como redundância nesta rodada em vez
            # de reescrever o mesmo horário e fingir que atualizou.
            log(f"ANA: ainda sem dado novo (última segue {nova_ultima_ana}); usando Copel como redundância nesta rodada.")
            historico = None

    if not historico:
        texto_historico = coletar_texto(URL_HISTORICO_COPEL)
        historico = extrair_medicoes(texto_historico)
        fonte_historico = FONTE_COPEL
        url_historico = URL_HISTORICO_COPEL
        log(f"Medições obtidas via {fonte_historico.split(' ')[0]}: {len(historico)}")

    historico = mesclar_historico(historico, historico_anterior)

    # Previsão é exclusiva da Copel -- a ANA não oferece esse dado, então essa
    # parte roda sempre, independentemente da fonte do histórico acima.
    previsao = []
    try:
        texto_previsao = coletar_texto(URL_PREVISAO)
        previsao = extrair_previsao(texto_previsao)
        log(f"Previsões extraídas: {len(previsao)}")
    except Exception as exc:
        log(f"Previsão indisponível: {exc}")

    return montar_payload(historico, previsao, fonte_historico, url_historico)


def carregar_anterior():
    if DATA_PATH.exists():
        try:
            return json.loads(DATA_PATH.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def _ler_historico_diario():
    """Lê o CSV atual do histórico diário (se existir) como um dicionário
    {data: [campos]}, pra permitir upsert por data sem duplicar linhas."""
    linhas = {}
    if HISTORICO_DIARIO_PATH.exists():
        try:
            texto = HISTORICO_DIARIO_PATH.read_text(encoding="utf-8")
        except Exception:
            return linhas
        for linha in texto.splitlines()[1:]:
            if not linha.strip():
                continue
            partes = linha.split(";")
            if len(partes) == 6:
                linhas[partes[0]] = partes
    return linhas


def atualizar_historico_diario(payload):
    """Mantém um registro de 1 linha por dia (nível máximo/mínimo/último e
    vazão do último horário do dia) num CSV crescente no repositório, pra
    dar continuidade ao histórico oficial da ANA (estação 65310000, que só
    vai até 31/12/2023) com os dados telemétricos coletados a partir daqui.

    Roda a cada execução com coleta bem-sucedida. Como o histórico coletado
    cobre as últimas JANELA_HISTORICO_HORAS horas (48h), isso também corrige
    o fechamento do dia anterior caso a última execução daquele dia tenha
    ficado incompleta -- todo dia presente na janela atual é reescrito com
    os dados mais completos disponíveis até agora."""
    try:
        linhas = _ler_historico_diario()
        por_dia = {}
        for item in payload["historico"]:
            data_str = item["data_hora"][:10]
            por_dia.setdefault(data_str, []).append(item)

        fonte_curta = (payload.get("fonte") or "").split(" ")[0] or "?"
        for data_str, itens in por_dia.items():
            itens_ordenados = sorted(itens, key=lambda i: i["data_hora"])
            niveis = [i["regua_m"] for i in itens_ordenados if isinstance(i.get("regua_m"), (int, float))]
            if not niveis:
                continue
            ultimo = itens_ordenados[-1]
            linhas[data_str] = [
                data_str,
                f"{max(niveis):.3f}",
                f"{min(niveis):.3f}",
                f"{ultimo['regua_m']:.3f}",
                str(ultimo.get("vazao_m3s", "")),
                fonte_curta,
            ]

        texto = HISTORICO_DIARIO_CABECALHO
        for data_str in sorted(linhas.keys()):
            texto += ";".join(linhas[data_str]) + "\n"
        HISTORICO_DIARIO_PATH.write_text(texto, encoding="utf-8")
    except Exception as exc:
        log(f"Histórico diário: falha ao atualizar ({exc}).")


def main():
    log("Execução do scrape.py iniciada (GitHub Actions).")
    anterior = carregar_anterior()
    ultima_anterior = None
    historico_anterior = []
    if anterior and anterior.get("dados"):
        ultima_anterior = anterior["dados"].get("ultima", {}).get("data_hora")
        historico_anterior = anterior["dados"].get("historico", [])

    payload = None
    erro = None
    tentativas = 2
    for tentativa in range(1, tentativas + 1):
        try:
            payload = coletar_uma_vez(ultima_anterior, historico_anterior)
        except Exception as exc:
            erro = str(exc)
            log(f"Erro na coleta (tentativa {tentativa}): {exc}")
            payload = None
            break

        nova_ultima = payload["ultima"]["data_hora"]
        if ultima_anterior is None or nova_ultima != ultima_anterior or tentativa == tentativas:
            break
        log(
            f"Ainda sem dado novo (última: {nova_ultima}, fonte: {payload['fonte'].split(' ')[0]}). "
            f"Aguardando {ESPERA_NOVA_TENTATIVA_SEGUNDOS}s para nova tentativa."
        )
        time.sleep(ESPERA_NOVA_TENTATIVA_SEGUNDOS)

    if payload:
        resultado = {"ok": True, "erro": None, "dados": payload}
        log("Dados atualizados com sucesso.")
        atualizar_historico_diario(payload)
    else:
        dados_cache = anterior["dados"] if anterior else None
        resultado = {"ok": False, "erro": erro or "falha desconhecida na coleta", "dados": dados_cache}
        log(f"Falha na coleta, mantendo dado anterior em cache. Erro: {erro}")

    DATA_PATH.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"data.json gravado ({DATA_PATH.stat().st_size} bytes).")


if __name__ == "__main__":
    main()
