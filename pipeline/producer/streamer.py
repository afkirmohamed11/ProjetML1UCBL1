import json
import time
from kafka import KafkaProducer
from utils import generate_customer
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

EVENT_HUBS_BROKER = os.getenv("EVENT_HUBS_BROKER")
EVENT_HUBS_CONNECTION_STRING = os.getenv("EVENT_HUBS_CONNECTION_STRING")


producer = KafkaProducer(
    bootstrap_servers=EVENT_HUBS_BROKER,
    security_protocol="SASL_SSL",
    sasl_mechanism="PLAIN",
    sasl_plain_username="$ConnectionString",
    sasl_plain_password=EVENT_HUBS_CONNECTION_STRING,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def simulate_customers(interval_sec=3):
    while True:
        new_customer = generate_customer()
        print('new_customer: ' + new_customer['customer_id'])  
        # send to Kafka
        producer.send("new-customers", value=new_customer)
        time.sleep(interval_sec)


if __name__ == "__main__":

    simulate_customers(5)

