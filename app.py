from flask import Flask, render_template, request, redirect, url_for, session
from match import load_data, clean_data, calculate_total_match
from constants import REGION_COLUMN, STATE_COLUMN, questions, form_fields, weights

app = Flask(__name__)
app.secret_key = 'your_secret_key'

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
    
    # Pass top_ten_data to the template
    return render_template('results.html', results_html=results_html, top_ten_data=top_ten_data)

if __name__ == '__main__':
    app.run(debug=True)
