import json
from kafka import KafkaConsumer
from influxdb import InfluxDBClient

# Initialize Kafka consumer
consumer = KafkaConsumer(
    'bess_telemetry',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='bess_group',
    value_serializer=lambda v: json.loads(v.decode('utf-8'))
)

# Initialize InfluxDB client
influx_client = InfluxDBClient(host='localhost', port=8086)
influx_client.switch_database('ems_bess')

# Create database if not exists
databases = influx_client.get_list_database()
if not any(db['name'] == 'ems_bess' for db in databases):
    influx_client.create_database('ems_bess')

def process_telemetry(data):
    # Simple anomaly detection: temperature > 70°C or SOC < 30%
    anomalies = []
    if data['temperature'] > 70:
        anomalies.append('Over Temperature')
    if data['soc'] < 30:
        anomalies.append('Low State of Charge')
    return anomalies

if __name__ == "__main__":
    for message in consumer:
        telemetry = json.loads(message.value)
        anomalies = process_telemetry(telemetry)
        
        # Prepare InfluxDB data point
        json_body = [
            {
                "measurement": "bess_telemetry",
                "tags": {
                    "battery_id": telemetry["battery_id"]
                },
                "time": telemetry["timestamp"],
                "fields": {
                    "voltage": telemetry["voltage"],
                    "current": telemetry["current"],
                    "temperature": telemetry["temperature"],
                    "soc": telemetry["soc"]
                }
            }
        ]

        # Write to InfluxDB
        influx_client.write_points(json_body)

        # Log anomalies
        if anomalies:
            print(f"Anomalies detected for {telemetry['battery_id']}: {anomalies}")
