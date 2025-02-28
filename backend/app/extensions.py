from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# ✅ Create Limiter instance WITHOUT attaching it to app
limiter = Limiter(key_func=get_remote_address)
