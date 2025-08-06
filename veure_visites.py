from crea_dades import Visita, engine
from sqlalchemy.orm import sessionmaker

# Crear sessió
Session = sessionmaker(bind=engine)
sessio = Session()

# Consultar totes les visites
visites = sessio.query(Visita).order_by(Visita.data_hora.desc()).all()

# Mostrar les visites
for visita in visites:
    print(f"{visita.data_hora} - IP: {visita.ip} - Pàgina: {visita.pagina}")

# Tancar sessió
sessio.close()
