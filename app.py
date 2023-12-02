from flask import Flask, render_template, request, redirect, url_for, session
from match import load_data, clean_data, calculate_total_match

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# CSV Columns
CSV_PATH = "college_data.csv"
SIZE_COLUMN = 'HD2021.Institution size category'
INSTITUTION_CATEGORY_COLUMN = 'HD2021.Institutional category'
REGION_COLUMN = 'HD2021.Bureau of Economic Analysis (BEA) regions'
STATE_COLUMN = 'HD2021.FIPS state code'
CONTROL_COLUMN = 'HD2021.Control of institution'
GRADUATION_RATE_COLUMN = 'DRVGR2021_RV.Graduation rate, total cohort'
ADMISSIONS_COLUMN = 'DRVADM2021_RV.Percent admitted - total'
URBANIZATION_COLUMN = 'HD2021.Degree of urbanization (Urban-centric locale)'
NET_PRICE_PUBLIC_COLUMN = 'SFA2021_RV.Average net price-students awarded grant or scholarship aid, 2020-21 Public'
NET_PRICE_PRIVATE_COLUMN = 'SFA2021_RV.Average net price-students awarded grant or scholarship aid, 2020-21 Private'
NET_PRICE_COLUMN = 'Combined Net Price'

# Step Questions
questions = [
    'Select Region',
    'Select State',
    'Select Size',
    'Select Control',
    'Enter Graduation Rate',
    'Enter Admissions Rate',
    'Select Urbanization',
    'Enter Net Price'
]

# Step Form Fields
form_fields = [
    REGION_COLUMN, STATE_COLUMN, SIZE_COLUMN, CONTROL_COLUMN,
    GRADUATION_RATE_COLUMN, ADMISSIONS_COLUMN, URBANIZATION_COLUMN, NET_PRICE_COLUMN
]

# Define weights for each criterion
weights = {
    REGION_COLUMN: 1,
    STATE_COLUMN: 1,
    SIZE_COLUMN: 1,
    CONTROL_COLUMN: 1,
    GRADUATION_RATE_COLUMN: 1,
    ADMISSIONS_COLUMN: 1,
    URBANIZATION_COLUMN: 1,
    NET_PRICE_COLUMN: 1,
}

# Load and clean data
df = load_data("college_data.csv")
df = clean_data(df)
region_values = df[REGION_COLUMN].unique().tolist()
state_values = df[STATE_COLUMN].unique().tolist()

@app.route('/')
def index():
    return render_template('survey.html')

@app.route('/restart', methods=['POST'])
def restart():
    # Clear specific form-related session variables
    for field in form_fields:
        session.pop(field, None)

    # Redirect to the beginning of the form
    return redirect(url_for('index'))


@app.route('/step/<int:step>', methods=['GET', 'POST'])
# Create pages for every question
def step(step):
    if request.method == 'POST':
        for field in form_fields:
            value = request.form.get(field, '').strip()
            session[field] = value if value else session.get(field, 0)
            print(value)

        if step < len(questions):
            # Redirect to the next step
            return redirect(url_for('step', step=step + 1))
        elif step == len(questions):
            # If on the last step, redirect to the results page
            return redirect(url_for('results'))

    # Render the template for the current step
    question = questions[step - 1]
    return render_template(f'step_{step}.html', question=question, step=step, region_values=region_values, state_values=state_values, form_fields=form_fields)

@app.route('/results')
def results():
    user_preferences = {field: session.get(field, 0) for field in form_fields}
    total_score = calculate_total_match(df, weights, user_preferences)
    df['Percent_Match'] = total_score
    sorted_data = df.sort_values(by='Percent_Match', ascending=False)
    top_ten_data = sorted_data.head(10)
    results_html = top_ten_data[['institution name', 'Percent_Match']].to_html(index=False)
    return render_template('results.html', results_html=results_html, region_values=region_values, state_values=state_values, form_fields=form_fields, questions=questions)

if __name__ == '__main__':
    app.run(debug=True)
