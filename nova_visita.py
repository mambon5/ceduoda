# afegeix_visita.py
from crea_dades import Visita, engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Session = sessionmaker(bind=engine)
sessio = Session()

nova_visita = Visita(data_hora=datetime.utcnow(), ip='127.0.0.1', pagina='pag_principal')
sessio.add(nova_visita)
sessio.commit()
sessio.close()
