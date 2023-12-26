from connections.db_connection import SessionLocal, Base

def get_credential_by_name(name):
    session = SessionLocal()
    credential = session.query(Base.classes.credencial).filter_by(nombre=name).first()
    session.close()

    if credential:
        return credential.token
    else:
        return None
