import requests
from connections.db_connection import get_db_session, Base
from sqlalchemy.exc import SQLAlchemyError
from helpers.error_handler import handle_exception

class utilities:
    @staticmethod
    def fetch_and_insert_symbols():
        try:
            response = requests.get('https://api.binance.com/api/v3/exchangeInfo')
            data = response.json()

            with get_db_session() as session:
                for symbol_info in data['symbols']:
                    if 'USDT' in symbol_info['symbol']:
                        try:
                            new_symbol = Base.classes.nuevos(nombre=symbol_info['symbol'])
                            session.add(new_symbol)
                        except SQLAlchemyError as e:
                            print(f"Error al insertar símbolo: {e}")
                session.commit()
            return "HE"
        except Exception as e:
            handle_exception(e)
    @staticmethod
    def check_new_symbols():
        response = requests.get('https://api.binance.com/api/v3/exchangeInfo')
        binance_symbols = {symbol_info['symbol'] for symbol_info in response.json()['symbols'] if 'USDT' in symbol_info['symbol']}

        with get_db_session() as session:
            existing_symbols = {symbol.nombre for symbol in session.query(Base.classes.nuevos).all()}
        
        new_symbols = binance_symbols - existing_symbols

        return list(new_symbols)
