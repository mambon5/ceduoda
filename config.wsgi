import sys
import logging

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
logging.debug("Starting WSGI application")

# Afegim el path del projecte
sys.path.insert(0, '/var/www/ceduoda')

# Importem l'aplicació directament
from app import app as application

logging.debug("WSGI application loaded")
