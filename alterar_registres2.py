from sqlalchemy.orm import Session
from sqlalchemy import create_engine, or_
from models import Visita
from config import SQLALCHEMY_DATABASE_URL

import pycountry
from geo import obtenir_geo
import user_agents


# ------------------------------------------------------------------
# Connexió BD
# ------------------------------------------------------------------
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)
session = Session(bind=engine)


# ------------------------------------------------------------------
# 1️⃣ IDIOMA BASE + CODI PAÍS NATIU
# ------------------------------------------------------------------
visites = session.query(Visita).filter(
    or_(
        Visita.idioma_base == None,
        Visita.codi_pais_natiu == None
    )
).all()

for v in visites:
    if v.idioma:
        idioma_net = v.idioma.replace("_", "-").strip()
        parts = idioma_net.split("-")

        v.idioma_base = parts[0].lower() if parts[0] else "desconegut"

        if len(parts) > 1 and len(parts[1]) == 2:
            v.codi_pais_natiu = parts[1].upper()
        else:
            v.codi_pais_natiu = "DESCO"
    else:
        v.idioma_base = "desconegut"
        v.codi_pais_natiu = "DESCO"

print(f"[OK] Idioma base / país natiu processats: {len(visites)}")


# ------------------------------------------------------------------
# 2️⃣ PAÍS NATIU (nom humà)
# ------------------------------------------------------------------
visites = session.query(Visita).filter(
    Visita.pais_natiu == None
).all()

for v in visites:
    try:
        if v.codi_pais_natiu and v.codi_pais_natiu != "DESCO":
            country = pycountry.countries.get(alpha_2=v.codi_pais_natiu)
            v.pais_natiu = country.name if country else "Desconegut"
        else:
            v.pais_natiu = "Desconegut"
    except Exception:
        v.pais_natiu = "Desconegut"

print(f"[OK] País natiu omplert: {len(visites)}")


# ------------------------------------------------------------------
# 3️⃣ GEOLOCALITZACIÓ (només IPs reals)
# ------------------------------------------------------------------
visites = session.query(Visita).filter(
    Visita.lat == None,
    Visita.ip != None,
    Visita.ip != "127.0.0.1"
).all()

for v in visites:
    try:
        geo = obtenir_geo(v.ip)
        if not geo:
            continue

        v.lat = geo.get("lat")
        v.lon = geo.get("lon")
        v.ciutat = geo.get("ciutat")
        v.regio = geo.get("regio")
        v.pais_fisic = geo.get("pais_fisic")
        v.codi_pais_fisic = geo.get("codi_pais_fisic")
        v.zip = geo.get("zip")
        v.isp = geo.get("isp")
        v.org = geo.get("org")
        v.as_name = geo.get("as_name")

        print("[GEO OK]", v.ip)

    except Exception as e:
        print("[GEO FAIL]", v.ip, e)

print(f"[OK] Geolocalització processada: {len(visites)}")


# ------------------------------------------------------------------
# 4️⃣ DISPOSITIU / NAVEGADOR / SISTEMA
# ------------------------------------------------------------------
visites = session.query(Visita).filter(
    Visita.tipus_dispositiu == None,
    Visita.user_agent != None
).all()

for v in visites:
    try:
        ua = user_agents.parse(v.user_agent)

        if ua.is_mobile:
            v.tipus_dispositiu = "mobil"
        elif ua.is_tablet:
            v.tipus_dispositiu = "tablet"
        elif ua.is_pc:
            v.tipus_dispositiu = "pc"
        else:
            v.tipus_dispositiu = "altres"

        v.navegador = ua.browser.family
        v.sistema_operatiu = ua.os.family
        v.model_dispositiu = ua.device.family

    except Exception as e:
        print("[UA FAIL]", e)

print(f"[OK] Dispositius processats: {len(visites)}")


# ------------------------------------------------------------------
# FINAL
# ------------------------------------------------------------------
session.commit()
session.close()

print("🎉 alter_registres.py completat correctament")
