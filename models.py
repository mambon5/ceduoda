from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Table, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()

# Taula d'associació per a usuaris compartits en una pissarra
pissarra_users = Table('pissarra_users', Base.metadata,
    Column('pissarra_id', Integer, ForeignKey('pissarres.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
)

# Definició de la taula
class Visita(Base):
    __tablename__ = "visites"

    id = Column(Integer, primary_key=True, autoincrement=True)
        # ...existing code...
    def generar_estadistiques():
        import os
        from datetime import datetime
    
        sessio = Session()
        visites = sessio.query(Visita).all()
        sessio.close()
        if not visites:
            print("No hi ha dades per generar estadístiques")
            return
    
        # obtenir l'última visita (timestamp)
        últim = max((v.data_hora for v in visites if v.data_hora), default=None)
        if últim is None:
            print("Cap visita amb data_hora valida")
            return
        últim_ts = últim.timestamp()
    
        # llista d'imatges que la plantilla mostra -> veure [templates/estadistiques.html](templates/estadistiques.html)
        imatges = [
            "visites_per_pagina.png",
            "temps_mig_per_pagina.png",
            "scroll_mig_per_pagina.png",
            "dispositius.png",
            "idiomes.png",
            "visites_dia_setmana.png",
            "visites_per_hora.png",
            "visites_per_mes.png",
            "evolucio_setmanal.png",
            "evolucio_diaria.png",
        ]
        # prefix amb OUTPUT_DIR definit a aquest fitxer
        imatges_paths = [os.path.join(OUTPUT_DIR, nom) for nom in imatges]
    
        # comprovar si cal regenerar alguna imatge
        need = []
        for p in imatges_paths:
            if not os.path.exists(p):
                need.append(p)
            else:
                try:
                    if os.path.getmtime(p) < últim_ts:
                        need.append(p)
                except OSError:
                    need.append(p)
    
        if not need:
            print("Imatges actualitzades. No cal regenerar res.")
            return
        else:
            print(f"Regenerant {len(need)} imatges obsoletes: {[os.path.basename(p) for p in need]}")
    
        # ...existing code...
        # (a partir d'aquí, el codi existent continua generant totes les imatges com abans)
    # ...existing code... = Column(DateTime)
    ip = Column(String(45))
    pagina = Column(String(100))
    
    user_agent = Column(Text)       # punt 1: navegador i dispositiu
    referer = Column(Text)          # punt 2: d’on venen
    idioma = Column(String(20))     # punt 3: idioma navegador
    idioma_base = Column(String(20))     # punt 3: idioma simplificat
    pais_natiu = Column(String(50))  # nom del país basat en codi_pais_natiu
    codi_pais_natiu = Column(String(5), nullable=True)  # ex: "MX"
    durada = Column(Integer)        # punt 4: durada visita en segons (nullable = pot ser zero o None)
    resolucio = Column(String(20))  # punt 6: resolució pantalla (ex: "1920x1080")
    geolocalitzacio = Column(String(100))  # punt 8: info geolocalització aprox (ex: "Barcelona, Espanya")

    # geolocalitzacio detallada
    lat = Column(String(20))
    lon = Column(String(20))
    ciutat = Column(String(100))
    regio = Column(String(100))
    pais_fisic = Column(String(100))
    codi_pais_fisic = Column(String(5))
    zip = Column(String(15))
    isp = Column(String(150))
    org = Column(String(150))
    as_name = Column(String(150))

    # Informació del dispositiu
    tipus_dispositiu = Column(String(20))
    navegador = Column(String(30))
    sistema_operatiu = Column(String(30))
    model_dispositiu = Column(String(50))

    hora_local = Column(String(40))
    zona_horaria = Column(String(40))
    scroll_max = Column(Integer)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    role = Column(String(20), default="user", nullable=False) # 'admin' or 'user'
    created_at = Column(DateTime, default=datetime.utcnow)

    def set_password(self, plaintext):
        self.password_hash = generate_password_hash(plaintext)

    def check_password(self, plaintext):
        return check_password_hash(self.password_hash, plaintext)

class Recurso(Base):
    __tablename__ = "recursos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    filename = Column(String(300), nullable=True)   # si s'ha pujat un fitxer
    url = Column(String(500), nullable=True)        # si és un enllaç extern
    file_type = Column(String(20), nullable=True)   # 'pdf','img','link'
    uploader_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    uploader = relationship("User", backref="recursos", foreign_keys=[uploader_id])
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    last_editor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    last_editor = relationship("User", foreign_keys=[last_editor_id])
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Pissarra(Base):
    __tablename__ = "pissarres"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    filename = Column(String(300), nullable=False) # fitxer .json on es guarda el canvas
    uploader_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    uploader = relationship("User", foreign_keys=[uploader_id])
    last_editor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    last_editor = relationship("User", foreign_keys=[last_editor_id])
    
    is_public = Column(Boolean, default=False)
    
    # Usuaris amb qui s'ha compartit (a part de l'uploader)
    shared_users = relationship("User", secondary=pissarra_users, backref="shared_pissarres")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


