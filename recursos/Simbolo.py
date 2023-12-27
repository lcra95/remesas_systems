from flask import request
from flask_restful import Resource
from binance.client import Client
from modelos.Simbolo import register_symbolo, get_active_symbols, update_symbolo
from helpers.binance import BinanceHelper
from helpers.error_handler import handle_exception
from modelos.Transaccion import register_transaction, find_transactions_by_symbol_id
from modelos.Rsi_calculos import register_rsi_calculation
class SimboloResource(Resource):

    @staticmethod
    def post():
        data =  request.get_json()
        info = register_symbolo(data)
        return info

class getSymbols(Resource):
    @staticmethod
    def get():
        try:
            interval = Client.KLINE_INTERVAL_1MINUTE
            lookback = 500
            symbols = get_active_symbols()
            result = []
            
            for symbol in symbols:
                
                virtual = symbol["virtual"]
                close_prices = BinanceHelper.get_close_prices(symbol["simbolo"], interval, lookback)
                rsi = BinanceHelper.calculate_rsi(close_prices)
                current_price = BinanceHelper.get_current_price(symbol["simbolo"])
                
                getSymbols.rsi(symbol["id"], symbol["simbolo"], current_price, rsi[-1])
                
                
                vendido = False
                if rsi[-1] < symbol["rsi_limit"] and symbol["transaccion"] is None:
                    if virtual != 1:
                        info_compra = BinanceHelper.buy_crypto(symbol["simbolo"], symbol["amount_usdt"])                
                        data_compra = {
                            "tipo_transaccion" : 1,
                            "valor" : info_compra["cummulativeQuoteQty"],
                            "cantidad": info_compra["origQty"],
                            "id_simbolo" : symbol["id"],
                            "price" : info_compra["fills"][0]["price"]
                        }
                        register_transaction(data_compra)
                        update_symbolo(symbol["id"], {"transaccion" : 1})
                    else:
                        getSymbols.compra_virtual(current_price, symbol["amount_usdt"], symbol["id"])
                elif symbol["transaccion"] == 1:
                    info_compra = find_transactions_by_symbol_id(symbol["id"])
                    porcentaje = BinanceHelper.calculate_percentage_change(current_price, float(info_compra[0]["price"]))
                    
                    if virtual != 1:
                        if porcentaje > 1   :
                            info_venta = BinanceHelper.sell_crypto(symbol["simbolo"])
                            vendido = True
                        elif porcentaje <= -symbol["stop_loss_percentage"]:
                            info_venta = BinanceHelper.sell_crypto(symbol["simbolo"])
                            vendido = True
                        
                        if vendido:
                            data_venta = {
                                "tipo_transaccion" : 2,
                                "valor" : info_venta["cummulativeQuoteQty"],
                                "cantidad": info_venta["origQty"],
                                "id_simbolo" : symbol["id"],
                                "price" : info_venta["fills"][0]["price"]
                            }
                            register_transaction(data_venta)
                            update_symbolo(symbol["id"], {"transaccion" : 2, "status" : 2})
                    else:
                        getSymbols.venta_virtual(current_price, symbol["id"], info_compra[0]["cantidad"])
                temp = {
                    "symbol" : symbol,
                    "rsi" : rsi[-1],
                    "price" : current_price
                }
                result.append(temp)

            return result
        except Exception as e:
            handle_exception(e)
    
    @staticmethod
    def compra_virtual(current_price, amount_usdt, id_simbolo):
        data_compra = {
            "tipo_transaccion" : 1,
            "valor" : amount_usdt,
            "cantidad": float(amount_usdt/current_price),
            "id_simbolo" : id_simbolo,
            "price" : current_price
        }
        register_transaction(data_compra)
        update_symbolo(id_simbolo, {"transaccion" : 1})
        print("Compra virtual")

    @staticmethod
    def venta_virtual(current_price, id_simbolo, cantidad):
        print("---------------")
        print(type(cantidad), type(current_price))
        data_venta = {
            "tipo_transaccion" : 2,
            "valor" : float(float(cantidad) * current_price),
            "cantidad": cantidad,
            "id_simbolo" : id_simbolo,
            "price" : current_price
        }
        register_transaction(data_venta)
        update_symbolo(id_simbolo, {"transaccion" : None, "status" : 1})

    @staticmethod
    def rsi(id_simbolo, simbolo, current_price, rsi):
        info = {
            "rsi" : rsi,
            "precio" : current_price,
            "id_simbolo" : id_simbolo,
            "simbolo" : simbolo
        }
        register_rsi_calculation(info)