from pydantic import BaseModel

class PredictRequest(BaseModel):
    """
    Docstring for PredictRequest
    This schema defines the expected input for predicting customer churn.
    It includes various customer attributes that will be used in the prediction model.
    Attributes:
        senior_citizen (bool): Indicates if the customer is a senior citizen.
        partner (bool): Indicates if the customer has a partner.
        dependents (bool): Indicates if the customer has dependents.
        internet_service (str): Type of internet service (e.g., DSL, Fiber optic).
        online_security (bool): Indicates if the customer has online security.
        tech_support (bool): Indicates if the customer has tech support.
        contract (str): Type of contract (e.g., One year, Two year).
        paperless_billing (bool): Indicates if the customer has paperless billing.
        payment_method (str): Method of payment (e.g., Electronic check, Mailed check, Bank transfer).
        monthly_charges (float): Monthly charges for the customer (will be scaled).
        total_charges (float): Total charges for the customer (will be scaled).
    """    
    senior_citizen: bool  
    partner: bool 
    dependents: bool  
    internet_service: str  # internet_service_DSL, internet_service_Fiber_optic
    online_security: bool
    tech_support: bool
    contract: str  # contract_One_year, contract_Two_year
    paperless_billing: bool  
    payment_method: str  # payment_method_Electronic_check, payment_method_Mailed_check, payment_method_Bank_transfer
    monthly_charges: float  # will be scaled
    total_charges: float  # will be scaled


class PredictResponse(BaseModel):
    """
    Docstring for PredictResponse
    This schema defines the output of the customer churn prediction.
    Attributes:
        churn_probability (float): The probability of customer churn.
    """
    churn_probability: float