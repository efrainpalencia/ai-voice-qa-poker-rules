import logging
from flask import Flask
from flask_cors import CORS


app = Flask(__name__)
CORS(app)


logger = logging.getLogger(__name__)

if __name__ == '__main__':
    print("🚀 Recipe Service is running on port 8000")
    app.run("127.0.0.1", 8000, debug=True)
