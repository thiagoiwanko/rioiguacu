import json
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


APP_VERSION = "GitHub Actions 1.0"
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data.json"
LOG_PATH = BASE_DIR / "monitor_web.log"

URL_HISTORICO = "https://www.copel.com/mhbweb/paginas/bacia-iguacu.jsf"
URL_PREVISAO = "https://www.copel.com/mhbweb/paginas/previsao.jsf"

JANELA_HISTORICO_HORAS = 48
JANELA_PREVISAO_HORAS = 48
TIMEOUT_COLETA_SEGUNDOS = 90
FUSO_BR = ZoneInfo("America/Sao_Paulo")


def agora_br():
    return datetime.now(FUSO_BR).replace(tzinfo=None)


ESPERA_NOVA_TENTATIVA_SEGUNDOS = 30

COTAS_BAIRROS = [
    (1.29, "Menor nível histórico - estiagem de 2020"),
    (6.00, "Limeira / Rio d'Areia / Rocio"),
    (6.50, "São Basílio / Navegantes / Ponte Nova"),
    (7.00, "Cidade Jardim / Cristo Rei / Sagrada Família"),
    (8.12, "Referência da enchente de 2014"),
    (8.38, "Referência da enchente de 2023"),
    (9.80, "Grande enchente de 1992"),
    (10.42, "Cheia histórica de 1983"),
]

COTAS_ALERTA_DEFESA_CIVIL = [
    (4.30, "ATENÇÃO MODERADA"),
    (4.50, "ATENÇÃO ALTA"),
    (4.90, "ATENÇÃO MUITO ALTA"),
    (5.50, "ALERTA CRÍTICO - PLANO DE CONTINGÊNCIA ACIONADO"),
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
    if regua < 4.30:
        return "NÍVEL NORMAL - monitoramento diário"
    if regua < 4.50:
        return "ATENÇÃO MODERADA"
    if regua < 4.90:
        return "ATENÇÃO ALTA"
    if regua < 5.50:
        return "ATENÇÃO MUITO ALTA"
    texto = "ALERTA CRÍTICO - Plano de Contingência acionado; início do impacto nas primeiras residências"
    if regua < 6.0:
        return texto
    if regua < 6.5:
        return f"{texto}; afetando Limeira / Rio d'Areia / Rocio"
    if regua < 7.0:
        return f"{texto}; afetando Limeira / Rio d'Areia / Rocio / São Basílio / Navegantes / Ponte Nova"
    if regua < 8.12:
        return f"{texto}; afetando Limeira / Rio d'Areia / Rocio / São Basílio / Navegantes / Ponte Nova / Cidade Jardim / Cristo Rei / Sagrada Família"
    if regua < 8.38:
        return f"{texto}; próximo da enchente de 2014"
    if regua < 9.80:
        return f"{texto}; próximo da enchente de 2023"
    if regua < 10.42:
        return f"{texto}; próximo da enchente de 1992"
    return f"{texto}; CHEIA HISTÓRICA - nível comparável a 1983"


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


def montar_payload(historico, previsao):
    if not historico:
        raise RuntimeError("nenhuma medição foi encontrada na tela da Copel")

    ultima = historico[-1]
    regua = float(ultima["regua_m"])
    return {
        "versao": APP_VERSION,
        "fonte": "Copel - Monitoramento Hidrológico",
        "url_historico": URL_HISTORICO,
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


def coletar_uma_vez():
    texto_historico = coletar_texto(URL_HISTORICO)
    historico = extrair_medicoes(texto_historico)
    log(f"Medições extraídas: {len(historico)}")

    previsao = []
    try:
        texto_previsao = coletar_texto(URL_PREVISAO)
        previsao = extrair_previsao(texto_previsao)
        log(f"Previsões extraídas: {len(previsao)}")
    except Exception as exc:
        log(f"Previsão indisponível: {exc}")

    return montar_payload(historico, previsao)


def carregar_anterior():
    if DATA_PATH.exists():
        try:
            return json.loads(DATA_PATH.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


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
            payload = coletar_uma_vez()
        except Exception as exc:
            erro = str(exc)
            log(f"Erro na coleta (tentativa {tentativa}): {exc}")
            payload = None
            break

        nova_ultima = payload["ultima"]["data_hora"]
        if ultima_anterior is None or nova_ultima != ultima_anterior or tentativa == tentativas:
            break
        log(
            f"Copel ainda não publicou dado novo (última: {nova_ultima}). "
            f"Aguardando {ESPERA_NOVA_TENTATIVA_SEGUNDOS}s para nova tentativa."
        )
        time.sleep(ESPERA_NOVA_TENTATIVA_SEGUNDOS)

    if payload:
        resultado = {"ok": True, "erro": None, "dados": payload}
        log("Dados atualizados com sucesso.")
    else:
        dados_cache = anterior["dados"] if anterior else None
        resultado = {"ok": False, "erro": erro or "falha desconhecida na coleta", "dados": dados_cache}
        log(f"Falha na coleta, mantendo dado anterior em cache. Erro: {erro}")

    DATA_PATH.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"data.json gravado ({DATA_PATH.stat().st_size} bytes).")


if __name__ == "__main__":
    main()
