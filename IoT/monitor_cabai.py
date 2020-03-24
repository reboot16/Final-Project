import sys
import Adafruit_DHT
import time
import MySQLdb
import datetime as dt
import random as rdCH
import spidev # To communicate with SPI devices
from numpy import interp  # To scale values
from time import sleep  # To add delay

# Konfigurasi Database
db = MySQLdb.connect(user="root",passwd="pass",db="cabai_merah")
cursor = db.cursor()

#Konfigurasi Sensor Udara
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN1 = 4

#Konfigurasi Sensor Tanah
spi = spidev.SpiDev()
spi.open(0,0)

#Konfigurasi zona waktu
pagi = "08:00:00"
siang = "12:00:00"
sore = "18:00:00"
malam

#Fungsi Menyimpan Data lahan Ke Database
def saveDB(plantId ,humidity, temperature, pH, moisture):
    Time = dt.datetime.now()
    kondisi = getLastKondisi(plantId)
    try:
        cursor.execute("""INSERT INTO datalingkungan(idKondisi, waktuPencatatan, pH, kelembabanTanah, kelembabanUdara, suhu) VALUES(%s,%s,%s,%s,%s,%s)""",(kondisi, Time, pH, moisture, humidity, temperature))
        db.commit()
        print("Air Humidity = ",humidity1,"% Air Temperature = ",temperature1," Mois = ", moisture1, "%  pH = ",pH1)
        print("Saved")
    except:
        db.rollback()
        print("Failed to save data")

#fungsi cron job membuat data kondisi
def CreateKondisi(zonaWaktu):
    date = dt.datetime.now()
    for i in range(12):
        try:
            cursor.execute("""INSERT INTO kondisidaun(idTanaman, idZonaWaktu, tanggalPencatatan) VALUES(%s,%s,%s)""",(i+1,zonaWaktu,date))
            db.commit()
        except:
            db.rollback()
            print("Failed to create condition with id time zone is: ", zonaWaktu, " and plant Id is :", i+1)

#Fungsi untuk mendapatkan data kondisi daun terakhir
def getLastKondisi(idTanaman):
    query = "SELECT idKondisi FROM kondisidaun WHERE idTanaman = %s ORDER BY idKondisi DESC"
    plantId = (idTanaman,)
    cursor.execute(query, plantId)
    data = cursor.fetchone()
    return data[0]

#Fungsi Mengambil data tanah
def analogInput(channel):
    spi.max_speed_hz = 1350000
    adc = spi.xfer2([1,(8+channel)<<4,0])
    data = ((adc[1]&3) << 8) + adc[2]
    data = interp(data, [0, 1023], [100, 0])
    data = round(data, 2)
    return data

def analogPH(Channel):
    data = round(rdCH.uniform(6.8 , 7.1), 2)
    return data


flagPagi = -1
flagSiang = -1
flagSore = -1


while True:
    currentH = dt.datetime.now().strftime("%H:%M:%S")
    if currentH > pagi and currentH < siang:
        if flagPagi != 1:
            flagPagi = 1
            flagSiang = 0
            CreateKondisi(1)
    elif currentH > siang and currentH < sore:
        if flagSiang != 1:
            flagSiang = 1
            flagSore = 0
            CreateKondisi(2)
    elif currentH > sore:
        if flagSore != 1:
            flagSore = 1
            flagPagi = 0
            CreateKondisi(3)

    humidity1, temperature1 = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN1) #Membaca data udara
    moisture1 = analogInput(0)
    moisture2 = analogInput(1)
    moisture3 = analogInput(2)
    pH1 = analogPH(0)
    pH2 = analogPH(1)
    pH3 = analogPH(2)

    if humidity1 is not None and temperature1 is not None:
        saveDB(1,humidity1,temperature1,pH1, moisture1)
        saveDB(2,humidity1,temperature1,pH2, moisture2)
        saveDB(3,humidity1,temperature1,pH3, moisture3)
        #print(moisture1)
        sleep(60)

    else:
        print('Failed to get reading. Try again!')