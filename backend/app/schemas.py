from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional, Union
from uuid import UUID
from datetime import datetime


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
    customer_id: str
    senior_citizen: bool  
    partner: bool 
    dependents: bool  
    internet_service: Literal['DSL', 'Fiber optic']  
    online_security: bool
    tech_support: bool
    contract: Literal['One year', 'Two year'] 
    paperless_billing: bool  
    payment_method: Literal['Electronic check', 'Mailed check', 'Bank transfer']  
    monthly_charges: float  # will be scaled
    total_charges: float  # will be scaled

class PredictByIdRequest(BaseModel):
    # Mode 1: API fetch customer infos by ID depuis table new_customers)
    customer_id: str

PredictInput = Union[PredictByIdRequest, PredictRequest]

class PredictResponse(BaseModel):
    """
    Docstring for PredictResponse
    This schema defines the output of the customer churn prediction.
    Attributes:
        churn_probability (float): The probability of customer churn.
    """
    prediction_id: int
    token: UUID
    customer_id: str
    churn_probability: float
    prediction: int  # 0/1

class FeedbackRequest(BaseModel):
    token: UUID
    answer: Literal["YES", "NO"]
    feedback_label: Literal[0, 1]
    source: str = Field(default="email")

class FeedbackResponse(BaseModel):
    status: str
    feedback_count: int
    retrain_triggered: bool

class RetrainRequest(BaseModel):
    reason: Literal["feedback", "drift"]


class CustomerDB(BaseModel):
    """
    Schema representing a row in the `customers` table.
    All fields except `customer_id` are optional to allow partial CSV rows.
    """
    customer_id: Optional[str] = None
    gender: Optional[str] = None
    senior_citizen: Optional[bool] = None
    partner: Optional[bool] = None
    dependents: Optional[bool] = None
    tenure: Optional[int] = None

    phone_service: Optional[bool] = None
    multiple_lines: Optional[str] = None

    internet_service: Optional[str] = None
    online_security: Optional[str] = None
    online_backup: Optional[str] = None
    device_protection: Optional[str] = None
    tech_support: Optional[str] = None
    streaming_tv: Optional[str] = None
    streaming_movies: Optional[str] = None

    contract: Optional[str] = None
    paperless_billing: Optional[bool] = None
    payment_method: Optional[str] = None

    monthly_charges: Optional[float] = None
    total_charges: Optional[float] = None

    churn: Optional[bool] = None
    status: Optional[str] = None
    notified: Optional[bool] = None
    updated_at: Optional[datetime] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None

