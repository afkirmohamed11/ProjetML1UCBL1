from pydantic import BaseModel

class PredictRequest(BaseModel):
    pass
    # TODO: Define the input features for the prediction model
    # feature_1: float
    # feature_n: float
    


class PredictResponse(BaseModel):
    churn_probability: float
