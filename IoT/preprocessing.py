import pandas.io.sql as sql
from xlsxwriter.workbook import Workbook
import MySQLdb

# Konfigurasi Database
db = MySQLdb.connect(user="root",passwd="pass",db="cabai_merah")
cursor = db.cursor()

for i in range (5):
    query1 = "SELECT DATE(tanggalPencatatan),idTanaman,MAX(PH), MIN(PH), ROUND(AVG(PH),2) ,MAX(kelembabanTanah), MIN(kelembabanTanah), ROUND(AVG(kelembabanTanah),2),MAX(suhu), MIN(suhu), ROUND(AVG(suhu),2), MAX(kelembabanUdara), MIN(kelembabanUdara), ROUND(AVG(kelembabanUdara),2) FROM datalingkungan JOIN kondisidaun WHERE datalingkungan.idKondisi = kondisidaun.idKondisi AND idZonaWaktu = %s GROUP BY datalingkungan.idKondisi"
    plantId = (i+1,)
    cursor.execute(query1, plantId)
    data = cursor.fetchall()
    dataLength = len(data)

    for j in range (dataLength):
        try:
            cursor.execute("""INSERT into data_test(tanggal,tanaman,ph_max,ph_min,ph_avg,kelembabanTanah_max,kelembabanTanah_min,kelembabanTanah_avg,suhu_max,suhu_min,suhu_avg,kelembabanUdara_max,kelembabanUdara_min,kelembabanUdara_avg) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",(data[j][0],data[j][1],data[j][2],data[j][3],data[j][4],data[j][5],data[j][6],data[j][7],data[j][8],data[j][9],data[j][10],data[j][11],data[j][12],data[j][13]))
            db.commit()
        except:
            db.rollback()
            print("error")


query = "SELECT DATE_FORMAT(tanggal, '%d %M %Y'),tanaman,ph_max,ph_min,ph_avg,kelembabanTanah_max,kelembabanTanah_min,kelembabanTanah_avg,suhu_max,suhu_min,suhu_avg,kelembabanUdara_max,kelembabanUdara_min,kelembabanUdara_avg FROM data_test"
cursor.execute(query)

workbook = Workbook('data_test.xlsx')
sheet = workbook.add_worksheet()
for r, row in enumerate(cursor.fetchall()):
    for c, col in enumerate(row):
        sheet.write(r, c, col)

workbook.close()