from flask_cors import CORS
from app import server
from flask import Flask

app = Flask(__name__)
CORS(app)
