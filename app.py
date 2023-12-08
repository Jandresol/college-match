# Import libraries
import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, url_for, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, is_strong_password
from match import load_data, clean_data, calculate_total_match
from constants import REGION_COLUMN, STATE_COLUMN, questions, form_fields, weights

# Configure application
app = Flask(__name__)
app.secret_key = "your_secret_key"

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///users.db")

# Load and clean data
df = load_data("college_data.csv")
df = clean_data(df)
region_values = df[REGION_COLUMN].unique().tolist()
state_values = df[STATE_COLUMN].unique().tolist()

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Modifies the response headers to prevent caching
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Inject username variable into context of all templates so it can be accessed globally
@app.context_processor
def inject_user():
    if "user_id" in session:
        # Get current user's id from the session
        user_id = session["user_id"]
        # make username a globally accesible variable
        username = db.execute("SELECT username FROM users WHERE id = ?", user_id)[0][
            "username"
        ]
        return dict(username=username)
    else:
        return {}


# Main route - home page
@app.route("/")
def home():
    # if the user has logged in...
    if "user_id" in session:
        # get user id from session
        user_id = session["user_id"]
        # check database to see if user has taken the survey already
        survey_completed = db.execute(
            "SELECT survey_completed FROM users WHERE id = ?", user_id
        )[0]["survey_completed"]

        # if the user has already taken the survey... show their results
        if survey_completed:
            # Fetch survey results from the database for the given user_id
            survey_results = db.execute(
                "SELECT REGION_COLUMN, STATE_COLUMN, SIZE_COLUMN, CONTROL_COLUMN, GRADUATION_RATE_COLUMN, ADMISSIONS_COLUMN, URBANIZATION_COLUMN, NET_PRICE_COLUMN FROM survey_results WHERE user_id = ?",
                user_id,
            )
            survey_values = []
            survey_values = list(survey_results[0].values())

            # Create a dictionary to hold the user's preferences
            user_preferences = {}

            # Set user preferences based on survey results
            for i, field in enumerate(form_fields):
                user_preferences[field] = survey_values[i]

            # Calculate the total match using the matching function in match.py
            total_score = calculate_total_match(df, weights, user_preferences)
            # Create a new column in the CSV that inputs the match score
            df["Percent_Match"] = total_score
            # Sort the colleges by closest match and only show the top 10 matches
            sorted_data = df.sort_values(by="Percent_Match", ascending=False)
            top_ten_data = sorted_data.head(10)
            results_html = top_ten_data[["institution name", "Percent_Match"]].to_html(
                index=False
            )

            # Pass top_ten_data to the template
            return render_template(
                "results.html", results_html=results_html, top_ten_data=top_ten_data
            )

        # if the user hasn't already completed the survey...
        elif not survey_completed:
            # render a page instructing the user to go take the survey
            return render_template("waiting.html")

    # if the user is not logged in...
    else:
        # render the main landing page
        return render_template("landing.html")


# Route for survey page
@app.route("/survey", methods=["GET", "POST"])
@login_required
def survey():
    # get user id from session
    user_id = session["user_id"]
    # check database to see if user has taken the survey already
    survey_completed = db.execute(
        "SELECT survey_completed FROM users WHERE id = ?", user_id
    )[0]["survey_completed"]

    # if the user presses the take survey button...
    if request.method == "POST":
        # take the user to the first step of the survey
        return redirect("/step/1")

    # else, if they haven't taken the survey yet...
    elif not survey_completed:
        # show the main survey page inviting them to take it
        return render_template("survey.html")

    # else, if they have taken the survey...
    elif survey_completed:
        # render the page saying that they have taken the survey and inviting them to retake it
        return render_template("survey_completed.html")


# Route for retaking the survey
@app.route("/retake-survey", methods=["GET", "POST"])
@login_required
def retake_survey():
    # If the user presses the button to retake the survey...
    if request.method == "POST":
        # Redirect the user to a route to confirm their decision
        return redirect("/confirm-retake")

    return render_template("confirm_retake.html")


# Route for confirming a retake of the survey
@app.route("/confirm-retake", methods=["GET", "POST"])
@login_required
def confirm_retake():
    # Get user id from session
    user_id = session["user_id"]
    # Record that the survey has not been completed for user in database
    try:
        db.execute("UPDATE users SET survey_completed = ? WHERE id = ?", False, user_id)
    except Exception as e:
        flash("500: AN ERROR OCCURED")
        return redirect("/confirm-retake")
    # Redirect user to main survey route
    return redirect("/survey")


# Route for 1st step of survey
@app.route("/step/1", methods=["GET", "POST"])
@login_required
def step1():
    # Get user id from session
    user_id = session["user_id"]

    # If user presses next button (ie. submits form)
    if request.method == "POST":
        # Get the value from form
        value = request.form.get(form_fields[0])
        if not value:
            value = 0

        # Save the value in the survey_results table in the database
        try:
            db.execute(
                "UPDATE survey_results SET REGION_COLUMN=? where user_id=?",
                value,
                user_id,
            )
        except Exception as e:
            flash("500: AN ERROR OCCURED")
            return redirect("/step/1")

        # Send the user to step 2
        return redirect("/step/2")

    return render_template(
        "step_1.html",
        region_values=region_values,
        state_values=state_values,
        form_fields=form_fields,
    )


# Route for 2nd step of survey
@app.route("/step/2", methods=["GET", "POST"])
@login_required
def step2():
    # Same format as 1st route -- see that route for more specific comments
    user_id = session["user_id"]
    if request.method == "POST":
        value = request.form.get(form_fields[1])
        if not value:
            value = 0

        try:
            db.execute(
                "UPDATE survey_results SET STATE_COLUMN=? where user_id=?",
                value,
                user_id,
            )
        except Exception as e:
            flash("500: AN ERROR OCCURED")
            return redirect("/step/2")

        return redirect("/step/3")

    return render_template(
        "step_2.html",
        region_values=region_values,
        state_values=state_values,
        form_fields=form_fields,
    )


# Route for 3rd step of survey
@app.route("/step/3", methods=["GET", "POST"])
@login_required
def step3():
    # Same format as 1st route -- see that route for more specific comments
    user_id = session["user_id"]
    if request.method == "POST":
        value = request.form.get(form_fields[2])
        if not value:
            value = 0

        try:
            db.execute(
                "UPDATE survey_results SET SIZE_COLUMN=? where user_id=?",
                value,
                user_id,
            )
        except Exception as e:
            flash("500: AN ERROR OCCURED")
            return redirect("/step/3")

        return redirect("/step/4")

    return render_template(
        "step_3.html",
        region_values=region_values,
        state_values=state_values,
        form_fields=form_fields,
    )


# Route for 4th step of survey
@app.route("/step/4", methods=["GET", "POST"])
@login_required
def step4():
    # Same format as 1st route -- see that route for more specific comments
    user_id = session["user_id"]
    if request.method == "POST":
        value = request.form.get(form_fields[3])
        if not value:
            value = 0

        try:
            db.execute(
                "UPDATE survey_results SET CONTROL_COLUMN=? where user_id=?",
                value,
                user_id,
            )
        except Exception as e:
            flash("500: AN ERROR OCCURED")
            return redirect("/step/4")

        return redirect("/step/5")

    return render_template(
        "step_4.html",
        region_values=region_values,
        state_values=state_values,
        form_fields=form_fields,
    )


# Route for 5th step of survey
@app.route("/step/5", methods=["GET", "POST"])
@login_required
def step5():
    # Same format as 1st route -- see that route for more specific comments
    user_id = session["user_id"]
    if request.method == "POST":
        value = request.form.get(form_fields[4])
        if not value:
            value = 0

        try:
            db.execute(
                "UPDATE survey_results SET GRADUATION_RATE_COLUMN=? where user_id=?",
                value,
                user_id,
            )
        except Exception as e:
            flash("500: AN ERROR OCCURED")
            return redirect("/step/5")

        return redirect("/step/6")

    return render_template(
        "step_5.html",
        region_values=region_values,
        state_values=state_values,
        form_fields=form_fields,
    )


# Route for 6th step of survey
@app.route("/step/6", methods=["GET", "POST"])
@login_required
def step6():
    # Same format as 1st route -- see that route for more specific comments
    user_id = session["user_id"]
    if request.method == "POST":
        value = request.form.get(form_fields[5])
        if not value:
            value = 0

        try:
            db.execute(
                "UPDATE survey_results SET ADMISSIONS_COLUMN=? where user_id=?",
                value,
                user_id,
            )
        except Exception as e:
            flash("500: AN ERROR OCCURED")
            return redirect("/step/6")

        return redirect("/step/7")

    return render_template(
        "step_6.html",
        region_values=region_values,
        state_values=state_values,
        form_fields=form_fields,
    )


# Route for 7th step of survey
@app.route("/step/7", methods=["GET", "POST"])
@login_required
def step7():
    # Same format as 1st route -- see that route for more specific comments
    user_id = session["user_id"]
    if request.method == "POST":
        value = request.form.get(form_fields[6])
        if not value:
            value = 0

        try:
            db.execute(
                "UPDATE survey_results SET URBANIZATION_COLUMN=? where user_id=?",
                value,
                user_id,
            )
        except Exception as e:
            flash("500: AN ERROR OCCURED")
            return redirect("/step/7")

        return redirect("/step/8")

    return render_template(
        "step_7.html",
        region_values=region_values,
        state_values=state_values,
        form_fields=form_fields,
    )


# Route for 8th step of survey
@app.route("/step/8", methods=["GET", "POST"])
@login_required
def step8():
    # Same format as 1st route -- see that route for more specific comments
    user_id = session["user_id"]
    if request.method == "POST":
        value = request.form.get(form_fields[7])
        if not value:
            value = 0

        try:
            db.execute(
                "UPDATE survey_results SET NET_PRICE_COLUMN=? where user_id=?",
                value,
                user_id,
            )
        except Exception as e:
            flash("500: AN ERROR OCCURED")
            return redirect("/step/8")

        try:
            db.execute("UPDATE users SET survey_completed = 1 WHERE id = ?", user_id)
        except Exception as e:
            flash("500: AN ERROR OCCURED")

        # Send user back to main/home route -- this is where their results will be displayed
        return redirect("/")

    return render_template(
        "step_8.html",
        region_values=region_values,
        state_values=state_values,
        form_fields=form_fields,
    )


# Route to log in
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Get username and password
        username = request.form.get("username")
        password = request.form.get("password")
        # Ensure username was submitted
        if not username or not password:
            flash("403: MUST PROVIDE USERNAME AND PASSWORD")
            return render_template("login.html")

        # Query database for username
        try:
            rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        except Exception as e:
            flash("500: AN ERROR OCCURED")
            return render_template("login.html")

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            flash("403: INVALID USERNAME AND/OR PASSWORD")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


# Route to log out
@app.route("/logout")
@login_required
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to main landing page
    return redirect("/")


# Route to register
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Forget any user_id
    session.clear()

    if request.method == "POST":
        # Get username, password, and confirmation from form
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure username was submitted
        if not username:
            flash("400: MUST PROVIDE USERNAME")
            return render_template("register.html")
        # Ensure username is unique (ie. does not exist)
        elif len(db.execute("SELECT * FROM users WHERE username = ?", username)) != 0:
            flash("400: THIS USERNAME ALREADY EXISTS")
            return render_template("register.html")

        # Ensure password was submitted
        elif not password:
            flash("400: MUST PROVIDE PASSWORD")
            return render_template("register.html")
        # Ensure confirmation of password was submitted
        elif not confirmation:
            flash("400: MUST CONFIRM PASSWORD")
            return render_template("register.html")
        # Ensure password and confirmation match:
        elif password != confirmation:
            flash("400: PASSWORDS DO NOT MATCH")
            return render_template("register.html")

        # Ensure password meets strength requirements
        password = request.form.get("password")
        if not is_strong_password(password):
            flash(
                "Password must be at least 8 characters long and contain one or more numbers/special characters"
            )
            return render_template("register.html")

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Insert the new user into the users table and get the user's id
        try:
            user_id = db.execute(
                "INSERT INTO users (username, hash) VALUES (?, ?)",
                username,
                hashed_password,
            )
        except Exception as e:
            flash("500: AN ERROR OCCURED")
            return render_template("register.html")

        # After registering new user in database in users table, set up a row in the survey_results table w/ default values for the user
        db.execute(
            f"INSERT INTO survey_results (user_id, REGION_COLUMN, STATE_COLUMN, SIZE_COLUMN, CONTROL_COLUMN, GRADUATION_RATE_COLUMN, ADMISSIONS_COLUMN, URBANIZATION_COLUMN, NET_PRICE_COLUMN) VALUES ({user_id}, 'Default Region', 'Default State', 'Default Size', 'Default Control', 0, 'Default Admissions', 'Default Urbanization', 0)"
        )

        # Log user in
        session["user_id"] = user_id

        # Flash confirmation message
        flash("Registered!")
        # Redirect to index
        return render_template("waiting.html")

    return render_template("register.html")


# Route for settings page
@app.route("/settings")
@login_required
def settings():
    return render_template("settings.html")


# Route to change username
@app.route("/settings/change-username", methods=["POST"])
@login_required
def settings_change_username():
    # Get current user's id from the session
    user_id = session["user_id"]

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Get current, new, and confirmation username, as well as password, from form
        current = request.form.get("current-username")
        password = request.form.get("password")
        new = request.form.get("new-username")
        confirmation = request.form.get("confirm-username")

        # Ensure current username was submitted
        if not current:
            flash("400: MUST PROVIDE CURRENT USERNAME")
            return render_template("settings.html")
        # Ensure username is correct
        if (
            current
            != db.execute("SELECT username FROM users WHERE id = ?", user_id)[0][
                "username"
            ]
        ):
            flash("403: INCORRECT USERNAME")
            return render_template("settings.html")

        # Query database for user password
        hashed_password = db.execute("SELECT hash FROM users WHERE id = ?", user_id)[0][
            "hash"
        ]

        # Ensure password was submitted
        if not password:
            flash("400: MUST PROVIDE PASSWORD")
            return render_template("settings.html")
        # Ensure password is correct
        if not check_password_hash(hashed_password, password):
            flash("403: INCORRECT PASSWORD")
            return render_template("settings.html")

        # Ensure new username was submitted
        elif not new:
            flash("400: MUST PROVIDE NEW USERNAME")
            return render_template("settings.html")
        # Ensure confirmation of new username was submitted
        elif not confirmation:
            flash("400: MUST CONFIRM NEW USERNAME")
            return render_template("settings.html")
        # Ensure new username is unique
        elif new in db.execute("SELECT username FROM users"):
            flash("400: MUST USE UNIQUE NEW USERNAME")
            return render_template("settings.html")
        # Ensure new username and confirmation match:
        elif new != confirmation:
            flash("400: USERNAMES DO NOT MATCH")
            return render_template("settings.html")

        # Try to update user's username
        try:
            db.execute("UPDATE users SET username = ? WHERE id = ?", new, user_id)
        except:
            flash("500: AN ERROR OCCURED")
            return render_template("settings.html")

        # Flash confirmation message
        flash("Username changed!")
        return redirect("/")


# Route to change password
@app.route("/settings/change-password", methods=["POST"])
@login_required
def settings_change_password():
    # Get current user's id from the session
    user_id = session["user_id"]

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Get username + current, new, and confirmation password from form
        username = request.form.get("username")
        current = request.form.get("current-password")
        new = request.form.get("new-password")
        confirmation = request.form.get("confirm-password")

        # Ensure username was submitted
        if not username:
            flash("400: MUST PROVIDE USERNAME")
            return render_template("settings.html")
        # Ensure username is correct
        if (
            username
            != db.execute("SELECT username FROM users WHERE id = ?", user_id)[0][
                "username"
            ]
        ):
            flash("403: INCORRECT USERNAME")
            return render_template("settings.html")

        # Query database for user password
        hashed_password = db.execute("SELECT hash FROM users WHERE id = ?", user_id)[0][
            "hash"
        ]

        # Ensure current password was submitted
        if not current:
            flash("400: MUST PROVIDE CURRENT PASSWORD")
            return render_template("settings.html")
        # Ensure current password is correct
        if not check_password_hash(hashed_password, current):
            flash("403: INCORRECT PASSWORD")
            return render_template("settings.html")

        # Ensure new password was submitted
        elif not new:
            flash("400: MUST PROVIDE NEW PASSWORD")
            return render_template("settings.html")
        # Ensure confirmation of new password was submitted
        elif not confirmation:
            flash("400: MUST CONFIRM NEW PASSWORD")
            return render_template("settings.html")
        # Ensure new password is different
        elif current == new:
            flash("400: NEW PASSWORD MUST BE DIFFERENT")
            return render_template("settings.html")
        # Ensure new password and confirmation match:
        elif new != confirmation:
            flash("400: PASSWORDS DO NOT MATCH")
            return render_template("settings.html")

        # Check that new passsword meets strength requirements
        if not is_strong_password(new):
            flash(
                "Password must be at least 8 characters long and contain one or more numbers/special characters"
            )
            return render_template("settings.html")

        # Hash the new password
        hashed_new = generate_password_hash(new)

        # Try to update user's password
        try:
            db.execute("UPDATE users SET hash = ? WHERE id = ?", hashed_new, user_id)
        except:
            flash("500: AN ERROR OCCURED")
            return render_template("settings.html")

        # Flash confirmation message
        flash("Password changed!")
        return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
