from connections.db_connection import get_db_session, Base
from sqlalchemy.exc import SQLAlchemyError

def register_transaction(data):
    with get_db_session() as session:
        try:
            new_transaction = Base.classes.transacciones(
                tipo_transaccion=data['tipo_transaccion'],
                valor=data['valor'],
                cantidad=data['cantidad'],
                id_simbolo=data['id_simbolo'],
                price = data["price"]
            )
            session.add(new_transaction)
            session.commit()
            return {"message": "Transacción registrada con éxito"}, 201
        except SQLAlchemyError as e:
            session.rollback()
            return {"error": str(e)}, 500

def find_transactions_by_symbol_id(symbol_id):
    with get_db_session() as session:
        try:
            transactions = session.query(Base.classes.transacciones).filter_by(id_simbolo=symbol_id).all()
            transactions_data = [
                {
                    "id": transaction.id,
                    "tipo_transaccion": transaction.tipo_transaccion,
                    "valor": str(transaction.valor),
                    "cantidad": str(transaction.cantidad),
                    "id_simbolo": transaction.id_simbolo,
                    "fecha": str(transaction.fecha),
                    "price" : str(transaction.price)
                }
                for transaction in transactions
            ]
            return transactions_data
        except SQLAlchemyError as e:
            return {"error": str(e)}, 500
