from flask import Flask, jsonify
import logging
import os
from flask_cors import CORS
from modelos.Indicador import Indicator

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)


@app.route('/')
def home():
    indicadores_list = Indicator.all_indicators()
    return jsonify(indicadores_list)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5353, debug=True)
