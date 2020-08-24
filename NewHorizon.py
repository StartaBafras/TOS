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

#experimently
soil_moisture = 75 
wait_time = 3
humidity = 30


#collector
start_data = {"Date":["0"],"Temperature":["0"],"Soil Moisture":["0"],"Humidity":["0"],"LDR":["0"],"Pump":["0"]}
df = pandas.DataFrame(data=start_data,columns=["Date","Temperature","Soil Moisture","Humidity","LDR","Pump"])

def dht():
    global humidity
    global temp

    while True:

        result = instance.read()
        if result.temperature == 0:
            result = instance.read()
        else:
            temp = str(result.temperature) + "C"
            humidity = "%" + str(result.humidity)
        time.sleep(5)

    
def converter(wait_time):
    global soil_moisture
    while True:
        

        bus.write_byte(address,A2) #A2 İnput soil moisture
        value = bus.read_byte(address)
        soil_moisture = 100-(value*100/255)
        time.sleep(wait_time)

        global ldr
        bus.write_byte(address,A0)#LDR input
        ldr = bus.read_byte(address)

def water_pump(soil_moisture):
    global wait_time
    while True:
        if soil_moisture < 60:
            wait_time = 0.1
            GPIO.output(5, GPIO.HIGH)
            GPIO.output(6, GPIO.LOW)
            if soil_moisture > 75:
                GPIO.output(5, GPIO.LOW)
                GPIO.output(6, GPIO.LOW)
                wait_time = 3


def data_collector(df,humidity,temp,soil_moisture,ldr,wait_time):
    while True:
        now = datetime.datetime.now()
        date = datetime.datetime.strftime(now,'%x %X')
        if wait_time == 0.1:
            pump_key = 1
        else :
            pump_key = 0


        dataset = {"Date":[date],"Temperature":[temp],"Soil Moisture":[soil_moisture],"Humidity":[humidity],"LDR":[ldr],"Pump":[pump_key]}
        
        df2 = pandas.DataFrame(data=dataset,columns=["Date","Temperature","Soil Moisture","Humidity","LDR","Pump"])
        df = pandas.concat([df,df2])
        df.to_csv("dataset.cvs")
        del dataset
        time.sleep(10)

t1 = threading.Thread(target=dht)
t3 = threading.Thread(target=water_pump, args=(soil_moisture,))
t2 = threading.Thread(target=converter, args= (wait_time,))
t4 = threading.Thread(target=data_collector, args=(df,humidity,temp,soil_moisture,ldr,wait_time,))

t1.start()
time.sleep(5)
t3.start()
time.sleep(5)
t2.start()
time.sleep(15)
print(humidity,temp,soil_moisture,wait_time,ldr)
time.sleep(5)
data_collector(df,humidity,temp,soil_moisture,ldr,wait_time)



