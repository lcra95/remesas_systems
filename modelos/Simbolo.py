from connections.db_connection import get_db_session, Base
from sqlalchemy.exc import SQLAlchemyError

def register_symbolo(data):
    with get_db_session() as session:
        try:
            new_symbolo = Base.classes.simbolo(
                simbolo=data['simbolo'],
                rsi_limit=data['rsi_limit'],
                stop_loss_percentage=data['stop_loss_percentage'],
                sell_percentage=data['sell_percentage'],
                status=1,
            )
            session.add(new_symbolo)
            session.commit()
            return {"message": "Símbolo registrado con éxito"}, 201
        except SQLAlchemyError as e:
            session.rollback()
            return {"error": str(e)}, 500

def get_active_symbols():
    with get_db_session() as session:
        try:
            active_symbols = session.query(Base.classes.simbolo).filter_by(status=1).all()
            resp = []
            for simbolo in active_symbols:
                
                temp = {
                    "id": simbolo.id,
                    "simbolo": simbolo.simbolo,
                    "rsi_limit": simbolo.rsi_limit,
                    "stop_loss_percentage": simbolo.stop_loss_percentage,
                    "sell_percentage": simbolo.sell_percentage,
                    "status": simbolo.status,
                    "fecha_inicio": str(simbolo.fecha_inicio),
                }
                resp.append(temp)
            return resp
        except SQLAlchemyError as e:
            return {"error": str(e)}, 500
