from unittest import TestCase
from app import app
from flask import session
import pdb

app.config['WTF_CSRF_ENABLED'] = False
