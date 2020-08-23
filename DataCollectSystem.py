import pandas
import time
import datetime
import smbus
import RPi.GPIO as GPIO
import dht11
import numpy as np


now = datetime.datetime.now()
tarih = datetime.datetime.strftime(now,'%x %X')

GPIO.setwarnings(True)
GPIO.setmode(GPIO.BCM)

instance = dht11.DHT11(pin=14) #changeable


address = 0x48
A0 = 0x40
A1 = 0x41
A2 = 0x42
A3 = 0x43
bus = smbus.SMBus(1)
start_data = {"Date":["0"],"Temperature":["0"],"Soil Moisture":["0"],"Humidity":["0"]}
df = pandas.DataFrame(data=start_data,columns=["Date","Temperature","Soil Moisture","Humidity"])

while True:
    #Soil Moisture 
    bus.write_byte(address,A2) #A2 İnput 
    value = bus.read_byte(address)
    soil_moisture = 100-(value*100/255)

    #dht11
    result = instance.read()
    temp = str(result.temperature) + "C"
    humidity = "%" + str(result.humidity)

    #date informations
    now = datetime.datetime.now()
    date = datetime.datetime.strftime(now,'%x %X')

    dataset = {"Date":[date],"Temperature":[temp],"Soil Moisture":[soil_moisture],"Humidity":[humidity]}

    df2 = pandas.DataFrame(data=dataset,columns=["Date","Temperature","Soil Moisture","Humidity"])
    df = pandas.concat([df,df2])
    filename = datetime.datetime.strftime(now,'%x ')

    df.to_csv("veriseti.cvs")
    del dataset
    time.sleep(10)


#Vr = 3*3 * float(value) / 255
#Rt = 10000 * Vr / (5 - Vr)
#temp = 1/(((math.log(Rt / 10000)) / 3950) + (1 / (273.15+35)))
#temp = temp - 273.15
#GPIO.cleanup()
#GPIO.setmode(GPIO.BCM)
#GPIO.setup(5, GPIO.OUT)
#GPIO.setup(6, GPIO.OUT)
#GPIO.output(5, GPIO.HIGH)
#GPIO.output(6, GPIO.LOW)
#time.sleep(5)
#GPIO.output(5, GPIO.LOW)
#GPIO.output(6, GPIO.LOW)
#time.sleep(4)
