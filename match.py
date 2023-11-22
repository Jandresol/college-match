import pandas as pd

# Load the CSV data
csv_path = "college_data.csv"
df = pd.read_csv(csv_path)

# User preferences (example values, replace with user input)
user_preferences = {
    'Institution Size': 'Medium',
    'Tuition and Fees': 20000,
    'Admission Rate': 50,
    'Graduation Rate': 70,
    'State': 'NY'
}

# Normalize user preferences if needed (for example, normalize tuition and fees)
user_preferences['Tuition and Fees'] = user_preferences['Tuition and Fees'] / df['DRVIC2021.Tuition and fees, 2021-22'].max()

# Calculate scores for each criterion
df['Size_Score'] = (df['HD2021.Institution size category'] == user_preferences['Institution Size']).astype(int)
df['Tuition_Score'] = 1 - abs(df['DRVIC2021.Tuition and fees, 2021-22'] - user_preferences['Tuition and Fees'])
df['Admission_Score'] = 1 - abs(df['DRVADM2021_RV.Percent admitted - total'] - user_preferences['Admission Rate'])
df['Graduation_Score'] = 1 - abs(df['DRVGR2021_RV.Graduation rate, total cohort'] - user_preferences['Graduation Rate'])
df['State_Score'] = (df['HD2021.State abbreviation'] == user_preferences['State']).astype(int)

# Calculate the total score
df['Total_Score'] = df[['Size_Score', 'Tuition_Score', 'Admission_Score', 'Graduation_Score', 'State_Score']].sum(axis=1)

# Normalize the total score to a percentage scale
df['Percent_Match'] = (df['Total_Score'] / df['Total_Score'].max()) * 100

# Display the top matching institutions
top_matches = df.sort_values(by='Percent_Match', ascending=True).head(10)
print(top_matches[['institution name', 'Percent_Match']])
