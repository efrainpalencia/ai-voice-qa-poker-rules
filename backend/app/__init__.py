from flask import Flask

app = Flask(__name__)

from app import chains, config, indexdata, server, processdata