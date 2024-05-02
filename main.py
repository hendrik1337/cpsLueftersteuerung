#! /bin/python3
import time
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.OUT)


def read_file(filename):
    with open(filename, "r") as f:
        data = f.read().strip()
    return data


def log(filename, timestamp, temp_c, temp_f, humidity, pressure):
    with open(filename, "a") as f:
        f.write(str(timestamp) + "\n")
        f.write(str(temp_c) + "\n")
        f.write(str(temp_f) + "\n")
        f.write(str(humidity) + "\n")
        f.write(str(pressure) + "\n")
    f.close()


def fan_on():
    GPIO.output(23, GPIO.HIGH)


def fan_off():
    GPIO.output(23, GPIO.LOW)


def main():
    while True:
        now = time.localtime()
        current_time = time.strftime("========== %d.%M.%y %H:%M:%S ==========", now)

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

        print(current_time)
        print("Temperatur (Celsius): " + str(temperature) + "°C")
        print("Temperatur (Fahrenheit): " + str(fahrenheit) + "°F")
        print("Luftfeuchte: " + str(humidity) + "%")
        print("Luftdruck: " + str(pressure) + "hPa")
        print()

        log("/opt/lueftersteuerung/log.txt", current_time, temperature, fahrenheit, humidity, pressure)

        if temperature > 30.0:
            fan_on()
        else:
            fan_off()
        time.sleep(10)


if __name__ == '__main__':
    main()
