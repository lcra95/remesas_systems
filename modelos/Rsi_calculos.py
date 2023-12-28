from connections.db_connection import get_db_session, Base
from sqlalchemy.exc import SQLAlchemyError

def register_rsi_calculation(data):
    with get_db_session() as session:
        try:
            new_rsi_calculation = Base.classes.rsi_calculos(
                id_simbolo=data['id_simbolo'],
                simbolo_nombre=data['simbolo'],
                precio=data['precio'],
                rsi=data['rsi']
            )
            session.add(new_rsi_calculation)
            session.commit()
            return {"message": "Cálculo de RSI registrado con éxito"}, 201
        except SQLAlchemyError as e:
            session.rollback()
            return {"error": str(e)}, 500

def get_rsi_calculations_by_symbol_id(symbol_id):
    with get_db_session() as session:
        try:
            rsi_calculations = session.query(Base.classes.rsi_calculos).filter_by(id_simbolo=symbol_id).all()
            rsi_calculations_data = [
                {
                    "id": rsi_calculation.id,
                    "id_simbolo": rsi_calculation.id_simbolo,
                    "simbolo_nombre": rsi_calculation.simbolo_nombre,
                    "precio": float(rsi_calculation.precio),
                    "rsi": float(rsi_calculation.rsi),
                    "fecha": rsi_calculation.fecha.isoformat()
                }
                for rsi_calculation in rsi_calculations
            ]
            return rsi_calculations_data
        except SQLAlchemyError as e:
            return {"error": str(e)}, 500
