import os
from collections import defaultdict
from datetime import datetime

import matplotlib
matplotlib.use("Agg")  # imprescindible en servidor
import matplotlib.pyplot as plt

from sqlalchemy.orm import sessionmaker
from crea_dades import engine
from models import Visita
from sqlalchemy import func

Session = sessionmaker(bind=engine)

OUTPUT_DIR = "/var/www/ceduoda/static/estadistiques"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def graf_visites_per_pagina(sessio):
    resultats = (
        sessio.query(
            Visita.pagina,
            func.count(Visita.id)
        )
        .group_by(Visita.pagina)
        .order_by(func.count(Visita.id).desc())
        .all()
    )

    pagines = [r[0] for r in resultats]
    totals = [r[1] for r in resultats]

    plt.figure(figsize=(10, 6))
    plt.bar(pagines, totals)
    plt.xticks(rotation=45, ha="right")
    plt.title("Nombre de visites per pàgina")
    plt.ylabel("Visites")
    plt.tight_layout()

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    plt.savefig(f"{OUTPUT_DIR}/visites_per_pagina.png")
    plt.close()

def graf_temps_mig_per_pagina(sessio):
    resultats = (
        sessio.query(
            Visita.pagina,
            func.avg(Visita.durada)
        )
        .filter(Visita.durada > 1)
        .filter(~Visita.pagina.like("canvi_idioma_%"))
        .group_by(Visita.pagina)
        .order_by(func.avg(Visita.durada).desc())
        .all()
    )

    pagines = [r[0] for r in resultats]
    temps = [round(r[1], 1) for r in resultats]

    plt.figure(figsize=(10, 6))
    plt.bar(pagines, temps)
    plt.xticks(rotation=45, ha="right")
    plt.title("Temps mitjà per pàgina (s)")
    plt.ylabel("Segons")
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/temps_mig_per_pagina.png")
    plt.close()




def generar_estadistiques():
    sessio = Session()
    visites = sessio.query(Visita).all()
    sessio.close()

    if not visites:
        print("No hi ha dades per generar estadístiques")
        return

    # =========================
    # Estructures de dades
    # =========================
    per_pagina = defaultdict(int)
    temps_per_pagina = defaultdict(list)
    scrolls = []

    dispositius = defaultdict(int)
    idiomes = defaultdict(int)

    per_dia_setmana = defaultdict(int)
    per_hora = defaultdict(int)
    per_mes = defaultdict(int)
    per_setmana = defaultdict(int)

    # =========================
    # Recorregut de dades
    # =========================
    for v in visites:
        if not v.data_hora:
            continue

        dt = v.data_hora

        # # pàgina
        # if v.pagina:
        #     per_pagina[v.pagina] += 1

        # temps
        # if v.pagina and v.durada is not None:
        #     temps_per_pagina[v.pagina].append(v.durada)

        # scroll
        if v.scroll_max is not None:
            scrolls.append(v.scroll_max)

        # dispositiu
        if v.tipus_dispositiu:
            dispositius[v.tipus_dispositiu] += 1

        # idioma
        if v.idioma_base:
            idiomes[v.idioma_base] += 1

        # dia setmana (0=dilluns)
        per_dia_setmana[dt.weekday()] += 1

        # hora
        per_hora[dt.hour] += 1

        # mes
        per_mes[dt.month] += 1

        # setmana ISO
        any_, setmana_, _ = dt.isocalendar()
        per_setmana[f"{any_}-W{setmana_:02d}"] += 1

    # =========================
    # 1️⃣ Visites per pagina
    # =========================
    graf_visites_per_pagina(sessio)

     # =========================
    # 1️⃣ temps per pagina
    # =========================
    graf_temps_mig_per_pagina(sessio)

    # =========================
    # 1️⃣ Visites per dia setmana
    # =========================
    dies = ["Dl", "Dt", "Dc", "Dj", "Dv", "Ds", "Dg"]
    valors = [per_dia_setmana[i] for i in range(7)]

    plt.figure()
    plt.bar(dies, valors)
    plt.title("Visites per dia de la setmana")
    plt.ylabel("Visites")
    plt.savefig(f"{OUTPUT_DIR}/visites_dia_setmana.png")
    plt.close()

    # =========================
    # 2️⃣ Visites per hora
    # =========================
    hores = list(range(24))
    valors = [per_hora[h] for h in hores]

    plt.figure()
    plt.bar(hores, valors)
    plt.title("Visites per hora del dia")
    plt.xlabel("Hora")
    plt.ylabel("Visites")
    plt.savefig(f"{OUTPUT_DIR}/visites_per_hora.png")
    plt.close()

    # =========================
    # 3️⃣ Visites per mes (barres horitzontals)
    # =========================
    noms_mesos = [
        "Gener", "Febrer", "Març", "Abril", "Maig", "Juny",
        "Juliol", "Agost", "Setembre", "Octubre", "Novembre", "Desembre"
    ]

    valors = [per_mes.get(i + 1, 0) for i in range(12)]

    plt.figure(figsize=(8, 5))
    plt.barh(noms_mesos, valors)
    plt.title("Visites per mes de l'any")
    plt.xlabel("Visites")
    plt.ylabel("Mes")
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/visites_per_mes.png")
    plt.close()


    # =========================
    # 4️⃣ Evolució temporal per setmana
    # =========================
    setmanes = sorted(per_setmana.keys())
    valors = [per_setmana[s] for s in setmanes]

    plt.figure(figsize=(10, 4))
    plt.plot(setmanes, valors, marker="o")
    plt.xticks(rotation=45, ha="right")
    plt.title("Evolució de visites per setmana")
    plt.ylabel("Visites")
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/evolucio_setmanal.png")
    plt.close()

    # =========================
    # 5️⃣ Histograma de scroll
    # =========================
    plt.figure()
    plt.hist(scrolls, bins=10, range=(0, 100))
    plt.title("Distribució del scroll (%)")
    plt.xlabel("Percentatge de scroll")
    plt.ylabel("Freqüència")
    plt.savefig(f"{OUTPUT_DIR}/histograma_scroll.png")
    plt.close()

    # print("📊 Estadístiques generades correctament")
