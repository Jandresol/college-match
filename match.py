import pandas as pd

# Load the CSV data
csv_path = "college_data.csv"
df = pd.read_csv(csv_path)

# User preferences (example values, replace with user input)
user_preferences = {
    'BEA Region': 'New England (CT, ME, MA, NH, RI, VT)',
    'State': 'Massachussets',
    'Enrollment Size': 8000,
    'SAT Reading and Writing': 800,
    'SAT Math': 800
}

# Filter out schools with NaN values in 'DRVEF2021.Full-time undergraduate enrollment'
df = df.dropna(subset=['DRVEF2021.Full-time undergraduate enrollment'])

# Filter rows where 'HD2021.Institutional category' matches the specified value
df = df[df['HD2021.Institutional category'] == 'Degree-granting, primarily baccalaureate or above']

# Define a function to calculate matching score for each criterion
def calculate_score(value, user_preference, weight):
    # Adjusted weighting algorithm to assign scores based on preferences
    if user_preference == value:
        return 100 * weight
    else:
        # Adjusted weighting algorithm for enrollment size using a linear approach
        if user_preference == 'Enrollment Size':
            try:
                value = float(value)
            except ValueError:
                return 0  # Assign a score of 0 for non-numeric values
            
            # Calculate enrollment score using a linear approach
            enrollment_score = max(0, 100 - 10 * abs(value - user_preferences['Enrollment Size']) / user_preferences['Enrollment Size'])
            return enrollment_score * weight
        elif user_preference == 'SAT Score':
            try:
                value = float(value)
            except ValueError:
                return 0  # Assign a score of 0 for non-numeric values
            
            # Calculate SAT score using a linear approach
            sat_score = max(0, 100 - abs(value - user_preferences['SAT Reading and Writing']) - abs(value - user_preferences['SAT Math']))
            return sat_score * weight
        else:
            return 0  # For other preferences, assign a score of 0

# Calculate scores for each criterion in the DataFrame
df['BEA_Region_Score'] = df['HD2021.Bureau of Economic Analysis (BEA) regions'].apply(lambda x: calculate_score(x, user_preferences['BEA Region'], 1))
df['State_Score'] = df['HD2021.FIPS state code'].apply(lambda x: calculate_score(x, user_preferences['State'], 1))
df['Enrollment_Score'] = df['DRVEF2021.Full-time undergraduate enrollment'].apply(lambda x: calculate_score(x, 'Enrollment Size', 1))
df['SAT_Score'] = df[['ADM2021_RV.SAT Evidence-Based Reading and Writing 75th percentile score', 'ADM2021_RV.SAT Math 75th percentile score']].mean(axis=1).apply(lambda x: calculate_score(x, 'SAT Score', 1))

# Calculate the total score for the DataFrame
total_weight = df[['BEA_Region_Score', 'State_Score', 'Enrollment_Score', 'SAT_Score']].sum(axis=1)
total_score = total_weight / total_weight.max() * 100
df['Percent_Match'] = total_score

# Display the institutions sorted by match score in the DataFrame
sorted_data = df.sort_values(by='Percent_Match', ascending=False)
print(sorted_data[['institution name', 'Percent_Match']])
