import pandas as pd
from sklearn.preprocessing import StandardScaler
from data_loader import read_postgres_table
from dotenv import load_dotenv
load_dotenv()

# drop duplicates function
def drop_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop_duplicates()

# Fills null values in total_charges with the median
def fill_total_charges_median(df: pd.DataFrame) -> pd.DataFrame:
    median_val = df['total_charges'].median()
    df['total_charges'] = df['total_charges'].fillna(median_val)
    return df

# Converts specific boolean columns to integers (0/1)
def encode_boolean_features(df: pd.DataFrame) -> pd.DataFrame:
    boolean_columns = ['senior_citizen', 'partner', 'dependents', 'phone_service', 'paperless_billing', 'churn']
    for col in boolean_columns:
        if col in df.columns:
            df[col] = df[col].astype(int)
    return df

# Removes the customer_id column from the DataFrame
def drop_customer_id(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop(columns=['customer_id'], errors='ignore')

# Converts service-related categorical columns to binary integers
# These columns have Yes/No/No phone service or No internet service
# Since "No phone/internet service" is redundant (already in phone_service/internet_service), treat as 0

def encode_service_features(df: pd.DataFrame) -> pd.DataFrame:
    service_columns = [
        'multiple_lines', 'online_security', 'online_backup', 
        'device_protection', 'tech_support', 'streaming_tv', 
        'streaming_movies'
    ]
    for col in service_columns:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: 1 if x == 'Yes' else 0)
    return df

# Applies custom one-hot encoding to categorical features
def encode_categorical_features(df: pd.DataFrame) -> pd.DataFrame:
    # Gender
    df['gender_Male'] = (df['gender'] == 'Male').astype(int)
    df['gender_Female'] = (df['gender'] == 'Female').astype(int)
    
    # Internet Service (Excluding 'No')
    df['internet_service_DSL'] = (df['internet_service'] == 'DSL').astype(int)
    df['internet_service_Fiber_optic'] = (df['internet_service'] == 'Fiber optic').astype(int)
    
    # Contract
    df['contract_Month_to_month'] = (df['contract'] == 'Month-to-month').astype(int)
    df['contract_One_year'] = (df['contract'] == 'One year').astype(int)
    df['contract_Two_year'] = (df['contract'] == 'Two year').astype(int)
    
    # Payment Method
    df['payment_method_Electronic_check'] = (df['payment_method'] == 'Electronic check').astype(int)
    df['payment_method_Mailed_check'] = (df['payment_method'] == 'Mailed check').astype(int)
    df['payment_method_Bank_transfer'] = (df['payment_method'] == 'Bank transfer (automatic)').astype(int)
    df['payment_method_Credit_card'] = (df['payment_method'] == 'Credit card (automatic)').astype(int)
    
    return df.drop(columns=['gender', 'internet_service', 'contract', 'payment_method'])

def drop_redundant_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Drops columns that are redundant either due to high correlation or
    can be logically deduced from other one-hot encoded columns.
    """
    columns_to_drop = ['tenure', 'gender_Female', 'contract_Month_to_month', 'payment_method_Credit_card']
    return df.drop(columns=columns_to_drop, errors='ignore')


def scale_numeric_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Scales high-magnitude numeric features.
    """
    numeric_columns = ['monthly_charges', 'total_charges']
    scaler = StandardScaler()
    df[numeric_columns] = scaler.fit_transform(df[numeric_columns])
    return df

def drop_low_impact_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Drops features that have very low correlation with churn or provide minimal predictive value.
    Check experiments/ML1_Model_Building.ipynb for correlation analysis.
    """
    low_impact_cols = [
        "gender_Male", "phone_service", "multiple_lines",
        "streaming_tv", "streaming_movies", "online_backup", "device_protection"
    ]
    return df.drop(columns=low_impact_cols, errors='ignore')


def preprocess_data() -> pd.DataFrame:
    """
    Preprocesses the input DataFrame.

    Parameters:
        df (pd.DataFrame): Input DataFrame to preprocess
    Returns:
        pd.DataFrame: Preprocessed DataFrame   
    """
    df = read_postgres_table()
    df = drop_duplicates(df)
    df = fill_total_charges_median(df)
    df = encode_boolean_features(df)
    df = drop_customer_id(df)
    df = encode_service_features(df)
    df = encode_categorical_features(df)
    df = drop_redundant_columns(df)
    df = scale_numeric_features(df)
    df = drop_low_impact_features(df)
    return df









# Example usage
# df = preprocess_data()
# print(df["total_charges"].max())
# df.to_csv('preprocessed_customers.csv', index=False)