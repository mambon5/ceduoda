from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, send_from_directory, abort
from werkzeug.utils import secure_filename
from sqlalchemy.orm import sessionmaker
from crea_dades import engine
from models import User, Recurso
import os
from datetime import datetime

bp = Blueprint("recursos", __name__, template_folder="templates")
Session = sessionmaker(bind=engine)

# configuració
STATIC_RECURSOS_DIR = "/var/www/ceduoda/static/recursos"
os.makedirs(STATIC_RECURSOS_DIR, exist_ok=True)
ALLOWED_EXT = {"png", "jpg", "jpeg", "pdf"}

def allowed(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

@bp.route("/recursos")
def recursos_list():
    sess = Session()
    recursos = sess.query(Recurso).order_by(Recurso.uploaded_at.desc()).all()
    sess.close()
    user = {"id": session.get("user_id"), "username": session.get("username")}
    return render_template("recursos.html", recursos=recursos, user=user)

@bp.route("/recursos/login", methods=["GET", "POST"])
def recursos_login():
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
    return render_template("recursos_login.html")

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

    return render_template("recursos_upload.html")

# opcional: servir fitxers pujats (normalment ja es serveixen des de /static)
@bp.route("/recursos/static/<path:filename>")
def recursos_static(filename):
    return send_from_directory(STATIC_RECURSOS_DIR, filename)