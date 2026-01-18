from sqlalchemy.orm import Session
from models import Visita
from sqlalchemy import create_engine
from config import SQLALCHEMY_DATABASE_URL
import pycountry
from geo import obtenir_geo

# Connexió
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)
session = Session(bind=engine)

# Recuperem tots els registres que encara no tenen codi_pais_natiu o idioma_base
visites = session.query(Visita).filter(
    (Visita.codi_pais_natiu == None) | (Visita.idioma_base == None)
).all()

for v in visites:
    if v.idioma:
        parts = v.idioma.split('-')
        if len(parts) == 2:
            v.idioma_base = parts[0]                # ex: "es" de "es-MX"
            v.codi_pais_natiu = parts[1].upper()    # ex: "MX"
        else:
            v.idioma_base = parts[0]                # idioma sencer si no hi ha guió
            v.codi_pais_natiu = 'DESCO'
    else:
        v.idioma_base = 'desconegut'
        v.codi_pais_natiu = 'DESCO'

    
    try:
        v.pais_natiu = pycountry.countries.get(alpha_2=v.codi_pais_natiu).name
    except:
        v.pais_natiu = "Desconegut"

print(f"S'han processat {len(visites)} registres antics i s'han actualitzat idioma_base i codi_pais_natiu.")

# Recuperem tots els registres que encara no tenen pais_natiu
visites = session.query(Visita).filter(Visita.pais_natiu == None).all()

for v in visites:
    codi = v.codi_pais_natiu or "DESCONEGUT"
    try:
        v.pais_natiu = pycountry.countries.get(alpha_2=codi).name
    except:
        v.pais_natiu = "Desconegut"

print(f"S'han processat {len(visites)} registres antics i s'han actualitzat pais natiu.")

# Recuperem tots els registres que encara no tenen info de geolocalització
visites = session.query(Visita).filter(Visita.lat == None).all()

for v in visites:
    geo = obtenir_geo(v.ip)
    if geo:
        v.lat = geo["lat"]
        v.lon = geo["lon"]
        v.ciutat = geo["ciutat"]
        v.regio = geo["regio"]
        v.pais_fisic = geo["pais_fisic"]
        v.codi_pais_fisic = geo["codi_pais_fisic"]
        v.zip = geo["zip"]
        v.isp = geo["isp"]
        v.org = geo["org"]
        v.as_name = geo["as_name"]
        print("OK:", v.ip)
    else:
        print("FAIL:", v.ip)

print(f"S'han processat {len(visites)} registres antics i s'han actualitzat geolocalitzacio.")


session.commit()
session.close()

