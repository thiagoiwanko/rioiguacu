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
    (5.09, "Cheia padrão (nível de atenção inicial)"),
    (6.89, "Área de risco de enchente pelo zoneamento local (cheia de 10 anos)"),
    (7.25, "Cheia de 1993"),
    (8.12, "Cheia de 2014"),
    (8.37, "Cheia de 2023"),
    (8.90, "Grande cheia de 1992"),
    (10.42, "Maior cheia histórica registrada (1983)"),
]

COTAS_ALERTA_DEFESA_CIVIL = [
    (6.89, "Área de risco de enchente (zoneamento local, cheia de 10 anos)"),
    (7.25, "Nível da cheia de 1993"),
    (8.90, "Nível da grande cheia de 1992"),
    (10.42, "Nível da maior cheia histórica (1983)"),
]


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


def definir_situacao(regua):
    if regua < 5.09:
        return "NÍVEL NORMAL - monitoramento de rotina"
    if regua < 6.89:
        return "ATENÇÃO - nível de cheia padrão atingido"
    if regua < 7.25:
        return "ALERTA - área de risco de enchente (zoneamento local, cheia de 10 anos)"
    if regua < 8.90:
        return "ALERTA - nível da cheia de 1993 atingido"
    if regua < 10.42:
        return "ALERTA CRÍTICO - nível da grande cheia de 1992 atingido"
    return "ALERTA CRÍTICO - nível comparável à maior cheia histórica (1983)"


def calcular_tendencia(historico):
    if len(historico) < 2:
        return {"texto": "Sem dados suficientes para tendência.", "delta": 0, "direcao": "estavel"}
    delta = historico[-1]["regua_m"] - historico[-2]["regua_m"]
    if delta > 0:
        return {"texto": f"SUBINDO +{delta:.3f} m/h", "delta": delta, "direcao": "subindo"}
    if delta < 0:
        return {"texto": f"BAIXANDO {delta:.3f} m/h", "delta": delta, "direcao": "baixando"}
    return {"texto": "ESTÁVEL", "delta": 0, "direcao": "estavel"}


def verificar_alerta_previsao(historico, previsao):
    if not historico or not previsao:
        return "Sem previsão disponível para alertas futuros."
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
        return "Sem previsão futura dentro das próximas 48 h."
    maior = max(valores)
    for cota, descricao in sorted(COTAS_ALERTA_DEFESA_CIVIL, reverse=True):
        if maior >= cota:
            return f"Previsão em 48 h: pode atingir {maior:.2f} m ({descricao})."
    return "Previsão em 48 h sem atingir cotas críticas."


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
        "situacao": definir_situacao(regua),
        "tendencia": calcular_tendencia(historico),
        "alerta_previsao": verificar_alerta_previsao(historico, previsao),
        "previsao_disponivel": bool(previsao),
        "cotas_bairros": [{"nivel": nivel, "descricao": desc} for nivel, desc in COTAS_BAIRROS],
        "cotas_alerta": [{"nivel": nivel, "descricao": desc} for nivel, desc in COTAS_ALERTA_DEFESA_CIVIL],
        "janela_historico_horas": JANELA_HISTORICO_HORAS,
        "janela_previsao_horas": JANELA_PREVISAO_HORAS,
    }


FONTE_ANA = "ANA – Agência Nacional de Águas e Saneamento Básico (estação telemétrica UHE Gov. Bento Munhoz, União da Vitória)"
FONTE_COPEL = "Copel – Monitoramento Hidrológico (fonte redundante, usada quando a ANA ainda não publicou a leitura da hora)"


def coletar_uma_vez(ultima_anterior=None):
    historico = coletar_via_ana()
    fonte_historico = None
    url_historico = URL_HISTORICO_COPEL
    if historico:
        nova_ultima_ana = historico[-1]["data_hora"]
        if ultima_anterior is None or nova_ultima_ana != ultima_anterior:
            fonte_historico = FONTE_ANA
            url_historico = URL_HISTORICO_ANA
        else:
            log(f"ANA: ainda sem dado novo (última segue {nova_ultima_ana}); usando Copel como redundância nesta rodada.")
            historico = None

    if not historico:
        texto_historico = coletar_texto(URL_HISTORICO_COPEL)
        historico = extrair_medicoes(texto_historico)
        fonte_historico = FONTE_COPEL
        url_historico = URL_HISTORICO_COPEL
    log(f"Medições obtidas via {fonte_historico.split(' ')[0]}: {len(historico)}")

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
    if anterior and anterior.get("dados"):
        ultima_anterior = anterior["dados"].get("ultima", {}).get("data_hora")

    payload = None
    erro = None
    tentativas = 2
    for tentativa in range(1, tentativas + 1):
        try:
            payload = coletar_uma_vez(ultima_anterior)
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
