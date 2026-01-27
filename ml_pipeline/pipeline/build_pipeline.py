import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.over_sampling import SMOTE

from preprocess import (
    drop_duplicates,
    fill_total_charges_median,
    encode_boolean_features,
    drop_customer_id,
    encode_service_features,
    encode_categorical_features,
    drop_redundant_columns,
    drop_low_impact_features,
)

class PreprocessingTransformer(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.scaler = StandardScaler()
        self.numeric_columns = ['monthly_charges', 'total_charges']

    def fit(self, X, y=None):
        X = self._apply_static_transforms(X.copy())
        self.scaler.fit(X[self.numeric_columns])
        return self

    def transform(self, X):
        X = self._apply_static_transforms(X.copy())
        X[self.numeric_columns] = self.scaler.transform(X[self.numeric_columns])
        return X

    def _apply_static_transforms(self, df: pd.DataFrame) -> pd.DataFrame:
        # df = drop_duplicates(df)
        df = fill_total_charges_median(df)
        df = encode_boolean_features(df)
        df = drop_customer_id(df)
        df = encode_service_features(df)
        df = encode_categorical_features(df)
        df = drop_redundant_columns(df)
        df = drop_low_impact_features(df)
        return df


def build_pipeline():
    
    # Fine-tuned parameters from GridSearch (see ML1_Model_fine-tuning.ipynb in experiments folder)
    model = LogisticRegression(
        C=1,
        l1_ratio=1.0, 
        solver='liblinear',
        class_weight='balanced',
        max_iter=3000,
        random_state=42
    )

    return Pipeline(steps=[
        ("preprocess", PreprocessingTransformer()),
        ("model", model)
    ])





