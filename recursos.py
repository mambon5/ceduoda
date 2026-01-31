import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, send_from_directory, abort
from sqlalchemy.orm import sessionmaker, joinedload
from werkzeug.utils import secure_filename
from crea_dades import engine
from models import User, Recurso
import os
from datetime import datetime

bp = Blueprint("recursos", __name__, template_folder="templates")
Session = sessionmaker(bind=engine)

def load_translation(lang_code):
    try:
        with open(f"/var/www/ceduoda/static/translations/{lang_code}.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        if lang_code != "ca":
            return load_translation("ca")
        else:
            raise

def get_current_lang():
    return request.accept_languages.best_match(['ca', 'es', 'en']) or 'ca'

# configuració
STATIC_RECURSOS_DIR = "/var/www/ceduoda/static/recursos"
os.makedirs(STATIC_RECURSOS_DIR, exist_ok=True)
ALLOWED_EXT = {"png", "jpg", "jpeg", "pdf"}

def allowed(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

@bp.route("/recursos")
def recursos_list():
    lang = get_current_lang()
    content = load_translation(lang)
    content["lang_code"] = lang
    
    sess = Session()
    recursos = sess.query(Recurso).options(joinedload(Recurso.uploader), joinedload(Recurso.last_editor)).order_by(Recurso.uploaded_at.desc()).all()
    sess.close()
    user = {"id": session.get("user_id"), "username": session.get("username")}
    return render_template("recursos.html", recursos=recursos, user=user, lang=lang, content=content)

@bp.route("/recursos/login", methods=["GET", "POST"])
def recursos_login():
    lang = get_current_lang()
    content = load_translation(lang)
    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        sess = Session()
        user = sess.query(User).filter_by(username=username).first()
        sess.close()
        if user and user.check_password(password):
            session["user_id"] = user.id
            session["username"] = user.username
            flash("Login correcte", "success")
            return redirect(url_for("recursos.recursos_list"))
        flash("Usuari o contrasenya incorrectes", "danger")
    return render_template("recursos_login.html", lang=lang, content=content)

@bp.route("/recursos/logout")
def recursos_logout():
    session.pop("user_id", None)
    session.pop("username", None)
    flash("Sessió tancada", "info")
    return redirect(url_for("recursos.recursos_list"))

@bp.route("/recursos/upload", methods=["GET", "POST"])
def recursos_upload():
    if "user_id" not in session:
        return redirect(url_for("recursos.recursos_login"))
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        link = request.form.get("link", "").strip()
        file = request.files.get("file")
        if not title:
            flash("Cal indicar un títol", "warning")
            return redirect(url_for("recursos.recursos_upload"))

        # El límit de 5MB
        if file and file.filename:
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            if file_size > 5 * 1024 * 1024:
                lang = get_current_lang()
                content = load_translation(lang)
                flash(content["recursos"].get("error_file_too_large", "El fitxer és massa gran (màx 5MB)"), "danger")
                return redirect(url_for("recursos.recursos_upload"))

        filename = None
        url = None
        file_type = None

        if link:
            url = link
            if link.lower().endswith(".pdf"):
                file_type = "pdf"
            else:
                file_type = "link"
        elif file and file.filename:
            if not allowed(file.filename):
                flash("Tipus de fitxer no permès", "danger")
                return redirect(url_for("recursos.recursos_upload"))
            filename = secure_filename(f"{int(datetime.utcnow().timestamp())}_{file.filename}")
            dest = os.path.join(STATIC_RECURSOS_DIR, filename)
            file.save(dest)
            ext = filename.rsplit(".", 1)[1].lower()
            file_type = "img" if ext in {"png","jpg","jpeg"} else ("pdf" if ext=="pdf" else "file")
        else:
            flash("Cal pujar un fitxer o indicar un enllaç", "warning")
            return redirect(url_for("recursos.recursos_upload"))

        sess = Session()
        rec = Recurso(
            title=title,
            description=description or None,
            filename=filename,
            url=url,
            file_type=file_type,
            uploader_id=session.get("user_id")
        )
        sess.add(rec)
        sess.commit()
        sess.close()
        flash("Recurs pujat correctament", "success")
        return redirect(url_for("recursos.recursos_list"))

    lang = get_current_lang()
    content = load_translation(lang)

    return render_template("recursos_upload.html", lang=lang, content=content)

@bp.route("/recursos/delete/<int:recurso_id>", methods=["POST"])
def recursos_delete(recurso_id):
    if "user_id" not in session:
        return abort(403)
    
    sess = Session()
    rec = sess.query(Recurso).get(recurso_id)
    if not rec:
        sess.close()
        return abort(404)
    
    # eliminar fitxer si existeix
    if rec.filename:
        path = os.path.join(STATIC_RECURSOS_DIR, rec.filename)
        if os.path.exists(path):
            os.remove(path)
    
    sess.delete(rec)
    sess.commit()
    sess.close()
    
    lang = get_current_lang()
    content = load_translation(lang)
    flash(content["recursos"].get("msg_deleted", "Recurs eliminat correctament."), "success")
    return redirect(url_for("recursos.recursos_list"))

@bp.route("/recursos/edit/<int:recurso_id>", methods=["GET", "POST"])
def recursos_edit(recurso_id):
    if "user_id" not in session:
        return redirect(url_for("recursos.recursos_login"))
    
    sess = Session()
    rec = sess.query(Recurso).get(recurso_id)
    if not rec:
        sess.close()
        return abort(404)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        link = request.form.get("link", "").strip()
        file = request.files.get("file")

        if not title:
            flash("Cal indicar un títol", "warning")
            return redirect(url_for("recursos.recursos_edit", recurso_id=recurso_id))

        # El límit de 5MB
        if file and file.filename:
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            if file_size > 5 * 1024 * 1024:
                lang = get_current_lang()
                content = load_translation(lang)
                flash(content["recursos"].get("error_file_too_large", "El fitxer és massa gran (màx 5MB)"), "danger")
                return redirect(url_for("recursos.recursos_edit", recurso_id=recurso_id))

        rec.title = title
        rec.description = description or None
        rec.last_editor_id = session.get("user_id")

        if link:
            rec.url = link
            rec.filename = None # si posen link, borrem fitxer? potser millor no borrar físicament encara
            if link.lower().endswith(".pdf"):
                rec.file_type = "pdf"
            else:
                rec.file_type = "link"
        elif file and file.filename:
            if not allowed(file.filename):
                flash("Tipus de fitxer no permès", "danger")
                return redirect(url_for("recursos.recursos_edit", recurso_id=recurso_id))
            
            # Borrar anterior si n'hi havia
            if rec.filename:
                old_path = os.path.join(STATIC_RECURSOS_DIR, rec.filename)
                if os.path.exists(old_path):
                    os.remove(old_path)

            filename = secure_filename(f"{int(datetime.utcnow().timestamp())}_{file.filename}")
            dest = os.path.join(STATIC_RECURSOS_DIR, filename)
            file.save(dest)
            ext = filename.rsplit(".", 1)[1].lower()
            rec.filename = filename
            rec.url = None
            rec.file_type = "img" if ext in {"png","jpg","jpeg"} else ("pdf" if ext=="pdf" else "file")

        sess.commit()
        sess.close()
        
        lang = get_current_lang()
        content = load_translation(lang)
        flash(content["recursos"].get("msg_updated", "Recurs actualitzat correctament."), "success")
        return redirect(url_for("recursos.recursos_list"))

    lang = get_current_lang()
    content = load_translation(lang)
    sess.close()
    return render_template("recursos_edit.html", recurso=rec, lang=lang, content=content)

# opcional: servir fitxers pujats (normalment ja es serveixen des de /static)
@bp.route("/recursos/static/<path:filename>")
def recursos_static(filename):
    return send_from_directory(STATIC_RECURSOS_DIR, filename)