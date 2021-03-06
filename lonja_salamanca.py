# coding=utf-8
import sys
import os
import requests
import csv
import argparse
from datetime import datetime
from datetime import timedelta
from bs4 import BeautifulSoup
#Captura de los comandos de fecha de inicio y de fin
parser = argparse.ArgumentParser()
parser.add_argument("--startDate", help="Fecha de inicio del intervalo")
parser.add_argument("--endDate", help="Fecha de fin del intervalo")
args = parser.parse_args()
reload(sys)
def to_unicode_or_bust(obj, encoding="latin1"):
    if isinstance(obj, basestring):
        if not isinstance(obj, unicode):
            obj=unicode(obj, encoding)
    return obj
#Función para obtener los datos
def queryPrices( queryURL, paramsValues,headersValues,elementList,date2Filter ):
    paramsValues['fecha']=date2Filter
    response= requests.post(queryURL, data = paramsValues, headers=headersValues)
    soup = BeautifulSoup(response.text,"html.parser")
    table=soup.find('table',{'border':'1'});#Identificación de la tabla que contiene los datos a almacenar
    currentIndex=0
    for row in table.findAll("tr"):
        cells = row.findAll('td')
        if (currentIndex > 0):
            if len(cells)==8:
                Producto=cells[0].find(text=True).encode("latin1")
                Categoria=cells[1].find(text=True).encode("latin1")
                Anterior=cells[2].find(text=True)
                Ultimo=cells[3].find(text=True)
                Dif=cells[4].find(text=True)
                Media=cells[5].find(text=True)
                FechaTabla=cells[7].find(text=True)
            else:
                Producto=cells[0].find(text=True).encode("latin1")
                Categoria=cells[1].find(text=True).encode("latin1")
                Anterior=cells[2].find(text=True)
                Ultimo=cells[3].find(text=True)
                Dif=cells[4].find(text=True)
                Media=cells[5].find(text=True)
                FechaTabla=cells[7].find(text=True)
            element=[Producto,Categoria,Anterior,Ultimo,Dif,Media,FechaTabla,date2Filter]
            elementList.append(element)
        currentIndex=currentIndex+1
    return

currentDir = os.path.dirname(__file__)
filename = "lonja_salamanca.csv" #Nombre del csv de almacenamiento
filePath = os.path.join(currentDir, filename)
#URL de la página a consultar
url="http://www.lasalina.es/Aplicaciones/GestorInter.jsp?prestacion=Lonja&funcion=BusquedaCotizacion"
currentDate=''
headerValues={}
formData={}

#cabecera de la consulta HTTP
headerValues['Origin']='http://www.lasalina.es'
headerValues['Referer']='http://www.lasalina.es/Aplicaciones/GestorInter.jsp'
headerValues['Content-Type']='application/x-www-form-urlencoded'

#Valores para la consulta HTTP
formData['presentation']='Lonja'
formData['funcion']='BusquedaCotizacion'
formData['mesa']='5'
formData['producto']='16'
formData['categoria']='0'
formData['productoStr']='Cereales'
formData['categoriaStr']='Cereales'

#Fecha de inicio y fin
startDate = datetime.strptime(args.startDate, "%d/%m/%Y")
endDate = datetime.strptime(args.endDate,"%d/%m/%Y")
priceList=[]
#Listado de valores del csv
headerList=["Producto","Categoria","Anterior","Ultimo","Dif","Medida","Fecha ","Fecha Consulta"]
priceList.append(headerList)
while startDate <= endDate:
    currentDate = startDate.strftime('%d/%m/%Y')
    print ("Generando base de datos %s" %  currentDate)
    queryPrices(url,formData,headerValues,priceList,currentDate)
    startDate = startDate + timedelta(days=7) #Realizamos una consulta semanal desde la fecha de inicio hasta la fecha de fin
#Escritura del csv  
with open(filePath, 'w')as csvFile:
    writer = csv.writer(csvFile)
    for priceElement in priceList:
        writer.writerow(priceElement)
