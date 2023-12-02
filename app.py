from flask import Flask, render_template, request
from match import (
    load_data,
    clean_data,
    calculate_total_match
)

app = Flask(__name__)

# CSV Columns
CSV_PATH = "college_data.csv"
SIZE_COLUMN = 'HD2021.Carnegie Classification 2021: Size and Setting'
INSTITUTION_CATEGORY_COLUMN = 'HD2021.Institutional category'
REGION_COLUMN = 'HD2021.Bureau of Economic Analysis (BEA) regions'
STATE_COLUMN = 'HD2021.FIPS state code'
SAT_READING_COLUMN = 'ADM2021_RV.SAT Evidence-Based Reading and Writing 75th percentile score'
SAT_MATH_COLUMN = 'ADM2021_RV.SAT Math 75th percentile score'
ACT_COLUMN = 'ADM2021_RV.ACT Composite 75th percentile score'
CONTROL_COLUMN = 'HD2021.Control of institution'
GRADUATION_RATE_COLUMN = 'DRVGR2021_RV.Graduation rate, total cohort'
ADMISSIONS_COLUMN = 'DRVADM2021_RV.Percent admitted - total'
URBANIZATION_COLUMN = 'HD2021.Degree of urbanization (Urban-centric locale)'
NET_PRICE_PUBLIC_COLUMN = 'SFA2021_RV.Average net price-students awarded grant or scholarship aid, 2020-21 Public'
NET_PRICE_PRIVATE_COLUMN = 'SFA2021_RV.Average net price-students awarded grant or scholarship aid, 2020-21 Private'
NET_PRICE_COLUMN = 'Combined Net Price'

@app.route('/')
def college_match_form():
    # Load data
    df = load_data(CSV_PATH)
    
    # Clean data
    df = clean_data(df)
    
    # Get unique region values
    region_values = df[REGION_COLUMN].unique().tolist()
    
    # Get unique state values
    state_values = df[STATE_COLUMN].unique().tolist()
    
    # Get unique control values
    control_values = df[CONTROL_COLUMN].unique().tolist()
    
    # Get unique urbanization values
    urban_values = df[URBANIZATION_COLUMN].unique().tolist()

    return render_template('form.html', region_values=region_values, state_values=state_values, control_values=control_values, urban_values=urban_values)

@app.route('/results', methods=['POST'])
def display_results():
    try:
        # Retrieve user input from the form
        user_preferences = {
            REGION_COLUMN: request.form.get('region') or 0,  
            STATE_COLUMN: request.form.get('state') or 0, 
            SIZE_COLUMN: request.form.get('size') or 0,
            SAT_READING_COLUMN: int(request.form.get('sat_reading') or 0),
            SAT_MATH_COLUMN: int(request.form.get('sat_math') or 0),
            ACT_COLUMN: int(request.form.get('act') or 0),
            CONTROL_COLUMN: request.form.get('control') or 0,
            GRADUATION_RATE_COLUMN: int(request.form.get('graduation_rate') or 0),
            ADMISSIONS_COLUMN: int(request.form.get('admissions') or 0),
            URBANIZATION_COLUMN: request.form.get('urbanization') or 0, 
            NET_PRICE_COLUMN: int(request.form.get('net_price') or 0)
        }

        # Load data
        df = load_data(CSV_PATH)

        # Clean data
        df = clean_data(df)

        # Define weights for each criterion
        weights = {
            REGION_COLUMN: 1,
            STATE_COLUMN: 1,
            SIZE_COLUMN: 1,
            SAT_READING_COLUMN: .5,
            SAT_MATH_COLUMN: .5,
            ACT_COLUMN: 1,
            CONTROL_COLUMN: 1,
            GRADUATION_RATE_COLUMN: 1,
            ADMISSIONS_COLUMN: 1,
            URBANIZATION_COLUMN: 1,
            NET_PRICE_COLUMN: 1,
        }

        # Calculate scores for each criterion in the DataFrame
        total_score = calculate_total_match(df, weights, user_preferences)

        # Add scores to DataFrame
        df['Percent_Match'] = total_score

        # Display the institutions sorted by match score in the DataFrame
        sorted_data = df.sort_values(by='Percent_Match', ascending=False)
        results_html = sorted_data[['institution name', 'Percent_Match']].to_html(index=False)

        return render_template('results.html', results_html=results_html)
    except Exception as e:
        return render_template('error.html', error=str(e))

if __name__ == '__main__':
    app.run(debug=True)
