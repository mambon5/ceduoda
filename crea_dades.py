from sqlalchemy import create_engine
from config import SQLALCHEMY_DATABASE_URL
from models import Base

# Connexió
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False) # el echo es el debug o xivato



# Crear la taula si no existeix
if __name__ == "__main__":
    Base.metadata.create_all(engine)

