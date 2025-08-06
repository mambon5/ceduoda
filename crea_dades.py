from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import SQLALCHEMY_DATABASE_URL

# Connexió
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False) # el echo es el debug o xivato
Base = declarative_base()

# Definició de la taula
class Visita(Base):
    __tablename__ = "visites"

    id = Column(Integer, primary_key=True, autoincrement=True)
    data_hora = Column(DateTime)
    ip = Column(String(45))
    pagina = Column(String(100))
    
    user_agent = Column(Text)       # punt 1: navegador i dispositiu
    referer = Column(Text)          # punt 2: d’on venen
    idioma = Column(String(20))     # punt 3: idioma navegador
    durada = Column(Integer)        # punt 4: durada visita en segons (nullable = pot ser zero o None)
    resolucio = Column(String(20))  # punt 6: resolució pantalla (ex: "1920x1080")
    geolocalitzacio = Column(String(100))  # punt 8: info geolocalització aprox (ex: "Barcelona, Espanya")


# Crear la taula si no existeix
if __name__ == "__main__":
    Base.metadata.create_all(engine)

