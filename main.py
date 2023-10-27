from flask import Flask
from flask_restful import Api
import logging
import requests
import json
from bs4 import BeautifulSoup
from flask_cors import CORS
from recursos.ValorIndicador import ValorIndicador
from helpers.binance import Binance

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)
api = Api(app)
api.add_resource(ValorIndicador, "/get_indicadores")


@app.route('/')
def home():
    return ":)"


@app.route('/indicadores')
def valordolar():

    url = "https://exchangemonitor.net/rates/data-new"
    urlbcv = 'https://www.bcv.org.ve/'

    querystring = {"reconv": "1", "type": "ve", "badge": "enparalelovzla"}

    payload = ""
    response = requests.request("GET", url, data=payload, params=querystring)

    inf = json.loads(response.text)
    longitud = len(inf["data"]) - 1
    tasa = inf["data"][longitud]
    paralelo = tasa[1]
    response = requests.get(urlbcv)
    soup = BeautifulSoup(response.content, 'html.parser')
    dolar_div = soup.find('div', {'id': 'dolar'})
    valor_dolar = dolar_div.text.strip()
    valor_limpio = valor_dolar.replace("USD", "").strip()
    valor_limpio = valor_limpio.replace(",", ".")
    valor_convertido = round(float(valor_limpio), 2)

    # TASA

    bs = Binance.consulta_bs()
    clp = Binance.consulta_clp()
    tasa = None
    for n, y in zip(bs["data"], clp["data"]):
        ves = round(float(n["adv"]["price"]), 3)
        clps = round(float(y["adv"]["price"]), 2)
        t0 = round(ves / clps, 4)
        t5 = round(t0 * 0.95, 4)
        tasa = t5

    ValorIndicador.insert_new_indicador(paralelo, valor_convertido, tasa)
    return {"paralelo": paralelo, "BCV": valor_convertido, "tasa": tasa}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5353, debug=True)
