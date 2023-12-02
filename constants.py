
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
