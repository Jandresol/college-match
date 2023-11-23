import pandas as pd

# Load the CSV data
csv_path = "college_data.csv"
df = pd.read_csv(csv_path)

#column names
columns = {
    'Region': 'HD2021.Bureau of Economic Analysis (BEA) regions',
    'State': 'HD2021.FIPS state code',
    'Enrollment': 'DRVEF2021.Full-time undergraduate enrollment',
    'SAT Reading and Writing': 'ADM2021_RV.SAT Evidence-Based Reading and Writing 75th percentile score',  
    'SAT Math': 'ADM2021_RV.SAT Math 75th percentile score'
}

# User preferences (example values, replace with user input)
user_preferences = {
    'Region': 'New England (CT, ME, MA, NH, RI, VT)',
    'State': 'Massachussets',
    'Enrollment': 8000,
    'SAT Reading and Writing': 800,
    'SAT Math': 800
}

# Filter out schools with NaN values in 'DRVEF2021.Full-time undergraduate enrollment'
df = df.dropna(subset=['DRVEF2021.Full-time undergraduate enrollment'])

# Filter rows where 'HD2021.Institutional category' matches the specified value
df = df[df['HD2021.Institutional category'] == 'Degree-granting, primarily baccalaureate or above']

# Define three separate functions for each preference
def string_match(value, user_preference, weight):
    return 100 * weight if user_preference == value else 0

def score_enrollment_size(value, weight):
    try:
        value = float(value)
    except ValueError:
        return 0

    enrollment_score = max(0, 100 - 10 * abs(value - user_preferences['Enrollment']) / user_preferences['Enrollment'])
    return enrollment_score * weight

def score_sat(value, weight):
    try:
        value = float(value)
    except ValueError:
        return 0

    sat_score = max(0, 100 - abs(value - user_preferences['SAT Reading and Writing']) - abs(value - user_preferences['SAT Math']))
    return sat_score * weight

# Calculate scores for each criterion in the DataFrame
df['BEA_Region_Score'] = df[columns['Region']].apply(lambda x: string_match(x, user_preferences['Region'], 1))
df['State_Score'] = df[columns['State']].apply(lambda x: string_match(x, user_preferences['State'], 1))
df['Enrollment_Score'] = df[columns['Enrollment']].apply(lambda x: score_enrollment_size(x, 1))
df['SAT_Score'] = df[['ADM2021_RV.SAT Evidence-Based Reading and Writing 75th percentile score', 'ADM2021_RV.SAT Math 75th percentile score']].mean(axis=1).apply(lambda x: score_sat(x, 1))

# Calculate the total score for the DataFrame
total_weight = df[['BEA_Region_Score', 'State_Score', 'Enrollment_Score', 'SAT_Score']].sum(axis=1)
total_score = total_weight / total_weight.max() * 100
df['Percent_Match'] = total_score

# Display the institutions sorted by match score in the DataFrame
sorted_data = df.sort_values(by='Percent_Match', ascending=False)
print(sorted_data[['institution name', 'Percent_Match']])
