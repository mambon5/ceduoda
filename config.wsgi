import sys
import logging
import site

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
logging.debug("Starting WSGI application")

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

# Afegir site-packages del venv
site.addsitedir('/var/www/ceduoda/venv/lib/python3.12/site-packages') # Ajusta python3.12 a la teva versió si és .10/.11

# Ruta del projecte
sys.path.insert(0, '/var/www/ceduoda')

from app import app as application
logging.debug("WSGI application loaded")
