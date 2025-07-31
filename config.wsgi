import sys
import logging

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
logging.debug("Starting WSGI application")

sys.path.insert(0, '/var/www/ceduoda')

from app import app as application

logging.debug("WSGI application loaded")
