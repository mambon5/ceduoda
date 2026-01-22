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
import pycountry
# app.py
import csv
from io import StringIO
from crea_dades import  engine
from models import Visita
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from datetime import datetime
from geo import obtenir_geo

from user_agents import parse
from estadistiques import generar_estadistiques


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
    # 👉 afegim idioma dins el diccionari perquè el frontend el pugui llegir
    content["lang_code"] = lang_code

    return render_template("index.html", lang=lang_code, content=content)

@app.route('/registre_click', methods=['POST'])
def registre_click():

    if request.is_json:
        data = request.get_json()
    else:
        data = json.loads(request.data.decode('utf-8'))  # <-- per sendBeacon

    # print("data: ")
    # print(data)

    # 🔒 Bloquejar crides externes manuals
    # if request.headers.get("X-Requested-With") != "XMLHttpRequest":
    #     return jsonify({"status": "blocked"}), 403
    # 🔒 Bloquejar crides externes manuals només si no ve del client
    # Permetre peticions AJAX i sendBeacon
    # Permetre AJAX, sendBeacon i JSON
    if request.content_type not in ["application/json", "text/plain;charset=UTF-8"]:
        return jsonify({"status": "blocked"}), 403


    
    # print("reached here")


    # data = request.get_json() or {}
    pagina = data.get('pagina', 'desconeguda')
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    referer = data.get('referer')
    idioma = data.get('idioma')
    idioma_base=data.get("idioma_base", "")  # nou camp
    codi_pais_natiu=data.get("codi_pais_natiu")
    try:
        pais_natiu = pycountry.countries.get(alpha_2=codi_pais_natiu).name
    except:
        pais_natiu = "Desconegut"
    durada = data.get('durada')
    resolucio = data.get('resolucio')
    
    # info del dispositiu que ens visita:    
    ua = parse(user_agent)
    if ua.is_mobile:
        tipus = "mobil"
    elif ua.is_tablet:
        tipus = "tablet"
    elif ua.is_pc:
        tipus = "pc"
    else:
        tipus = "altres"
    
    hora_local = data.get("hora_local")
    zona_horaria = data.get("zona_horaria")
    scroll_max = data.get("scroll_max")



    sessio = Session()
    visita = Visita(
        data_hora=datetime.utcnow(),
        ip=ip,
        pagina=pagina,
        user_agent=user_agent,
        referer=referer,
        idioma=idioma,
        idioma_base=idioma_base,
        codi_pais_natiu=codi_pais_natiu,
        pais_natiu=pais_natiu,
        durada=durada,
        resolucio=resolucio,
        geolocalitzacio=None,

        #info dispositiu
        tipus_dispositiu = tipus,
        navegador = ua.browser.family,
        sistema_operatiu = ua.os.family,
        model_dispositiu = ua.device.family,

        hora_local = hora_local,
        zona_horaria = zona_horaria,
        scroll_max = scroll_max

    )

    # obtenir info geolocalització
    geo = obtenir_geo(ip)
    if geo:
        visita.lat = geo["lat"]
        visita.lon = geo["lon"]
        visita.ciutat = geo["city"]
        visita.regio = geo["regio"]
        visita.pais_fisic = geo["pais_fisic"]
        visita.codi_pais_fisic = geo["codi_pais_fisic"]
        visita.zip = geo["zip"]
        visita.isp = geo["isp"]
        visita.org = geo["org"]
        visita.as_name = geo["as_name"]

    sessio.add(visita)
    try:
        sessio.commit()
    except Exception as e:
        sessio.rollback()
        print("Error guardant visita:", e)
    finally:
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

    columnes = [c.name for c in Visita.__table__.columns]

    def generar_csv():
        output = StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        writer.writerow(columnes)

        for visita in visites:
            fila = [getattr(visita, col) for col in columnes]
            writer.writerow(fila)
            yield output.getvalue()
            output.seek(0)
            output.truncate(0)

    return Response(generar_csv(), mimetype='text/csv',
                    headers={"Content-Disposition": "attachment;filename=visites.csv"})

# @app.route('/estadistiques')
# def estadistiques():
#     sessio = Session()
#     resultats = sessio.query(
#         Visita.pagina,
#         func.count(Visita.id).label('total')
#     ).group_by(Visita.pagina).order_by(func.count(Visita.id).desc()).all()
#     sessio.close()

#     return render_template("estadistiques.html", estadistiques=resultats)

@app.route('/estadistiques')
def estadistiques():
    generar_estadistiques()
    return render_template("estadistiques.html")


if __name__ == "__main__":
    app.run(debug=True)