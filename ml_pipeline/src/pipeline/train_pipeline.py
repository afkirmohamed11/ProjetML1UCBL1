from build_pipeline import build_pipeline
# from utils.data_loader import read_postgres_table

# def train_pipeline(target="churn"):
#     df = read_postgres_table()
#     X = df.drop(columns=[target])
#     y = df[target]

#     pipeline = build_pipeline()
#     pipeline.fit(X, y)

#     return pipeline

def train_pipeline(X,y, target="churn"):
  

    pipeline = build_pipeline()
    pipeline.fit(X, y)

    return pipeline

