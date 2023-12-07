from flask import redirect, render_template, session
from functools import wraps
import re

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

def get_field_name(input_value):
    dict = {
        "HD2021.Institution size category'": "SIZE_COLUMN",
        "HD2021.Institutional category'": "INSTITUTION_CATEGORY_COLUMN",
        "HD2021.Bureau of Economic Analysis (BEA) regions'": "REGION_COLUMN",
        "HD2021.Institution size category'": "SIZE_COLUMN",
        "HD2021.FIPS state code": "STATE_COLUMN",
        "HD2021.Control of institution": "GRADUATION_RATE_COLUMN",
        "DRVGR2021_RV.Graduation rate, total cohort": "GRADUATION_RATE_COLUMN",
        "DRVADM2021_RV.Percent admitted - total": "ADMISSIONS_COLUMN",
        "HD2021.Degree of urbanization (Urban-centric locale)": "URBANIZATION_COLUMN",
        "SFA2021_RV.Average net price-students awarded grant or scholarship aid, 2020-21 Public": "NET_PRICE_PUBLIC_COLUMN",
        "SFA2021_RV.Average net price-students awarded grant or scholarship aid, 2020-21 Private": "NET_PRICE_PRIVATE_COLUMN",
        "Combined Net Price": "NET_PRICE_COLUMN",
        }
    # Return the key associated with the input_value
    return dict.get(input_value)


def is_strong_password(password):
    # Check if the password meets strength requirements:
    # 8 characters
    if len(password) < 8:
        return False

    # Check if the password contains at least one special character or a number
    if not re.search(r"[!@#$%^&*()_+{}\[\]:;<>,.?~\\/\d]", password):
        return False

    return True

