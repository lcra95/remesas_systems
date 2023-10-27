from connections.db_connection import SessionLocal, Base


class Indicator:
    @staticmethod
    def all_indicators():
        session = SessionLocal()
        indicadores = session.query(Base.classes.indicador).all()
        session.close()
        indicadores_list = [{"nombre": indicador.nombre, "id": indicador.id, "url": indicador.url_api} for indicador in
                            indicadores]

        return indicadores_list
