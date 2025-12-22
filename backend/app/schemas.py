from pydantic import BaseModel

class PredictRequest(BaseModel):
    # TODO : Define the input features for the prediction request based on the model requirements
    
    # gender: str
    # senior_citizen: bool
    # partner: bool
    # dependents: bool
    # tenure: int

    # phone_service: bool
    # multiple_lines: str

    # internet_service: str
    # online_security: str
    # online_backup: str
    # device_protection: str
    # tech_support: str
    # streaming_tv: str
    # streaming_movies: str

    # contract: str
    # paperless_billing: bool
    # payment_method: str

    # monthly_charges: float
    # total_charges: float

    # TODO
    senior_citizen: int
    partner: int
    dependents: int
    phone_service: int
    multiple_lines: int
    online_security: int
    online_backup: int
    device_protection: int
    tech_support: int
    streaming_tv: int
    streaming_movies: int
    paperless_billing: int
    monthly_charges: int
    total_charges: int
    gender_Male: int
    internet_service_DSL: int
    internet_service_Fiber_optic: int

    contract_One_year: int
    contract_Two_year: int

    payment_method_Electronic_check: int
    payment_method_Mailed_check: int
    payment_method_Bank_transfer: int


class PredictResponse(BaseModel):
    churn_probability: float