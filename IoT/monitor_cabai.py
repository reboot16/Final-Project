import sys
import Adafruit_DHT
import time
import MySQLdb
import datetime as dt
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
pagi = "04:00:00"
siang = "10:00:00"
sore = "14:00:00"
petang = "16:30:00"
malam = "18:30:00"


#Fungsi Menyimpan Data lahan Ke Database
def saveDB(plantId ,humidity, temperature, moisture):
    Time = dt.datetime.now()
    moisture1 = 70.1
    kondisi = getLastKondisi(plantId)
    try:
        cursor.execute("""INSERT INTO datalingkungan(idKondisi, waktuPencatatan, kelembabanTanah, kelembabanUdara, suhu) VALUES(%s,%s,%s,%s,%s)""",(kondisi, Time, moisture1, humidity, temperature))
        db.commit()
        print("Air Humidity = ",humidity,"% Air Temperature = ",temperature," Mois = ", moisture, "%")
        print("Saved")
    except:
        db.rollback()
        print("Failed to save data")

#fungsi cron job membuat data kondisi
def CreateKondisi(zonaWaktu):
    date = dt.datetime.now()
    flag = 0
    for i in range(12):
        try:
            cursor.execute("""INSERT INTO kondisidaun(idTanaman, idZonaWaktu, tanggalPencatatan) VALUES(%s,%s,%s)""",(i+1,zonaWaktu,date))
            db.commit()
            flag = 1
        except:
            db.rollback()
            print("Failed to create condition with id time zone is: ", zonaWaktu, " and plant Id is :", i+1)
    if flag == 1:
        print("New Kondisi Daun created with zone id is ", zonaWaktu, " on ",date)

#Fungsi untuk mendapatkan data kondisi daun terakhir
def getLastKondisi(idTanaman):
    query = "SELECT idKondisi FROM kondisidaun WHERE idTanaman = %s ORDER BY idKondisi DESC"
    plantId = (idTanaman,)
    cursor.execute(query, plantId)
    data = cursor.fetchone()
    return data[0]

#Fungsi mencek data kondisidaun berdasarkan zona waktu pada 1 hari sudah ada atau tidak
def checkLastKondisi(idZonaWaktu):
    query = "SELECT idKondisi from kondisidaun WHERE DATE(tanggalPencatatan) = CURDATE() AND idZonaWaktu = %s"
    cursor.execute(query, (idZonaWaktu,))
    record = cursor.fetchall()
    if record:
        return True
    else:
        return False

#Fungsi Mengambil data tanah
def analogInput(channel):
    spi.max_speed_hz = 1350000
    adc = spi.xfer2([1,(8+channel)<<4,0])
    data = ((adc[1]&3) << 8) + adc[2]
    data = interp(data, [0, 1023], [100, 0])
    data = round(data, 2)
    data1 = 70.0
    return data1



while True:
    currentH = dt.datetime.now().strftime("%H:%M:%S")
    if currentH > pagi and currentH < siang:
        if checkLastKondisi(1) == False:
            CreateKondisi(1)
    elif currentH > siang and currentH < sore:
        if checkLastKondisi(2) == False:
            CreateKondisi(2)
    elif currentH > sore and currentH < petang:
        if checkLastKondisi(3) == False:
            CreateKondisi(3)
    elif currentH > petang and currentH < malam:
        if checkLastKondisi(4) == False:
            CreateKondisi(4)
    elif currentH > malam:
        if checkLastKondisi(5) == False:
            CreateKondisi(5)


    humidity1, temperature1 = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN1) #Membaca data udara
    moisture1 = analogInput(0)
    moisture2 = analogInput(1)
    moisture3 = analogInput(2)
    moisture4 = analogInput(3)
    moisture5 = analogInput(4)
    moisture6 = analogInput(5)
    moisture7 = analogInput(6)
    moisture8 = analogInput(7)


    if humidity1 is not None and temperature1 is not None:
        saveDB(1,humidity1,temperature1, moisture1)
        saveDB(2,humidity1,temperature1, moisture2)
        saveDB(3,humidity1,temperature1, moisture3)
        saveDB(4,humidity1,temperature1, moisture4)
        saveDB(5,humidity1,temperature1, moisture1)
        saveDB(6,humidity1,temperature1, moisture2)
        saveDB(7,humidity1,temperature1, moisture5)
        saveDB(8,humidity1,temperature1, moisture6)
        saveDB(9,humidity1,temperature1, moisture7)
        saveDB(10,humidity1,temperature1, moisture8)
        saveDB(11,humidity1,temperature1, moisture5)
        saveDB(12,humidity1,temperature1, moisture6)
        #print(moisture1)
        sleep(1800)

    else:
        print('Failed to get reading. Try again!')