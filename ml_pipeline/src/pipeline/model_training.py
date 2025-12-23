from sklearn.linear_model import LogisticRegression

def train_logistic_model(df, target='churn'):
    """
    Train Logistic Regression on preprocessed DataFrame.
    Returns the trained model as artifact.
    """
    X = df.drop(columns=[target])
    y = df[target]

    # Fine-tuned parameters from GridSearch (see ML1_Model_fine-tuning.ipynb in experiments folder)
    model = LogisticRegression(
        C=1,
        penalty='l1',
        solver='liblinear',
        class_weight='balanced',
        max_iter=3000,
        random_state=42
    )

    model.fit(X, y)
    return model
