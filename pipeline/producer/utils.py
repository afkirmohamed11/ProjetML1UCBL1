import random
import string
import time
from datetime import datetime
from faker import Faker


fake = Faker()

# Kafka optional imports
# from kafka import KafkaProducer
# import json

# Utility to create customer_id like xxxx-YYYYY
def generate_customer_id():
    x_part = ''.join(random.choices(string.digits, k=4))
    y_part = ''.join(random.choices(string.ascii_uppercase, k=5))
    return f"{x_part}-{y_part}"

# Utility to generate random monthly charges
def generate_monthly_charges():
    return round(random.uniform(20, 150), 2)

# Utility to generate total charges based on tenure
def generate_total_charges(monthly_charges, tenure):
    # Adding some variation
    return round(monthly_charges * tenure * random.uniform(0.9, 1.1), 2)

# Random selection helpers
def random_bool(p=0.5):
    return random.random() < p

def random_choice_weighted(choices):
    total = sum(weight for _, weight in choices)
    r = random.uniform(0, total)
    upto = 0
    for val, weight in choices:
        if upto + weight >= r:
            return val
        upto += weight
    assert False, "Shouldn't reach here"

# Customer generator
def generate_customer():
    tenure = random.randint(0, 72)  # 0-6 years

    monthly_charges = generate_monthly_charges()
    total_charges = generate_total_charges(monthly_charges, tenure)

    customer = {
        "customer_id": generate_customer_id(),
        "gender": random.choice(["Male", "Female"]),
        "senior_citizen": random_bool(0.2),
        "partner": random_bool(0.5),
        "dependents": random_bool(0.4),
        "tenure": tenure,
        "phone_service": random_bool(0.9),
        "multiple_lines": random_choice_weighted([("Yes",0.3), ("No",0.6), ("No phone service",0.1)]),
        "internet_service": random_choice_weighted([("DSL",0.4), ("Fiber optic",0.5), ("None",0.1)]),
        "online_security": random_choice_weighted([("Yes",0.3), ("No",0.6), ("No internet service",0.1)]),
        "online_backup": random_choice_weighted([("Yes",0.3), ("No",0.6), ("No internet service",0.1)]),
        "device_protection": random_choice_weighted([("Yes",0.3), ("No",0.6), ("No internet service",0.1)]),
        "tech_support": random_choice_weighted([("Yes",0.3), ("No",0.6), ("No internet service",0.1)]),
        "streaming_tv": random_choice_weighted([("Yes",0.4), ("No",0.5), ("No internet service",0.1)]),
        "streaming_movies": random_choice_weighted([("Yes",0.4), ("No",0.5), ("No internet service",0.1)]),
        "contract": random_choice_weighted([("Month-to-month",0.5), ("One year",0.3), ("Two year",0.2)]),
        "paperless_billing": random_bool(0.7),
        "payment_method": random_choice_weighted([("Electronic check",0.4), ("Mailed check",0.2), ("Bank transfer",0.2), ("Credit card",0.2)]),
        "monthly_charges": monthly_charges,
        "total_charges": total_charges,
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.email()
    }
    return customer
