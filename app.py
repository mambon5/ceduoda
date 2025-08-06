# Estructura del projecte:
# ├── app.py
# ├── templates/
# │   └── index.html
# └── static/
#     ├── css/
#     │   └── style.css
#     └── images/

from flask import Flask, render_template, request, redirect, jsonify, Response
import json
import os
# app.py
from crea_dades import Visita, Base, engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from datetime import datetime

app = Flask(__name__)
Session = sessionmaker(bind=engine)

def load_translation(lang_code):
    try:
        # Aquí carregues la traducció real (ex: fitxer JSON, diccionari, etc.)
        with open(f"/var/www/ceduoda/static/translations/{lang_code}.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        if lang_code != "ca":
            return load_translation("ca")  # Fallback només si no és "ca"
        else:
            raise  # Si també falta el "ca", llença l'error original


@app.route("/")
def redirect_home():
    # Opcional: redirigir segons idioma del navegador
    user_lang = request.accept_languages.best_match(['ca', 'es', 'en']) or 'ca'
    return redirect(f"/{user_lang}")

@app.route("/<lang_code>")
def home(lang_code):
    if lang_code not in ['ca', 'es', 'en']:
        lang_code = 'ca'

    content = load_translation(lang_code)
    return render_template("index.html", lang=lang_code, content=content)


# @app.route('/registre_click', methods=['POST'])
# def registre_click():
#     data = request.json
#     pagina = data.get('pagina', 'desconeguda')
#     ip = request.remote_addr

#     sessio = Session()
#     visita = Visita(data_hora=datetime.utcnow(), ip=ip, pagina=pagina)
#     sessio.add(visita)
#     sessio.commit()
#     sessio.close()

#     return jsonify({'status': 'ok'})

@app.route('/registre_click', methods=['POST'])
def registre_click():
    data = request.get_json() or {}
    pagina = data.get('pagina', 'desconeguda')
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent')
    referer = data.get('referer')
    idioma = data.get('idioma')
    durada = data.get('durada')
    resolucio = data.get('resolucio')
    
    # Aquí poso un valor per geolocalització si tens una funció (opcional)
    # geolocalitzacio = obtenir_geolocalitzacio_des_ip(ip)  # definir després o deixar None
    geolocalitzacio = None

    sessio = Session()
    visita = Visita(
        data_hora=datetime.utcnow(),
        ip=ip,
        pagina=pagina,
        user_agent=user_agent,
        referer=referer,
        idioma=idioma,
        durada=durada,
        resolucio=resolucio,
        geolocalitzacio=geolocalitzacio
    )
    sessio.add(visita)
    sessio.commit()
    sessio.close()

    return jsonify({'status': 'ok'})

@app.route("/visites")
def veure_visites():
    sessio = Session()
    visites = sessio.query(Visita).order_by(Visita.data_hora.desc()).all()
    sessio.close()
    return render_template("visites.html", visites=visites)

@app.route('/descarrega_visites')
def descarrega_visites():
    sessio = Session()
    visites = sessio.query(Visita).order_by(Visita.data_hora.desc()).all()
    sessio.close()

    def generar_csv():
        yield 'data_hora,ip,pagina,idioma,resolucio,referer,durada\n'
        for visita in visites:
            fila = f'"{visita.data_hora}","{visita.ip}","{visita.pagina}","{visita.idioma}","{visita.resolucio}","{visita.referer}","{visita.durada}"\n'
            yield fila

    return Response(generar_csv(), mimetype='text/csv',
                    headers={"Content-Disposition": "attachment;filename=visites.csv"})


@app.route('/estadistiques')
def estadistiques():
    sessio = Session()
    resultats = sessio.query(
        Visita.pagina,
        func.count(Visita.id).label('total')
    ).group_by(Visita.pagina).order_by(func.count(Visita.id).desc()).all()
    sessio.close()

    return render_template("estadistiques.html", estadistiques=resultats)


if __name__ == "__main__":
    app.run(debug=True)