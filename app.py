# Estructura del projecte:
# ├── app.py
# ├── templates/
# │   └── index.html
# └── static/
#     ├── css/
#     │   └── style.css
#     └── images/

from flask import Flask, render_template, request, redirect
import json
import os

app = Flask(__name__)

def load_translation(lang_code):
    try:
        # Aquí carregues la traducció real (ex: fitxer JSON, diccionari, etc.)
        with open(f"static/translations/{lang_code}.json", "r", encoding="utf-8") as f:
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

if __name__ == "__main__":
    app.run(debug=True)
