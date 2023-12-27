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
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)
api = Api(app)
api.add_resource(SimboloResource, "/simbolo")
api.add_resource(getSymbols, "/simbolos")
api.add_resource(newSymbolsResource, "/newsimbolos")

@app.route('/')
def home():
    INFO = get_credential_by_name('TOKEN')    
    return INFO



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5353, debug=True)
