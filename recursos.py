import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, send_from_directory, abort
from sqlalchemy.orm import sessionmaker, joinedload, subqueryload
from sqlalchemy import or_
from werkzeug.utils import secure_filename
from crea_dades import engine
from models import User, Recurso, Pissarra
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
STATIC_PISSARRES_DIR = os.path.join(STATIC_RECURSOS_DIR, "pissarres")
os.makedirs(STATIC_PISSARRES_DIR, exist_ok=True)
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
    user = {"id": session.get("user_id"), "username": session.get("username"), "role": session.get("role")}
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
            session["role"] = user.role
            flash("Login correcte", "success")
            return redirect(url_for("recursos.recursos_list"))
        flash("Usuari o contrasenya incorrectes", "danger")
    return render_template("recursos_login.html", lang=lang, content=content)

@bp.route("/recursos/logout")
def recursos_logout():
    session.pop("user_id", None)
    session.pop("username", None)
    session.pop("role", None)
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

@bp.route("/recursos/pissarres")
def pissarra_list():
    lang = get_current_lang()
    content = load_translation(lang)
    sess = Session()
    
    current_user_id = session.get("user_id")
    user_role = session.get("role")
    
    q = sess.query(Pissarra).options(
        joinedload(Pissarra.uploader),
        joinedload(Pissarra.last_editor),
        subqueryload(Pissarra.shared_users)
    )
    
    if current_user_id:
        if user_role != 'admin':
            q = q.filter(
                or_(
                    Pissarra.uploader_id == current_user_id,
                    Pissarra.shared_users.any(id=current_user_id),
                    Pissarra.is_public == True
                )
            )
    else:
        q = q.filter(Pissarra.is_public == True)
        
    boards = q.order_by(Pissarra.updated_at.desc()).all()
    
    # Get all users for sharing dropdown (only if logged in)
    all_users = []
    if current_user_id:
        all_users = sess.query(User).order_by(User.username).all()

    sess.close()
    user = {"id": current_user_id, "username": session.get("username"), "role": user_role}
    return render_template("pissarra_list.html", boards=boards, user=user, all_users=all_users, lang=lang, content=content)

@bp.route("/recursos/pissarres/nova", methods=["POST"])
def pissarra_nova():
    if "user_id" not in session:
        return abort(403)
    title = request.form.get("title", "Sense títol").strip()
    
    # Check for unique title
    sess = Session()
    existing = sess.query(Pissarra).filter_by(title=title).first()
    if existing:
        sess.close()
        flash(f"Ja existeix una pissarra amb el títol '{title}'. Tria un altre nom.", "danger")
        return redirect(url_for("recursos.pissarra_list"))
    
    filename = f"{int(datetime.utcnow().timestamp())}_{session['user_id']}.json"
    initial_data = {"version": "5.3.0", "objects": []}
    with open(os.path.join(STATIC_PISSARRES_DIR, filename), "w") as f:
        json.dump(initial_data, f)
    
    new_board = Pissarra(
        title=title,
        filename=filename,
        uploader_id=session["user_id"],
        last_editor_id=session["user_id"]
    )
    sess.add(new_board)
    sess.commit()
    bid = new_board.id
    sess.close()
    return redirect(url_for("recursos.pissarra_editor", board_id=bid))

@bp.route("/recursos/pissarres/editor/<int:board_id>")
def pissarra_editor(board_id):
    sess = Session()
    b = sess.query(Pissarra).get(board_id)
    if not b:
        sess.close(); return abort(404)
        
    # Check permissions
    current_user_id = session.get("user_id")
    is_admin = session.get("role") == 'admin'
    is_owner = b.uploader_id == current_user_id if current_user_id else False
    is_shared = any(u.id == current_user_id for u in b.shared_users) if current_user_id else False
    is_public = b.is_public
    
    if not (is_admin or is_owner or is_shared or is_public):
        sess.close()
        if current_user_id:
            flash("No tens permís per veure aquesta pissarra.", "danger")
            return redirect(url_for("recursos.pissarra_list"))
        else:
            return abort(403)  # Or redirect to login

    p = os.path.join(STATIC_PISSARRES_DIR, b.filename)
    cdata = "{}"
    if os.path.exists(p):
        with open(p, "r") as f: cdata = f.read()
    sess.close()
    l = get_current_lang()
    cnt = load_translation(l)
    can_edit = current_user_id and (is_admin or is_owner or is_shared or is_public)
    return render_template("pissarra_editor.html", board=b, canvas_data=cdata, lang=l, content=cnt, is_owner=is_owner or is_admin, can_edit=can_edit)

@bp.route("/recursos/pissarres/guardar/<int:board_id>", methods=["POST"])
def pissarra_guardar(board_id):
    if "user_id" not in session: return abort(403)
    d = request.get_json()
    sess = Session()
    b = sess.query(Pissarra).get(board_id)
    if not b: sess.close(); return abort(404)
    
    # Check permissions (Owner, admin, shared, or public can edit/save)
    current_user_id = session["user_id"]
    is_admin = session.get("role") == 'admin'
    is_owner = b.uploader_id == current_user_id
    is_shared = any(u.id == current_user_id for u in b.shared_users)
    is_public = b.is_public
    
    if not (is_admin or is_owner or is_shared or is_public):
        sess.close()
        return abort(403)

    p = os.path.join(STATIC_PISSARRES_DIR, b.filename)
    with open(p, "w") as f: json.dump(d, f)
    b.last_editor_id = session["user_id"]
    b.updated_at = datetime.utcnow()
    sess.commit(); sess.close()
    return {"status": "ok"}

@bp.route("/recursos/pissarres/eliminar/<int:board_id>", methods=["POST"])
def pissarra_eliminar(board_id):
    if "user_id" not in session: return abort(403)
    sess = Session()
    b = sess.query(Pissarra).get(board_id)
    if not b: sess.close(); return abort(404)
    
    # Check permissions (Delete ONLY Owner or Admin)
    current_user_id = session["user_id"]
    is_admin = session.get("role") == 'admin'
    is_owner = b.uploader_id == current_user_id
    
    if not (is_admin or is_owner):
        sess.close()
        flash("Només el creador o un administrador pot esborrar.", "danger")
        return redirect(url_for("recursos.pissarra_list"))

    p = os.path.join(STATIC_PISSARRES_DIR, b.filename)
    if os.path.exists(p): os.remove(p)
    sess.delete(b); sess.commit(); sess.close()
    return redirect(url_for("recursos.pissarra_list"))

@bp.route("/recursos/pissarres/compartir/<int:board_id>", methods=["POST"])
def pissarra_compartir(board_id):
    if "user_id" not in session: return abort(403)
    username_to_add = request.form.get("username")
    
    sess = Session()
    b = sess.query(Pissarra).get(board_id)
    if not b: sess.close(); return abort(404)
    
    # Check permissions (Share allowed for Owner or Admin)
    current_user_id = session["user_id"]
    is_admin = session.get("role") == 'admin'
    is_owner = b.uploader_id == current_user_id
    
    if not (is_admin or is_owner):
        sess.close()
        flash("No tens permís per compartir aquesta pissarra.", "danger")
        return redirect(url_for("recursos.pissarra_list"))
        
    user_to_add = sess.query(User).filter_by(username=username_to_add).first()
    if not user_to_add:
        sess.close()
        flash(f"L'usuari {username_to_add} no existeix.", "warning")
        return redirect(url_for("recursos.pissarra_list"))
        
    if user_to_add not in b.shared_users:
        b.shared_users.append(user_to_add)
        sess.commit()
        flash(f"Pissarra compartida amb {username_to_add}.", "success")
    else:
        flash(f"L'usuari ja té accés.", "info")
        
    sess.close()
    return redirect(url_for("recursos.pissarra_list"))

@bp.route("/recursos/pissarres/toggle_public/<int:board_id>", methods=["POST"])
def pissarra_toggle_public(board_id):
    if "user_id" not in session: return abort(403)
    
    sess = Session()
    b = sess.query(Pissarra).get(board_id)
    if not b: sess.close(); return abort(404)
    
    # Only owner or admin can toggle visibility
    current_user_id = session["user_id"]
    is_admin = session.get("role") == 'admin'
    is_owner = b.uploader_id == current_user_id
    
    if not (is_admin or is_owner):
        sess.close()
        flash("Només el creador o un administrador pot canviar la visibilitat.", "danger")
        return redirect(url_for("recursos.pissarra_list"))
    
    # Toggle
    b.is_public = not b.is_public
    sess.commit()
    status = "pública" if b.is_public else "privada"
    flash(f"La pissarra '{b.title}' ara és {status}.", "success")
    sess.close()
    return redirect(url_for("recursos.pissarra_list"))

@bp.route("/recursos/users/create", methods=["POST"])
def user_create():
    if "user_id" not in session or session.get("role") != 'admin':
        return abort(403)
        
    username = request.form.get("username")
    password = request.form.get("password")
    role = request.form.get("role", "user")
    
    if not username or not password:
        flash("Falten dades.", "warning")
        return redirect(url_for("recursos.pissarra_list"))
        
    sess = Session()
    if sess.query(User).filter_by(username=username).first():
        sess.close()
        flash("L'usuari ja existeix.", "danger")
        return redirect(url_for("recursos.pissarra_list"))
        
    new_user = User(username=username, role=role)
    new_user.set_password(password)
    sess.add(new_user)
    sess.commit()
    sess.close()
    flash(f"Usuari {username} creat correctament.", "success")
    flash(f"Usuari {username} creat correctament.", "success")
    return redirect(request.referrer or url_for("recursos.pissarra_list"))

# opcional: servir fitxers pujats (normalment ja es serveixen des de /static)
@bp.route("/recursos/static/<path:filename>")
def recursos_static(filename):
    return send_from_directory(STATIC_RECURSOS_DIR, filename)