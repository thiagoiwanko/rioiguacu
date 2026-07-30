import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("Precisa do pacote requests (o mesmo do backfill): pip install requests")

AQUI = Path(os.path.dirname(os.path.abspath(__file__)))
PASTA = AQUI / "chuva_prevista"

PONTOS = [
    ("65035001", "PortoAmazonas",  -25.5481, -49.8894),
    ("65155001", "SaoBento_Varzea", -25.9439, -49.7961),
    ("65100001", "RioNegro",        -26.1097, -49.8011),
    ("65060001", "SaoMateus",       -25.8756, -50.3894),
    ("65175001", "Divisa",          -26.0914, -50.3339),
    ("65220001", "Fluviopolis",     -26.0192, -50.5925),
    ("65310001", "UV",              -26.2281, -51.0803),
    ("65365801", "PortoVitoria",    -26.1653, -51.2281),
    ("65774400", "BarramentoFozAreia", -26.0094, -51.6647),
]
MODELOS = "ecmwf_ifs025,gfs_seamless,icon_seamless"
DIAS = 8
ESPERAS = [30, 120, 300]

def montar_url(com_modelos=True):
    lats = ",".join(f"{p[2]}" for p in PONTOS)
    lons = ",".join(f"{p[3]}" for p in PONTOS)
    url = ("https://api.open-meteo.com/v1/forecast"
           f"?latitude={lats}&longitude={lons}"
           "&hourly=precipitation"
           f"&forecast_days={DIAS}"
           "&timezone=America%2FSao_Paulo")
    if com_modelos:
        url += f"&models={MODELOS}"
    return url

def baixar():
    for com_modelos in (True, False):
        url = montar_url(com_modelos)
        for i, espera in enumerate([0] + ESPERAS):
            if espera:
                time.sleep(espera)
            try:
                r = requests.get(url, timeout=60)
                if r.status_code == 200:
                    return r.json(), url, com_modelos
                print(f"HTTP {r.status_code}")
                if r.status_code == 400:
                    break
            except Exception as e:
                print(type(e).__name__)
    sys.exit("falha na coleta")

def somar_janela(tempos, valores, ini, fim):
    tot, n = 0.0, 0
    for t, v in zip(tempos, valores):
        if ini < t <= fim and v is not None:
            tot += v
            n += 1
    return round(tot, 1) if n else None

def processar(dados, agora):
    if isinstance(dados, dict):
        dados = [dados]
    if len(dados) != len(PONTOS):
        print(f"pontos: {len(dados)}/{len(PONTOS)}")
    ag = agora.strftime("%Y-%m-%dT%H:%M")
    janelas = [24, 48, 72]
    resumo = {}
    for i, resp in enumerate(dados):
        cod, nome = PONTOS[i][0], PONTOS[i][1]
        hh = resp.get("hourly", {})
        tempos = hh.get("time", [])
        campos = [c for c in hh if c.startswith("precipitation")]
        for campo in campos:
            modelo = campo.replace("precipitation_", "") if "_" in campo else "best_match"
            for j in janelas:
                fim = (agora.timestamp() + j * 3600)
                fim_txt = datetime.fromtimestamp(fim).strftime("%Y-%m-%dT%H:%M")
                s = somar_janela(tempos, hh[campo], ag, fim_txt)
                if s is not None:
                    resumo.setdefault(modelo, {}).setdefault(f"+{j}h", {})[nome] = s
    medias = {}
    for modelo, jans in resumo.items():
        medias[modelo] = {}
        for jan, pontos in jans.items():
            vals = list(pontos.values())
            medias[modelo][jan] = {
                "media_bacia_mm": round(sum(vals) / len(vals), 1),
                "max_ponto_mm": round(max(vals), 1),
                "por_ponto": pontos,
            }
    registro = {
        "coletado_em": agora.strftime("%Y-%m-%d %H:%M:%S"),
        "fonte": "open-meteo.com (gratuito, licença CC-BY 4.0)",
        "pontos": [{"codigo": c, "nome": n, "lat": la, "lon": lo}
                   for c, n, la, lo in PONTOS],
        "resumo_mm": medias,
        "resposta_crua": dados,
    }
    return registro, medias

def main():
    agora = datetime.now()
    print(agora.strftime("%Y-%m-%d %H:%M"))
    dados, url, com_modelos = baixar()
    registro, medias = processar(dados, agora)
    registro["url"] = url
    PASTA.mkdir(exist_ok=True)
    arq = PASTA / f"qpf_{agora.strftime('%Y-%m-%d_%H%M')}.json"
    with open(arq, "w", encoding="utf-8") as f:
        json.dump(registro, f, ensure_ascii=False, indent=1)
    print(arq.name)
    for modelo, jans in sorted(medias.items()):
        linha = f"  {modelo:15s}"
        for jan in ("+24h", "+48h", "+72h"):
            if jan in jans:
                m = jans[jan]
                linha += f"  {jan}: {m['media_bacia_mm']:5.1f} mm ({m['max_ponto_mm']:.1f})"
        print(linha)

if __name__ == "__main__":
    main()
