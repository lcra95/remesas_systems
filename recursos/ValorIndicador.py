from flask_restful import Resource
from connections.db_connection import Base, SessionLocal
Indicador = Base.classes.indicador


class ValorIndicador(Resource):
    @staticmethod
    def get():
        session = SessionLocal()
        try:
            current_indicador = session.query(Indicador).filter(Indicador.vigente == 1).first()
            if current_indicador:
                return {
                    "id": current_indicador.id,
                    "dolar_paralelo": current_indicador.dolar_paralelo,
                    "dolar_bcv": current_indicador.dolar_bcv,
                    "tasa_venezuela": current_indicador.tasa_venezuela,
                    "creado": str(current_indicador.creado),
                    "actualizado": str(current_indicador.actualizado)
                }
            else:
                return None
        finally:
            session.close()

    @staticmethod
    def insert_new_indicador(dolar_paralelo, dolar_bcv, tasa_venezuela):
        session = SessionLocal()

        try:
            session.query(Indicador).update({Indicador.vigente: 0})
            new_indicador = Indicador(
                dolar_paralelo=dolar_paralelo,
                dolar_bcv=dolar_bcv,
                tasa_venezuela=tasa_venezuela,
                vigente=1
            )
            session.add(new_indicador)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
