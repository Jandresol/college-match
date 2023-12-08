import pandas as pd

# Constants
CSV_PATH = "college_data.csv"
ENROLLMENT_COLUMN = 'DRVEF2021.Full-time undergraduate enrollment'
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

# Read the csv file
def load_data(csv_path):
    return pd.read_csv(csv_path)

# Drop schools without data, and that are not accreditaed 4-year schools
def clean_data(df):
    df = df.dropna(subset=[ENROLLMENT_COLUMN, INSTITUTION_CATEGORY_COLUMN, REGION_COLUMN, STATE_COLUMN, GRADUATION_RATE_COLUMN])
    df = df[(df[REGION_COLUMN] != 'U.S. Service schools') & (~df[REGION_COLUMN].isna())]
    df = df[df[INSTITUTION_CATEGORY_COLUMN] == 'Degree-granting, primarily baccalaureate or above']
    df['Combined Net Price'] = df[NET_PRICE_PUBLIC_COLUMN].fillna(0) + df[NET_PRICE_PRIVATE_COLUMN].fillna(0)
    return df

def string_match(value, user_preference, weight):
    try:
        # Convert the value to a string to handle different data types
        str_value = str(value)
        return 100 * weight if user_preference in str_value else 0
    except Exception as e:
        return 0

def calculate_graduation_match(column, weight, user_preference):
    try:
        # Convert graduation rate column to float
        column = column.astype(float)
        user_preference = float(user_preference)

        # Handle the case where user_preference is 0 to avoid division by zero
        denominator = max(1, user_preference)
        
        # Calculate match scores based on the provided equation
        match_scores = column.apply(lambda x: max(0, 100 - 100 * abs(x - user_preference) / denominator))
        normalized_scores = ((match_scores - match_scores.min()) / max(1, (match_scores.max() - match_scores.min()))) * 100

        # Return the total match score, multiplied by the weight
        return normalized_scores * weight
    except ValueError:
        return 0

def calculate_admissions_match(column, weight, user_preference):
    try:
        # Convert graduation rate column to float
        column = column.astype(float)
        user_preference = float(user_preference)

        # Create a match score where it classifies it as a 100% match if it falls in the range
        match_score = column.apply(lambda x: 100 if user_preference - 10 <= x < user_preference + 10 else 0)

        # Return the binary match scores, multiplied by the weight
        return match_score * weight
    except ValueError:
        return 0


def calculate_enrollment_match(column, weight, user_preference):
    try:
        # Convert graduation rate column to float
        column = column.astype(float)
        user_preference = float(user_preference)

        # Handle the case where user_preference is 0 to avoid division by zero
        denominator = max(1, user_preference)
        
        # Calculate match scores based on the provided equation
        match_scores = 100 - 20 * abs(column - user_preference) / denominator
        normalized_scores = ((match_scores - match_scores.min()) / max(1, (match_scores.max() - match_scores.min()))) * 100

        # Return the total match score, multiplied by the weight
        return normalized_scores * weight
    except ValueError:
        return 0

def calculate_price_match(column, weight, user_preference):
    try:
        # Convert the column to float
        column = column.astype(float)
        user_preference = float(user_preference)

        # Handle the case where user_preference is 0 to avoid division by zero
        denominator = max(1, user_preference)
        
        # Calculate match scores based on the provided equation
        match_scores = 100 - 20 * abs(column - user_preference) / denominator
        normalized_scores = ((match_scores - match_scores.min()) / max(1, (match_scores.max() - match_scores.min()))) * 100

        # Return the total match score, multiplied by the weight
        return normalized_scores * weight
    except ValueError:
        return 0

def calculate_sat_match(df, weight, user_preference):
    # Linear algorithm to determine sat reading match score
    sat_rw_match = df[SAT_READING_COLUMN].dropna().astype(float).apply(lambda x: max(0, 100 - abs(x - user_preference)))

    # Linear algorithm to determine sat math match score
    sat_math_match = df[SAT_MATH_COLUMN].dropna().astype(float).apply(lambda x: max(0, 100 - abs(x - user_preference)))

    # Combine scores with weights
    sat_match = (sat_rw_match + sat_math_match) / 2 
    return sat_match * weight / 2

def calculate_act_match(df, weight, user_preference):
    # Linear algorithm to determine act match score
    act_match = df[ACT_COLUMN].dropna().astype(float).apply(lambda x: max(0, 100 - abs(x - user_preference)))
    return act_match * weight

# Calculate total match
def calculate_total_match(df, weights, preferences):
    score_columns = pd.DataFrame()
    for column, weight in weights.items():
        if column == ENROLLMENT_COLUMN:
            score_columns[column] = calculate_enrollment_match(df[column], weight, preferences[column])
        elif column == SAT_READING_COLUMN or column == SAT_MATH_COLUMN:
            score_columns[column] = calculate_sat_match(df, weight, preferences[column])
        elif column == ACT_COLUMN:
            score_columns[column] = calculate_act_match(df, weight, preferences[column])
        elif column == GRADUATION_RATE_COLUMN:
            score_columns[column] = calculate_graduation_match(df[column], weight, preferences[column])
        elif column == ADMISSIONS_COLUMN:
            score_columns[column] = calculate_admissions_match(df[column], weight, preferences[column])
        elif column == NET_PRICE_COLUMN: 
            score_columns[column] = calculate_price_match(df[NET_PRICE_COLUMN], weight, preferences[column])
        else:
            score_columns[column] = df[column].apply(lambda x: string_match(x, preferences[column], weight))

    total_weight = score_columns.sum(axis=1)
    total_score = total_weight / total_weight.max() * 100
    return total_score

def main():
    # Load data
    df = load_data(CSV_PATH)

    # Clean data
    df = clean_data(df)

    # CHANGE USER INPUT HERE !!
    user_preferences = {
        REGION_COLUMN: '',
        STATE_COLUMN: '',
        ENROLLMENT_COLUMN: 0,
        SAT_READING_COLUMN: 0,
        SAT_MATH_COLUMN: 0,
        ACT_COLUMN: 0,
        CONTROL_COLUMN: '',
        GRADUATION_RATE_COLUMN: 0,
        ADMISSIONS_COLUMN: 0,
        URBANIZATION_COLUMN: '',
        NET_PRICE_COLUMN: 0
        
    }

    # Define weights for each criterion
    weights = {
        REGION_COLUMN: 1,
        STATE_COLUMN: 1,
        ENROLLMENT_COLUMN:1,
        SAT_READING_COLUMN: 1,
        SAT_MATH_COLUMN: 1,
        ACT_COLUMN: 1,
        CONTROL_COLUMN: 1,
        GRADUATION_RATE_COLUMN: 1,
        ADMISSIONS_COLUMN: 1,
        URBANIZATION_COLUMN: 1,
        NET_PRICE_COLUMN: 1
    }

    # Calculate scores for each criterion in the DataFrame
    total_score = calculate_total_match(df, weights, user_preferences)

    # Add scores to DataFrame
    df['Percent_Match'] = total_score

    # Display the institutions sorted by match score in the DataFrame
    sorted_data = df.sort_values(by='Percent_Match', ascending=False)
    print(sorted_data[['institution name', 'Percent_Match']])

if __name__ == "__main__":
    main()
