from flask import request
from flask_restful import Resource
from binance.client import Client
from modelos.Simbolo import register_symbolo, get_active_symbols
from helpers.binance import BinanceHelper
class SimboloResource(Resource):

    @staticmethod
    def post():
        data =  request.get_json()
        info = register_symbolo(data)
        return info

class getSymbols(Resource):
    @staticmethod
    def get():
        interval = Client.KLINE_INTERVAL_1MINUTE
        lookback = 500
        symbols = get_active_symbols()
        result = []
        
        for symbol in symbols:
            
            close_prices = BinanceHelper.get_close_prices(symbol["simbolo"], interval, lookback)
            rsi = BinanceHelper.calculate_rsi(close_prices)
            current_price = BinanceHelper.get_current_price(symbol["simbolo"])
            temp = {
                "symbol" : symbol,
                "rsi" : rsi[-1],
                "price" : current_price
            }
            result.append(temp)

        return result