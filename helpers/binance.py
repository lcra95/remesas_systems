import os
import time
import numpy as np
from binance.client import Client
import talib
import logging
from modelos.Credencial import get_credential_by_name
from helpers.telegram import TelegramHelper
api_key = get_credential_by_name('BINANCE_API_KEY')
api_secret = get_credential_by_name('BINANCE_SECRET')
client = Client(api_key, api_secret)

class BinanceHelper:
    def get_current_price(symbol):
        ticker = client.get_symbol_ticker(symbol=symbol)
        return float(ticker['price'])

    def calculate_percentage_change(current_price, purchase_price):
        if purchase_price:
            return (current_price - purchase_price) / purchase_price * 100
        else:
            return 0


    def get_close_prices(symbol, interval, lookback):
        candles = client.get_klines(symbol=symbol, interval=interval, limit=lookback)
        close_prices = [float(candle[4]) for candle in candles]
        return np.array(close_prices)


    def calculate_rsi(prices, period=14):
        rsi = talib.RSI(prices, timeperiod=period)
        return rsi


    def get_lot_size(client, symbol):
        info = client.get_symbol_info(symbol)
        for filter in info['filters']:
            if filter['filterType'] == 'LOT_SIZE':
                return {
                    'minQty': float(filter['minQty']),
                    'maxQty': float(filter['maxQty']),
                    'stepSize': float(filter['stepSize'])
                }
        return None


    def adjust_quantity(quantity, step_size):
        return round(quantity - (quantity % step_size), len(str(step_size).split('.')[1]))


    def buy_crypto(client, symbol, amount_usd):
        current_price = BinanceHelper.get_current_price(symbol)
        lot_size = BinanceHelper.get_lot_size(client, symbol)

        if lot_size:
            quantity = amount_usd / current_price
            quantity = BinanceHelper.adjust_quantity(quantity, lot_size['stepSize'])

            if quantity < lot_size['minQty'] or quantity > lot_size['maxQty']:
                logging.error("Cantidad fuera del rango permitido por LOT_SIZE")
                print("Cantidad fuera del rango permitido por LOT_SIZE")
                return None

            try:
                order = client.order_market_buy(symbol=symbol, quantity=quantity)
                logging.info(f"Orden de compra ejecutada: {order}")
                print(f"Orden de compra ejecutada: {order}")
                TelegramHelper.send_telegram_message(f"Compra de {symbol} a {current_price} la cantidad de {quantity} ")
                return order
            except Exception as e:
                logging.error(f"Error al realizar la compra: {e}")
                print(f"Error al realizar la compra: {e}")
                return None
        else:
            logging.error("No se pudo obtener la información de LOT_SIZE")
            print("No se pudo obtener la información de LOT_SIZE")
            return None


    def sell_crypto(client, symbol):
        try:
            balance = client.get_asset_balance(asset=symbol.replace("USDT", ""))
            quantity = float(balance['free'])
            lot_size = BinanceHelper.get_lot_size(client, symbol)

            if lot_size:
                quantity = BinanceHelper.adjust_quantity(quantity, lot_size['stepSize'])

                if quantity < lot_size['minQty'] or quantity > lot_size['maxQty']:
                    logging.error("Cantidad de venta fuera del rango permitido por LOT_SIZE")
                    print("Cantidad de venta fuera del rango permitido por LOT_SIZE")
                    return None

                order = client.order_market_sell(symbol=symbol, quantity=quantity)
                logging.info(f"Orden de venta ejecutada: {order}")
                print(f"Orden de venta ejecutada: {order}")
                TelegramHelper.send_telegram_message(f"Venta {symbol} la cantidad de {quantity}")
                return order
            else:
                logging.error("No se pudo obtener la información de LOT_SIZE para la venta")
                print("No se pudo obtener la información de LOT_SIZE para la venta")
                return None
        except Exception as e:
            logging.error(f"Error al realizar la venta: {e}")
            print(f"Error al realizar la venta: {e}")
            return None
