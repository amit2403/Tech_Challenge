from fastapi import FastAPI
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from pydantic import BaseModel
import os

# Initialize FastAPI app
app = FastAPI()

# Define InfluxDB credentials (replace with your InfluxDB setup)
INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "AxvNoLdFyPTMnwTlC8ByesLxFYpSytkmuYrzhqOhk7eMqE-CdxVyzGjqaKgAx5a5dLAAzyLbyhn692JymmQEKg==")
INFLUXDB_ORG = "test"
INFLUXDB_BUCKET = "bess"

# InfluxDB Client setup
client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
query_api = client.query_api()

# Define model for telemetry data input
class Telemetry(BaseModel):
    device_id: str
    value: float
    timestamp: str  # ISO format timestamp

# Sample endpoint to write data to InfluxDB
@app.post("/bess")
async def write_bess(bess: Telemetry):
    write_api = client.write_api(write_options=SYNCHRONOUS)
    point = Point("bess_telemetry") \
        .tag("device_id", bess.device_id) \
        .field("value", bess.value) \
        .time(bess.timestamp)
    write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
    return {"message": "BESS Telemetry data written successfully"}

# Sample endpoint to query data from InfluxDB
@app.get("/bess/{device_id}")
async def get_bess(device_id: str):
    query = f'from(bucket: "{INFLUXDB_BUCKET}") |> range(start: -1h) |> filter(fn: (r) => r["device_id"] == "{device_id}")'
    result = query_api.query(org=INFLUXDB_ORG, query=query)
    data = []
    for table in result:
        for record in table.records:
            data.append({"device_id": record["device_id"], "value": record["_value"], "time": record["_time"]})
    return {"data": data}

# Run the app with uvicorn (start server with: uvicorn <filename>:app --reload)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
