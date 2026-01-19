import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Visita  # 👈 importa la teva classe ORM de Visita

# ----------------------------
# Configura la connexió a la BD
# ----------------------------
DATABASE_URL = "sqlite:///visites.db"  # canvia al teu URL si no és sqlite
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# ----------------------------
# Funció per generar les estadístiques
# ----------------------------
def generar_estadistiques():
    sessio = Session()
    
    # Carreguem totes les visites en un DataFrame
    df = pd.read_sql(sessio.query(Visita).statement, sessio.bind)
    sessio.close()
    
    if df.empty:
        print("No hi ha dades per generar estadístiques.")
        return
    
    # ----------------------------
    # 1️⃣ Nombre de visites per pàgina
    # ----------------------------
    visits_per_page = df.groupby("pagina").size().reset_index(name="visites")
    fig_visites = px.bar(visits_per_page, x="pagina", y="visites",
                         title="Nombre de visites per pàgina", text="visites")
    fig_visites.update_layout(xaxis_title="Pàgina / Secció", yaxis_title="Visites")
    fig_visites.write_html("estadistiques_visites.html", include_plotlyjs="cdn")
    
    # ----------------------------
    # 2️⃣ Temps mitjà i scroll mitjà per pàgina
    # ----------------------------
    summary = df.groupby("pagina").agg(
        temps_mig=("durada", "mean"),
        scroll_mig=("scroll_max", "mean")
    ).reset_index()
    
    fig_temps = px.bar(summary, x="pagina", y="temps_mig",
                       title="Temps mitjà per pàgina (s)", text="temps_mig")
    fig_scroll = px.bar(summary, x="pagina", y="scroll_mig",
                        title="Scroll mitjà per pàgina (%)", text="scroll_mig")
    
    fig_temps.update_layout(xaxis_title="Pàgina / Secció", yaxis_title="Temps mitjà (s)")
    fig_scroll.update_layout(xaxis_title="Pàgina / Secció", yaxis_title="Scroll mitjà (%)")
    
    fig_temps.write_html("temps_mig_per_pagina.html", include_plotlyjs="cdn")
    fig_scroll.write_html("scroll_mig_per_pagina.html", include_plotlyjs="cdn")
    
    # ----------------------------
    # 3️⃣ Distribució d'idiomes
    # ----------------------------
    idiomes = df.groupby("idioma_base").size().reset_index(name="visites")
    fig_idiomes = px.pie(idiomes, names="idioma_base", values="visites", title="Distribució d'idiomes")
    fig_idiomes.write_html("idiomes.html", include_plotlyjs="cdn")
    
    # ----------------------------
    # 4️⃣ Distribució de dispositius
    # ----------------------------
    dispositius = df.groupby("tipus_dispositiu").size().reset_index(name="visites")
    fig_disp = px.pie(dispositius, names="tipus_dispositiu", values="visites", title="Distribució de dispositius")
    fig_disp.write_html("dispositius.html", include_plotlyjs="cdn")
    
    print("Les estadístiques s'han generat correctament en fitxers HTML.")

# ----------------------------
# Executar si cridem directament
# ----------------------------
if __name__ == "__main__":
    generar_estadistiques()
