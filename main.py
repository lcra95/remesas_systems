from flask import Flask
from flask_restful import Api
import logging
import requests
import json
from bs4 import BeautifulSoup
from flask_cors import CORS
from modelos.Credencial import get_credential_by_name
from recursos.Simbolo import SimboloResource , newSymbolsResource
from recursos.Simbolo import getSymbols
from recursos.Rsi import RsiCalculationsResource
from modelos.NewSymbols import utilities
from helpers.binance import BinanceHelper

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)
api = Api(app)
api.add_resource(SimboloResource, "/simbolo")
api.add_resource(getSymbols, "/simbolos")
api.add_resource(newSymbolsResource, "/newsimbolos")
api.add_resource(RsiCalculationsResource, "/rsi_list")

@app.route('/')
def home():
    INFO = get_credential_by_name('TOKEN')    
    return INFO

@app.route('/find')
def find():
    result = "None"
    list = utilities.check_new_symbols()
    if len(list) > 0:
        for simbolo in list:
            result = BinanceHelper.buy_crypto(simbolo, 100)
            
    return result

@app.route('/insert_simbolo')
def insert():
    ins = utilities.fetch_and_insert_symbols()
    return  ins


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5353, debug=True)
