from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import SQLALCHEMY_DATABASE_URL
from models import Base

# Connexió
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False) # el echo es el debug o xivato

# (ha d'existir una variable `engine` definida més amunt en aquest fitxer)

Session = sessionmaker(bind=engine)

def create_initial_users():
    # importa models aquí per evitar imports circulars a l'inici
    from models import Base, User
    # crea les taules (si no existeixen)
    Base.metadata.create_all(bind=engine)

    sess = Session()
    try:
        if not sess.query(User).filter_by(username="sergi").first():
            u = User(username="sergi")
            u.set_password("sergiroma")
            sess.add(u)
        if not sess.query(User).filter_by(username="roma").first():
            u2 = User(username="roma")
            u2.set_password("sergiroma")
            sess.add(u2)
        sess.commit()
    finally:
        sess.close()

# Crear la taula si no existeix
if __name__ == "__main__":
    create_initial_users()
    print("Taules creades i usuaris inicials inserits (si no existien).")

