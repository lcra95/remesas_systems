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
