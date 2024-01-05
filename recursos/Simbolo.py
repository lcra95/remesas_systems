from flask import request
from flask_restful import Resource
from binance.client import Client
from modelos.Simbolo import register_symbolo, get_active_symbols, update_symbolo
from helpers.binance import BinanceHelper
from helpers.error_handler import handle_exception
from modelos.Transaccion import register_transaction, find_transactions_by_symbol_id
from modelos.Rsi_calculos import register_rsi_calculation
from helpers.telegram import TelegramHelper
import requests
import pandas as pd
from datetime import datetime, timedelta
from flask import send_from_directory
import os


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
                        if info_compra is not None:
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
                    try:
                        info_compra = find_transactions_by_symbol_id(symbol["id"])
                        if not info_compra:
                            print(f"No se encontraron datos de compra para el símbolo: {symbol['simbolo']}")
                            continue  # Salta a la siguiente iteración del bucle
                        
                        porcentaje = BinanceHelper.calculate_percentage_change(current_price, float(info_compra[0]["price"]))
                    except Exception as e:
                        handle_exception(e)
                        print(e)
                    if virtual != 1:
                        if porcentaje > symbol["sell_percentage"]:
                            info_venta = BinanceHelper.sell_crypto(symbol["simbolo"])
                            if info_venta is not None:
                                vendido = True
                        elif porcentaje <= -symbol["stop_loss_percentage"]:
                            info_venta = BinanceHelper.sell_crypto(symbol["simbolo"])
                            if info_venta is not None:
                                TelegramHelper.send_telegram_message("HAZ PERDIDO")
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
                        if porcentaje > symbol["sell_percentage"]:
                            getSymbols.venta_virtual(current_price, symbol["id"], info_compra[0]["cantidad"])
                        elif porcentaje <= -symbol["stop_loss_percentage"]:
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

class newSymbolsResource(Resource):
    @staticmethod
    def get():
        symbol = request.args.get('simbolo')

        response = requests.get('https://api.binance.com/api/v3/exchangeInfo')
        data = response.json()
        
        interval = "1m"
        limit =  request.args.get('limit')  # Cantidad de datos históricos que deseas obtener

        if int(limit) <= 1000:
            # Si el límite es de 1000 o menos, realiza una sola llamada
            url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
            response = requests.get(url)
            combined_data = response.json()
        else:
            # Si el límite es mayor que 1000 pero menor o igual a 1440
            # Primera llamada para obtener los últimos 1000 registros
            url_1 = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=1000"
            response_1 = requests.get(url_1)
            data_1 = response_1.json()

            # Calcular cuántos datos adicionales se necesitan
            additional_data_needed = int(limit) - 1000

            # Calcular el timestamp para la segunda llamada
            start_time = datetime.utcfromtimestamp(data_1[0][0] / 1000) - timedelta(minutes=additional_data_needed)

            # Segunda llamada para obtener los datos adicionales
            url_2 = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&startTime={int(start_time.timestamp() * 1000)}&limit={additional_data_needed}"
            response_2 = requests.get(url_2)
            data_2 = response_2.json()

            # Combinar los datos
            combined_data = data_2 + data_1
        headers = [
            "Timestamp",
            "Precio de Apertura",
            "Precio Máximo",
            "Precio Mínimo",
            "Precio de Cierre",
            "Volumen",
            "Timestamp Fin",
            "Volumen en Moneda Base",
            "Número de Operaciones",
            "Volumen Taker en Moneda Base",
            "Volumen Taker en Moneda Cotizada",
            "Ignore"
        ]

        # Crear un DataFrame de Pandas con los datos y los encabezados
        df = pd.DataFrame(combined_data, columns=headers)

        # Convertir los timestamps en formato de fecha legible
        df['Timestamp'] = df['Timestamp'].apply(lambda x: (datetime.utcfromtimestamp(x / 1000) - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'))
        df['Timestamp Fin'] = df['Timestamp Fin'].apply(lambda x: (datetime.utcfromtimestamp(x / 1000) - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'))


        precio_cierre_inicial = df["Precio de Cierre"].astype(float).iloc[0]

        # Calcular el porcentaje de incremento/decremento con respecto al primer precio de cierre
        df["Porcentaje de Incremento"] = ((df["Precio de Cierre"].astype(float) - precio_cierre_inicial) / precio_cierre_inicial) * 100

        # Guardar el DataFrame en un archivo Excel
        excel_file_path = f'datos_crypto_{symbol}_{datetime.now()}.xlsx'
        df.to_excel(excel_file_path, index=False)

        # Directorio donde se encuentra el archivo (puede ser diferente según tu configuración)
        directory = os.getcwd()

        # Devolver el archivo para su descarga
        return send_from_directory(directory, excel_file_path, as_attachment=True)


from datetime import datetime, timedelta
import requests
from flask_restful import Resource
from concurrent.futures import ThreadPoolExecutor

class MultipleSymbolsChangeResource(Resource):
    @staticmethod
    def process_symbol(symbol, interval, intervals):
        data_2h = MultipleSymbolsChangeResource.get_data(symbol, interval, intervals["2h"])
        precio_inicial_2h = float(data_2h[0][1])
        precio_final_2h = float(data_2h[-1][4])
        cambio_2h = ((precio_final_2h - precio_inicial_2h) / precio_inicial_2h) * 100

        if cambio_2h > 0:
            symbol_result = {"Simbolo": symbol, "2h": round(cambio_2h, 5)}
            for key, minutes in intervals.items():
                if key != "2h":
                    data = MultipleSymbolsChangeResource.get_data(symbol, interval, minutes)
                    precio_inicial = float(data[0][1])
                    precio_final = float(data[-1][4])
                    cambio_porcentual = ((precio_final - precio_inicial) / precio_inicial) * 100
                    symbol_result[key] = round(cambio_porcentual, 5)
            symbol_result["URL"] = f"https://www.binance.com/es-LA/trade/{symbol}?type=spot"
            return symbol_result
        return None

    @staticmethod
    def get():
        try:
            symbols = BinanceHelper.get_positive_balance_symbols()
            interval = "1m"
            intervals = {"24h": 1440, "6h": 360, "2h": 120, "10m": 10}
            
            # Usar ThreadPoolExecutor para realizar solicitudes de forma paralela
            with ThreadPoolExecutor(max_workers=50) as executor:
                futures = [executor.submit(MultipleSymbolsChangeResource.process_symbol, symbol, interval, intervals) for symbol in symbols]
                all_data = [future.result() for future in futures if future.result() is not None]

            # Crear DataFrame
            df = pd.DataFrame(all_data)
            df = df[["Simbolo", "24h", "6h", "2h", "10m", "URL"]]
            df = df.sort_values(by="2h", ascending=False)
            # Guardar el DataFrame en un archivo Excel
            excel_file_path = f'datos_crypto_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            df.to_excel(excel_file_path, index=False)

            # Directorio donde se encuentra el archivo
            directory = os.getcwd()

            # Devolver el archivo para su descarga
            return send_from_directory(directory, excel_file_path, as_attachment=True)
        except Exception as e:
            handle_exception(e)

    @staticmethod
    def get_data(symbol, interval, minutes):
        if minutes <= 1000:
            url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={minutes}"
            response = requests.get(url)
            return response.json()
        else:
            # Realizar dos llamadas para obtener más de 1000 datos
            first_call_limit = 1000
            second_call_limit = minutes - 1000

            # Primera llamada
            url_1 = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={first_call_limit}"
            response_1 = requests.get(url_1)
            data_1 = response_1.json()

            # Calcular el timestamp para la segunda llamada
            start_time = datetime.utcfromtimestamp(data_1[0][0] / 1000) - timedelta(minutes=second_call_limit)

            # Segunda llamada
            url_2 = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&startTime={int(start_time.timestamp() * 1000)}&limit={second_call_limit}"
            response_2 = requests.get(url_2)
            data_2 = response_2.json()

            return data_2 + data_1


