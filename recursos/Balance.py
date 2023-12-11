from flask import request
from flask_restful import Resource
from binance.client import Client
from binance.exceptions import BinanceAPIException
from telegram import Bot
import asyncio
from connections.db_connection import Base, SessionLocal
from datetime import datetime
Transaccion = Base.classes.transaccion


api_key = 'iVT1aRRukap9b12jlFqrjU8ix0QOREoffD41Ey1VvLEPRWDDXt0fL2PyYVxQaQrm'
api_secret = '4byprzjIvjJfIbo0bbkg2o27buy1oFzMw0l6DydHe7y1ZdbAxF9XtszR5e5T0IKn'
class BinanceBalance(Resource):

    @staticmethod
    def get():
        try:
            api_key = 'iVT1aRRukap9b12jlFqrjU8ix0QOREoffD41Ey1VvLEPRWDDXt0fL2PyYVxQaQrm'
            api_secret = '4byprzjIvjJfIbo0bbkg2o27buy1oFzMw0l6DydHe7y1ZdbAxF9XtszR5e5T0IKn'
            token = '6609889311:AAFIVvD_0pJuz7myNLsy0QJzYo5TNDp1kKk'
            chat_id = '5090328284'
            client = Client(api_key, api_secret)
            bot = Bot(token)

            # Consultar el balance de VTHO y obtener el precio actual
            balance_VTHO = client.get_asset_balance(asset='VTHO')
            cantidad_VTHO = float(balance_VTHO['free']) + float(balance_VTHO['locked'])
            precio_actual = float(client.get_symbol_ticker(symbol="VTHOUSDT")['price'])
            valor_total_usdt = cantidad_VTHO * precio_actual

            # Determinar acción y enviar mensaje si es necesario
            mensaje = ""
            if valor_total_usdt > 51:
                mensaje = "Es momento de vender para ganar. Valor total: {:.2f} USDT".format(valor_total_usdt)
                asyncio.run(bot.send_message(chat_id=chat_id, text=mensaje))
            elif valor_total_usdt < 47:
                mensaje = "Estás perdiendo, debes vender. Valor total: {:.2f} USDT".format(valor_total_usdt)
                asyncio.run(bot.send_message(chat_id=chat_id, text=mensaje))

            print(f"Valor Actual {valor_total_usdt}")
            return {"valor_total_usdt": valor_total_usdt, "mensaje": mensaje}

        except BinanceAPIException as e:
            print(e)
            return {"error": str(e)}

class SpotBalance(Resource):
    @staticmethod
    def get():
        return SpotBalance.obtener_balance_spot(api_key, api_secret)    
    
    def obtener_balance_spot(api_key, api_secret):
        client = Client(api_key, api_secret)
        balance = client.get_account()
        precios = client.get_all_tickers()

        resultado = []
        for asset in balance['balances']:
            cantidad = float(asset['free'])
            if cantidad > 0:
                simbolo = asset['asset'] + 'USDT'
                precio_usdt = next((item['price'] for item in precios if item['symbol'] == simbolo), None)
                if precio_usdt:
                    valor_total = cantidad * float(precio_usdt)
                    resultado.append({
                        'simbolo': simbolo,
                        'cantidad': cantidad,
                        'precio_usdt': float(precio_usdt),
                        'valor_total': valor_total
                    })

        return resultado
    
class VentaSimbolo(Resource):
    def post(self, simbolo):
        client = Client(api_key, api_secret)
        
        try:
            # Obtener balance del símbolo
            balance = client.get_asset_balance(asset=simbolo)
            cantidad = float(balance['locked'])

            # Obtener precio actual
            precio_actual = float(client.get_symbol_ticker(symbol=f"{simbolo}USDT")['price'])
            valor_total = cantidad * precio_actual

            # Crear una orden de venta
            if cantidad > 0:
                orden = client.order_market_sell(symbol=f"{simbolo}USDT", quantity=cantidad)
                return {
                    "mensaje": "Orden de venta creada",
                    "cantidad": cantidad,
                    "precio_actual": precio_actual,
                    "valor_total": valor_total,
                    "orden": orden
                }
            else:
                return {"mensaje": "No hay suficientes activos para vender"}

        except BinanceAPIException as e:
            return {"error": str(e)}
        



class CompraSimbolo(Resource):
    def post(self):
        datos = request.json
        simbolo = datos['simbolo']
        cantidad_usdt = datos['cantidad_usdt']

        session = SessionLocal()
        client = Client(api_key, api_secret)
        
        try:
            # Obtener precio actual del símbolo en USDT
            precio_actual = float(client.get_symbol_ticker(symbol=f"{simbolo}USDT")['price'])

            # Calcular la cantidad del símbolo a comprar
            cantidad_simbolo = cantidad_usdt / precio_actual
            cantidad_simbolo=  round(cantidad_simbolo,4 )
            # Crear una orden de compra
            orden = client.order_market_buy(symbol=f"{simbolo}USDT", quantity=cantidad_simbolo)

            # Registrar la transacción en la base de datos
            session = SessionLocal()
            nueva_transaccion = Transaccion(
                symbol=simbolo,
                monto_usdt=str(cantidad_usdt),
                cantidad=str(cantidad_simbolo),
                estado=1,  # Estado de la transacción, asumiendo 1 para completado
                tipo_transaccion=1,  # 1 para compra
                fecha=datetime.now()
            )
            session.add(nueva_transaccion)
            session.commit()
            session.close()

            return {"mensaje": "Orden de compra creada y registrada en la base de datos", "orden": orden}

        except BinanceAPIException as e:
            session.close()
            return {"error": str(e)}
