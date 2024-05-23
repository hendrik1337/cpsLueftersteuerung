#! /bin/python3
import math
import time
import os
from influxdb_client import InfluxDBClient, Point, WritePrecision


def read_file(filename):
    with open(filename, "r") as f:
        data = f.read().strip()
    return data


def log(filename, timestamp, temp_c, temp_f, humidity, pressure, taupunkt):
    with open(filename, "a") as f:
        f.write(str(timestamp) + "°C\n")
        f.write("Temperatur (Celsius): " + str(temp_c) + "°C\n")
        f.write("Temperatur (Fahrenheit): " + str(temp_f) + "°F\n")
        f.write("Luftfeuchte: " + str(humidity) + "%\n")
        f.write("Luftdruck: " + str(pressure) + "hPa\n")
        f.write("Taupunkt: " + str(taupunkt) + "°C\n")
    f.close()


def send_to_influx(timestamp, temp_c, temp_f, humidity, pressure, taupunkt):
    print(timestamp)
    url = "http://localhost:8086"  # Replace with your InfluxDB URL
    token = "LTEybj-7h-ko_whHAeyTFEJp4b3alfBZbS_2lAScNSFA4Pe5S0ECmg-BsntnzfQZo0-z9uTF5yOv85kTC8Yk_g=="  # Replace with your InfluxDB token
    org = "gruppe2"
    with InfluxDBClient(url=url, token=token, org=org) as client:
        with client.write_api() as write_api:
            try:
                # Create a Point object with your data
                point = Point("bme280") \
                    .tag("device", "sensor1") \
                    .field("temp_c", temp_c) \
                    .field("temp_f", temp_f) \
                    .field("humidity", humidity) \
                    .field("pressure", pressure) \
                    .field("taupunkt", taupunkt) \
                    .time(int(time.time() * 1000), WritePrecision.MS)

                # Write the point to InfluxDB
                write_api.write(
                    bucket="gruppe2",
                    org="gruppe2",
                    record=point
                )
            except Exception as e:
                print(e)


def taupunkt_berechnen(temperatur, luftfeuchtigkeit):
    a = 17.625
    b = 243.04
    c = math.log(luftfeuchtigkeit / 100)
    d = a * temperatur / (b + temperatur)
    e = c + d
    taupunkt = (b * e) / (a - e)
    return taupunkt


def csv_export(filename, timestamp, temp_c, temp_f, humidity, pressure, taupunkt):
    if not os.path.isfile(filename):
        with open(filename, "w") as out:
            out.write("#datatype measurement,string,double,double,long,long,double\n")
            out.close()

    with open(filename, "a") as out:
        out.write(f"bme280,{timestamp};{temp_c};{temp_f};{humidity};{pressure};{taupunkt}\n")
        out.close()


def fan_on():
    os.system("pigs w 23 1")


def fan_off():
    os.system("pigs w 23 0")


def main():
    while True:
        now = time.localtime()
        current_time = time.strftime("========== %d.%m.%y %H:%M:%S ==========", now)

        path = "/sys/bus/iio/devices/iio:device0/"
        temperature = read_file(f'{path}in_temp_input')
        temperature = float(temperature) / 1000.0
        temperature = round(temperature, 2)

        fahrenheit = temperature * 9.0 / 5.0 + 32.0
        fahrenheit = round(fahrenheit, 2)

        humidity = read_file(f'{path}in_humidityrelative_input')
        humidity = int(float(humidity)) / 1000
        humidity = int(humidity)

        pressure = read_file(f'{path}in_pressure_input')
        pressure = int(float(pressure)) * 10

        taupunkt = taupunkt_berechnen(temperature, humidity)
        taupunkt = round(taupunkt, 2)

        print(current_time)
        print("Temperatur (Celsius): " + str(temperature) + "°C")
        print("Temperatur (Fahrenheit): " + str(fahrenheit) + "°F")
        print("Luftfeuchte: " + str(humidity) + "%")
        print("Luftdruck: " + str(pressure) + "hPa")
        print("Taupunkt: " + str(taupunkt))
        print()

        log("/opt/lueftersteuerung/log.txt", current_time, temperature, fahrenheit, humidity, pressure, taupunkt)
        csv_export("/opt/lueftersteuerung/auswertung/influx_data/log.csv", time.strftime("%d.%m.%y %H:%M:%S", now),
                   temperature, fahrenheit,
                   humidity, pressure, taupunkt)
        send_to_influx(time.strftime("%d.%m.%y %H:%M:%S", now), temperature, fahrenheit, humidity, pressure, taupunkt)

        if temperature > 30.0:
            fan_on()
        else:
            fan_off()
        time.sleep(10)


if __name__ == '__main__':
    main()
