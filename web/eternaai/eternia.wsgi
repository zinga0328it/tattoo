#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os

# Percorso applicazione
sys.path.insert(0, '/home/alex/web/eternaai')

# Ambiente produzione
os.environ['FLASK_ENV'] = 'production'

# Aggiungi il virtual environment al path
venv_path = '/home/alex/web/eternaai/venv/lib/python3.10/site-packages'
sys.path.insert(0, venv_path)

# Importa applicazione
from app import app as application

# Debug
print("WSGI loaded successfully", file=sys.stderr)
