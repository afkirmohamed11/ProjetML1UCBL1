import pandas as pd
from read_data import read_postgres_table
from dotenv import load_dotenv
load_dotenv()


def preprocess_data() -> pd.DataFrame:
    """
    Preprocesses the input DataFrame by handling missing values and encoding categorical variables.

    Parameters:
        df (pd.DataFrame): Input DataFrame to preprocess
    Returns:
        pd.DataFrame: Preprocessed DataFrame   
    """

    df = read_postgres_table()
    df = df.drop_duplicates()


    return df

# Example usage
# print(preprocess_data())