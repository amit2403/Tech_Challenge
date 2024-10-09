from flask import Flask, jsonify, request  
from influxdb import InfluxDBClient  
  
app = Flask(__name__)  
  
# InfluxDB configuration  
INFLUXDB_HOST = 'localhost'  
INFLUXDB_PORT = 8086  
INFLUXDB_DB = 'telemetry'  
  
# Create an InfluxDB client  
client = InfluxDBClient(INFLUXDB_HOST, INFLUXDB_PORT, INFLUXDB_DB)  
  
# Define the telemetry data model  
class TelemetryData:  
 def __init__(self, device_id, timestamp, metric_name, value):  
    self.device_id = device_id  
    self.timestamp = timestamp  
    self.metric_name = metric_name  
    self.value = value  
  
# Define the API endpoints  
@app.route('/telemetry', methods=['POST'])  
def ingest_telemetry_data():  
   data = request.get_json()  
   device_id = data['device_id']  
   timestamp = data['timestamp']  
   metric_name = data['metric_name']  
   value = data['value']  
  
   # Create a TelemetryData object  
   telemetry_data = TelemetryData(device_id, timestamp, metric_name, value)  
  
   # Write the telemetry data to InfluxDB  
   client.write_points([{  
      'measurement': metric_name,  
      'tags': {'device_id': device_id},  
      'fields': {'value': value},  
      'time': timestamp  
   }])  
  
   return jsonify({'message': 'Telemetry data ingested successfully'}), 201  
  
@app.route('/telemetry', methods=['GET'])  
def get_telemetry_data():  
   query = request.args.get('query')  
   if query:  
      # Query InfluxDB for the telemetry data  
      result = client.query(query)  
      data = []  
      for point in result.get_points():  
        data.append({  
           'device_id': point['device_id'],  
           'timestamp': point['time'],  
           'metric_name': point['measurement'],  
           'value': point['value']  
        })  
      return jsonify(data)  
   else:  
      return jsonify({'error': 'Invalid query'}), 400  
  
@app.route('/telemetry/devices', methods=['GET'])  
def get_devices():  
   # Query InfluxDB for the list of devices  
   result = client.query('SHOW TAG VALUES FROM "device_id"')  
   devices = []  
   for point in result.get_points():  
      devices.append(point['value'])  
   return jsonify(devices)  
  
@app.route('/telemetry/metrics', methods=['GET'])  
def get_metrics():  
   # Query InfluxDB for the list of metrics  
   result = client.query('SHOW MEASUREMENTS')  
   metrics = []  
   for point in result.get_points():  
      metrics.append(point['name'])  
   return jsonify(metrics)  
  
if __name__ == '__main__':  
   app.run(debug=True)
