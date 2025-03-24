import json
import csv
import math

RADIUS_OF_EARTH_IN_METERS = 6378000
ACCURACY_OF_SENSORS_IN_METERS = 100

def readJsonFile(filePath: str) -> list:
    try: 
        with open(filePath, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except Exception as exeption:
        print("Error reading json: " + exeption)

def readCsvFile(filePath: str) -> list: 
    try:
        with open(filePath, 'r', encoding='utf-8') as file:
            csvReader = csv.DictReader(file)
            return [row for row in csvReader]
    except Exception as exeption:
        print("Error reading csv: " + exeption)

def convertStringToFloat(dataPoint: dict, key: str) -> dict:
    dataPoint[key] = float(dataPoint[key])

def convertDegreesToRadians(dataPoint: dict, key: str) -> float:
    dataPoint[key] = dataPoint[key] * math.pi / 180 

def convertSphericalToCartesain(dataPoint: dict, radius: float, longitudeKey: str, latitudeKey: str) -> dict:
    theta = dataPoint[longitudeKey]
    phi = dataPoint[latitudeKey]

    dataPoint['x'] = radius * math.cos(phi) * math.cos(theta)
    dataPoint['y'] = radius * math.cos(phi) * math.sin(theta)
    dataPoint['z'] = radius * math.sin(phi)

def transformGeospatialData(dataSet: list[dict]) -> list[dict]:
    for data in dataSet:
        convertStringToFloat(data, 'longitude')
        convertDegreesToRadians(data, 'longitude')
        convertStringToFloat(data, 'latitude')
        convertDegreesToRadians(data, 'latitude')
        convertSphericalToCartesain(data, RADIUS_OF_EARTH_IN_METERS, 'longitude', 'latitude')

# This uses the direction vector to compute distance (linear distance). Since the sensor range is so small compared to the raduis of the earth, the delta in distance from the curvature of the earth is negligible
def computeDistanceBetweenTwoCartesianPoints(point1: dict, point2: dict) -> float:
    x1, y1, z1 = point1['x'], point1['y'], point1['z']
    x2, y2, z2 = point2['x'], point2['y'], point2['z']

    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2)

def getCorrelatedData(dataSet1: list, dataSet2: list, sensorRangeInMeters: float) -> dict:
    transformGeospatialData(dataSet1)
    transformGeospatialData(dataSet2)
    
    correlatedData = {}
    for dataPoint1 in dataSet1:
        for dataPoint2 in dataSet2:
            distanceBetweenPointsInMeters = computeDistanceBetweenTwoCartesianPoints(dataPoint1, dataPoint2)
            if(distanceBetweenPointsInMeters <= sensorRangeInMeters):
                correlatedData[dataPoint1['id']] = dataPoint2['id']
    
    return correlatedData

# Approach
# First take in the data and convert numbers to floats
# Then convert spherical longitude and latitude into cartesian x, y, z
# Then for every data point in set 1, compute its distance from every data point in set 2. If they are within 100 meters, they correlate
# Since we are matching all data points in one set with all the data points in the other, this solution has time complexity O(n^2) 

if __name__ == "__main__":
    csvSensorData = readCsvFile("SensorData1.csv")
    jsonSensorData = readJsonFile("SensorData2.json")

    correlatedData = getCorrelatedData(csvSensorData, jsonSensorData, ACCURACY_OF_SENSORS_IN_METERS)

    with open('output.json', 'w') as file:
        json.dump(correlatedData, file, indent=4)
