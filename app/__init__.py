import os
from flask import Flask

# Ruta absoluta a la carpeta de templates
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates"))

app = Flask(__name__, template_folder=template_dir)

from . import routes
