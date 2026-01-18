from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base

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
    idioma_base = Column(String(20))     # punt 3: idioma navegador
    pais_natiu = Column(String(50))  # nom del país basat en codi_pais_natiu
    codi_pais_natiu = Column(String(5), nullable=True)  # ex: "MX"
    durada = Column(Integer)        # punt 4: durada visita en segons (nullable = pot ser zero o None)
    resolucio = Column(String(20))  # punt 6: resolució pantalla (ex: "1920x1080")
    geolocalitzacio = Column(String(100))  # punt 8: info geolocalització aprox (ex: "Barcelona, Espanya")

    # geolocalitzacio detallada
    lat = Column(String(20))
    lon = Column(String(20))
    ciutat = Column(String(100))
    regio = Column(String(100))
    pais_fisic = Column(String(100))
    codi_pais_fisic = Column(String(5))
    zip = Column(String(15))
    isp = Column(String(150))
    org = Column(String(150))
    as_name = Column(String(150))

    # Informació del dispositiu
    tipus_dispositiu = Column(String(20))
    navegador = Column(String(30))
    sistema_operatiu = Column(String(30))
    model_dispositiu = Column(String(50))

    hora_local = Column(String(40))
    zona_horaria = Column(String(40))
    scroll_max = Column(Integer)


