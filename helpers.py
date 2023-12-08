# import libraries
from flask import redirect, render_template, session
from functools import wraps
import re

# Decorates routes to require login
def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

def is_strong_password(password):
    # Check if the password meets strength requirements:
    # 8 characters
    if len(password) < 8:
        return False

    # Check if the password contains at least one special character or a number
    if not re.search(r"[!@#$%^&*()_+{}\[\]:;<>,.?~\\/\d]", password):
        return False

    return True

