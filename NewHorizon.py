import pandas
import time
import datetime
import smbus
import RPi.GPIO as GPIO
import dht11
import numpy as np
import threading

GPIO.cleanup()
GPIO.setwarnings(True)
GPIO.setmode(GPIO.BCM)

#DHT11 ping
instance = dht11.DHT11(pin=14)

#A/D converter
address = 0x48  
A0 = 0x40
A1 = 0x41
A2 = 0x42
A3 = 0x43
bus = smbus.SMBus(1)

#Water pump pin
GPIO.setup(5, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)

#collector
start_data = {"Date":["0"],"Temperature":["0"],"Soil Moisture":["0"],"Humidity":["0"],"LDR":["0"],"Pump":["0"]}
df = pandas.DataFrame(data=start_data,columns=["Date","Temperature","Soil Moisture","Humidity","LDR","Pump"])

def dht():

    global humidity
    global temp

    result = instance.read()
    if result.temperature == 0:
        result = instance.read()
    else:
        temp = str(result.temperature) + "C"
        humidity = "%" + str(result.humidity)
    time.sleep(5)

    
def converter(wait_time):
    global soil_moisture

    bus.write_byte(address,A2) #A2 İnput soil moisture
    value = bus.read_byte(address)
    soil_moisture = 100-(value*100/255)
    time.sleep(wait_time)

    global LDR
    bus.write_byte(address,A0)#LDR input
    LDR = bus.read_byte(address)

def water_pump(soil_moisture):
    global wait_time

    if soil_moisture < 60:
        wait_time = 0.1
        GPIO.output(5, GPIO.HIGH)
        GPIO.output(6, GPIO.LOW)
        if soil_moisture > 75:
            GPIO.output(5, GPIO.LOW)
            GPIO.output(6, GPIO.LOW)
            wait_time = 3


def data_collector(df,humidity,temp,soil_moisture,LDR,wait_time):
    now = datetime.datetime.now()
    date = datetime.datetime.strftime(now,'%x %X')
    if wait_time == 0.1:
        pump_key = 1
    else :
        pump_key = 0


    dataset = {"Date":[date],"Temperature":[temp],"Soil Moisture":[soil_moisture],"Humidity":[humidity],"LDR":[LDR],"Pump":[pump_key]}
    
    df2 = pandas.DataFrame(data=dataset,columns=["Date","Temperature","Soil Moisture","Humidity","LDR","Pump"])
    df = pandas.concat([df,df2])
    df.to_csv("dataset.cvs")
    del dataset
    time.sleep(10)






