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
                amount_usdt = data["amount_usdt"]
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
                    "transaccion" : simbolo.transaccion,
                    "amount_usdt" : simbolo.amount_usdt,
                    "virtual": simbolo.virtual
                }
                resp.append(temp)
            return resp
        except SQLAlchemyError as e:
            return {"error": str(e)}, 500
        

def update_symbolo(symbol_id, data):
    with get_db_session() as session:
        try:
            symbolo = session.query(Base.classes.simbolo).get(symbol_id)
            if symbolo:
                # Actualizar solo si el campo está en el JSON recibido
                if 'rsi_limit' in data:
                    symbolo.rsi_limit = data['rsi_limit']
                if 'stop_loss_percentage' in data:
                    symbolo.stop_loss_percentage = data['stop_loss_percentage']
                if 'sell_percentage' in data:
                    symbolo.sell_percentage = data['sell_percentage']
                if 'status' in data:
                    symbolo.status = data['status']
                if 'fecha_fin' in data:
                    symbolo.fecha_fin = data['fecha_fin']
                if 'transaccion' in data:
                    symbolo.transaccion = data['transaccion']
                if 'amount_usdt' in data:
                    symbolo.amount_usdt = data['amount_usdt']
                
                session.commit()
                return {"message": "Símbolo actualizado con éxito"}, 200
            else:
                return {"error": "Símbolo no encontrado"}, 404
        except SQLAlchemyError as e:
            session.rollback()
            return {"error": str(e)}, 500

