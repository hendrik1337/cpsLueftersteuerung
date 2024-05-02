#! /bin/python3
# echo "bme280 0x76" > /sys/bus/i2c/devices/i2c-1/new_device
import time
from datetime import datetime

now = datetime.now()

current_time = now.strftime("%H:%M:%S")


def read_file(filename):
    with open(filename, "r") as f:
        data = f.read().strip()
    return data


def main():
    while True:
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print(current_time)

        path = "/sys/bus/iio/devices/iio:device0/"
        temperature = read_file(f'{path}in_temp_input')
        temperature = float(temperature) / 1000.0
        temperature = round(temperature, 2)

        humidity = read_file(f'{path}in_humidityrelative_input')
        humidity = float(humidity) / 1000.0
        humidity = round(humidity, 2)

        pressure = read_file(f'{path}in_pressure_input')
        pressure = float(pressure) * 10
        pressure = round(pressure, 2)

        print(str(temperature) + "°C")
        print(str(humidity) + "%")
        print(str(pressure) + "hPa")
        print()
        time.sleep(10)


if __name__ == '__main__':
    main()