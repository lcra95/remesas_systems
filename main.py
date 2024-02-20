from flask import Flask
from flask_restful import Api
import logging
import requests
import json
from bs4 import BeautifulSoup
from flask_cors import CORS
from modelos.Credencial import get_credential_by_name
from recursos.Simbolo import SimboloResource , newSymbolsResource, MultipleSymbolsChangeResource
from recursos.Simbolo import getSymbols
from recursos.Rsi import RsiCalculationsResource
from modelos.NewSymbols import utilities
from helpers.binance import BinanceHelper
from helpers.telegram import TelegramHelper
import time


logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)
api = Api(app)
api.add_resource(SimboloResource, "/simbolo")
api.add_resource(getSymbols, "/simbolos")
api.add_resource(newSymbolsResource, "/historico")
api.add_resource(RsiCalculationsResource, "/rsi_list")
api.add_resource(MultipleSymbolsChangeResource, "/monitoreo")

@app.route('/')
def home():
    #INFO = get_credential_by_name('TOKEN')    
    INFO = BinanceHelper.get_binance_usdt_balance()
    return INFO

@app.route('/find')
def find():
    try:
        result = None
        simbolo = 'STRKUSDT'
        result = BinanceHelper.buy_crypto(simbolo, 360)
        TelegramHelper.send_telegram_message(str(result))
        return str(result)
    except Exception as e:
        TelegramHelper.send_telegram_message('Aun no hay STRK')
        return str(result)
@app.route('/insert_simbolo')
def insert():
    ins = utilities.fetch_and_insert_symbols()
    return  ins


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5353, debug=True)
