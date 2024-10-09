from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from influxdb import InfluxDBClient
import time

app = FastAPI()

# Initialize InfluxDB client
influx_client = InfluxDBClient(host='localhost', port=8086)
influx_client.switch_database('ems_bess')

class Telemetry(BaseModel):
    timestamp: int
    battery_id: str
    voltage: float
    current: float
    temperature: float
    soc: float

@app.get("/telemetry/latest", response_model=List[Telemetry])
def get_latest_telemetry():
    query = """
    SELECT LAST("voltage") as voltage, LAST("current") as current,
           LAST("temperature") as temperature, LAST("soc") as soc
    FROM bess_telemetry
    GROUP BY "battery_id"
    """
    result = influx_client.query(query)
    telemetry_list = []
    for battery_id, points in result.items():
        if points:
            point = points[0]
            telemetry = Telemetry(
                timestamp=int(time.time() * 1000),
                battery_id=battery_id[1]["battery_id"],
                voltage=point['voltage'],
                current=point['current'],
                temperature=point['temperature'],
                soc=point['soc']
            )
            telemetry_list.append(telemetry)
    return telemetry_list

@app.get("/telemetry/history/{battery_id}", response_model=List[Telemetry])
def get_telemetry_history(battery_id: str, limit: int = 10):
    query = f"""
    SELECT "voltage", "current", "temperature", "soc" 
    FROM bess_telemetry 
    WHERE "battery_id" = '{battery_id}' 
    ORDER BY time DESC 
    LIMIT {limit}
    """
    result = influx_client.query(query)
    telemetry_list = []
    for point in result.get_points():
        telemetry = Telemetry(
            timestamp=int(time.mktime(point['time'].timetuple()) * 1000),
            battery_id=battery_id,
            voltage=point['voltage'],
            current=point['current'],
            temperature=point['temperature'],
            soc=point['soc']
        )
        telemetry_list.append(telemetry)
    if not telemetry_list:
        raise HTTPException(status_code=404, detail="Battery ID not found")
    return telemetry_list
