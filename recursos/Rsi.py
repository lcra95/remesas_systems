from flask import request
from flask_restful import Resource
from helpers.error_handler import handle_exception
from modelos.Rsi_calculos import get_rsi_calculations_by_symbol_id
import pandas as pd

class RsiCalculationsResource(Resource):
    def get(self):
        symbol_id = request.args.get('id_simbolo')
        if symbol_id:
            # Obtener datos usando la función existente
            rsi_data = get_rsi_calculations_by_symbol_id(symbol_id)

            # Convertir a DataFrame
            df = pd.DataFrame(rsi_data)

            # Asegúrate de que los precios están en formato numérico y ordena por fecha
            df['precio'] = pd.to_numeric(df['precio'])
            df.sort_values(by='fecha', inplace=True)

            # Calcular el porcentaje de diferencia
            first_price = df['precio'].iloc[0]
            df['porcentaje_diferencia'] = ((df['precio'] - first_price) / first_price) * 100

            # Exportar a Excel
            file_name = f"rsi_calculations_{symbol_id}.xlsx"
            df.to_excel(file_name, index=False)

            return file_name
    