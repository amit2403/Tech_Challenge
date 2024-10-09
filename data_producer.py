import json
import time
import random
from kafka import KafkaProducer

# Initialize Kafka producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def generate_telemetry():
    return {
        "timestamp": int(time.time() * 1000),
        "battery_id": f"BESS_{random.randint(1, 5)}",
        "voltage": round(random.uniform(200, 250), 2),  # in volts
        "current": round(random.uniform(0, 100), 2),    # in amperes
        "temperature": round(random.uniform(20, 80), 2),# in Celsius
        "soc": round(random.uniform(20, 100), 2)        # State of Charge in %
    }

if __name__ == "__main__":
    try:
        while True:
            telemetry = generate_telemetry()
            producer.send('bess_telemetry', telemetry)
            print(f"Produced: {telemetry}")
            time.sleep(1)  # Publish every second
    except KeyboardInterrupt:
        producer.close()
        print("Data producer stopped.")
