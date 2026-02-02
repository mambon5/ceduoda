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
        # User sergi
        u = sess.query(User).filter_by(username="sergi").first()
        if not u:
            u = User(username="sergi", role="user")
            u.set_password("sergiroma")
            sess.add(u)
        else:
            if u.role != "admin": u.role = "admin"

        # User roma
        u2 = sess.query(User).filter_by(username="roma").first()
        if not u2:
            u2 = User(username="roma", role="admin")
            u2.set_password("sergiroma")
            sess.add(u2)
        else:
            if u2.role != "admin": u2.role = "admin"

        sess.commit()
    finally:
        sess.close()

# Crear la taula si no existeix
if __name__ == "__main__":
    create_initial_users()
    print("Taules creades i usuaris inicials inserits (si no existien).")

