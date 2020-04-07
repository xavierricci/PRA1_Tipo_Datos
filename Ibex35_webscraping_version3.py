#!/usr/bin/env python
# coding: utf-8

# Recogida de datos del Ibex35 (para simplificar el formato para mostrar los datos mantenemos las mismas 35 empresas como referencia, en caso de que el listado cambie, se deberia empezar un nuevo listado).

# In[ ]:


# Cargando librerias
import os
import requests
import pandas as pd
import numpy
import csv
from bs4 import BeautifulSoup
from dateutil.tz import gettz
from time import sleep
import datetime


#indicamos la web
url_page = 'http://www.bolsamadrid.es/esp/aspx/Mercados/Precios.aspx?indice=ESI100000000'

#introducimos el html en un objeto beautifulSoap
page = requests.get(url_page).text 
soup = BeautifulSoup(page, "lxml")

#seleccionamos la tabla a partir del Xpath //*[@id="ctl00_Contenido_tblAcciones"] que copiamos con el boton derecho sobre el inspector de html de firefox
tabla = soup.find('table', attrs={'id': "ctl00_Contenido_tblAcciones"})
tabla2 = soup.find('table', attrs={'id': "ctl00_Contenido_tblÍndice"})



#para que el programa funcione igual aunque lo lancemos desde cualquier lugar del mundo usamos como referencia la hora de madrid
def today():
    t=datetime.datetime.now(gettz("Europe/Madrid")).isoformat()
    year=t[0:4]
    month=t[5:7]
    day=t[8:10]
    return day+"/"+month+"/"+year
#'07/04/2020'
today=today()

#creamos una funcion para iterar por los datos que nos interesan
#vemos que el primer nombre esta en /html/body/div[1]/table/tbody/tr[4]/td[2]/div[1]/form/div[6]/table/tbody/tr[2]/td[1]
#y que su precio de cierre es       /html/body/div[1]/table/tbody/tr[4]/td[2]/div[1]/form/div[6]/table/tbody/tr[2]/td[2]
def iteracionTabla(x):
    listado = []
    name=""
    price=""
    #creamos un contador para recorrer las filas identificadas en el html con 'tr'
    nroFila=-1
    for fila in tabla.find_all("tr"):
        #para cada fila se selecciona 
        if nroFila==x:
            #creamos un contador para recorrer las celdas identificadas con 'td'
            nroCelda=0
            for celda in fila.find_all('td'):
                #el contador nos permite seleccionar la casilla que queremos. la guardamos en la lista
                if nroCelda==0:
                    name=celda.text
                    listado.append(name)
                if nroCelda==1:
                    price=celda.text
                    listado.append(price)
                nroCelda=nroCelda+1
        nroFila=nroFila+1
    return listado

#recogemos tambien el total (creo) PUEDE SERVIR PARA HACER UNA COMPARATIVA GENERAL?
def ibexTotal():
    listadoExtra=[]
    date=""
    price=""
    nroFila=-1
    for fila in tabla2.find_all("tr"):
        if nroFila==0:
            #creamos un contador para recorrer las celdas identificadas con 'td'
            nroCelda=0
            for celda in fila.find_all('td'):
                #guardamos el precio
                if nroCelda==2:
                    price=celda.text
                if nroCelda==6:
                    date=celda.text
                    listadoExtra.append(date) 
                    # permite el seguimiento de la fecha de la entrada (fin de semana la bolsa no carga)
                    listadoExtra.append(price)
                nroCelda=nroCelda+1
        nroFila=nroFila+1
    return listadoExtra

#anadimos los resultados a una sola lista 
def listadoDiario():
    listadoTotal=[]
    listadoTotal.append(ibexTotal()) 
    for x in range(35):  
        listadoTotal.append(iteracionTabla(x))    
    return listadoTotal
#un solo documento continene: el total diario(creo), la fecha y las 35 empresas con su valor 

#listadoDiario()[0]


def programaRecogida():
    #indicamos la web
    url_page = 'http://www.bolsamadrid.es/esp/aspx/Mercados/Precios.aspx?indice=ESI100000000'

    #introducimos el html en un objeto beautifulSoap
    page = requests.get(url_page).text 
    soup = BeautifulSoup(page, "lxml")

    #seleccionamos la tabla a partir del Xpath //*[@id="ctl00_Contenido_tblAcciones"] que copiamos con el boton derecho sobre el inspector de html de firefox
    tabla = soup.find('table', attrs={'id': "ctl00_Contenido_tblAcciones"})

    tabla2 = soup.find('table', attrs={'id': "ctl00_Contenido_tblÍndice"})

    
    #ordenamos los datos recogidos en dos listas separadas para crear un dataframe
    list = []
    list = listadoDiario()

    nombres=[]
    for x in range(len(list)):
        nombres.append(list[x][0])
    
    precios=[]
    for x in range(len(list)):
        precios.append(list[x][1])
    

    #creacion de un dataframe
    fecha = list[0][0]
    nombres[0] = 'TOTAL'
    data = {'empresa': nombres,
            fecha: precios
            }

    df = pd.DataFrame (data, columns = ['empresa',fecha])



    #almacenado de los datos en un csv que se va actualizando siempre que la fecha de entrada de los datos haya cambiado 

    #primero nos aseguramos de si el documento ya existe y si no existe lo creamos
    if os.path.isfile('ibex35.csv') == False:
        df.to_csv('ibex35.csv', encoding='utf −8 ',index=False,sep="\t")

    #creamos un documento de trabajo importando los datos ya guardados
    dfGuardado = pd.read_csv('ibex35.csv',sep="\t")


    #miramos si hoy ya se ha hecho la carga para evitar cargar dos veces los mismos datos
    if dfGuardado.columns[-1] != (today):
        #es los datos que estamos cargando son los mismos del dia anterior es pq la bolsa no abre hoy (findesemana o catastrofe)
        if dfGuardado.columns[-1][0:10] >= (fecha):
            dfGuardado[today +'_Cerrado'] = precios #en caso de que la ficha no se modifique (el fin de semana la bolsa no se actualiza) no habra entrada 
        else:
            dfGuardado[today] = precios #en caso de que la ficha no se modifique (el fin de semana la bolsa no se actualiza) no habra entrada 
   
        dfGuardado.to_csv('ibex35.csv', encoding='utf −8 ',index=False,sep="\t")
    else:
        pass
#dfGuardado 



def borrarUltimaColumna():
    dfGuardado = pd.read_csv('ibex35.csv',sep="\t")
    del dfGuardado[dfGuardado.columns[-1]]
    dfGuardado.to_csv('ibex35.csv', encoding='utf −8 ',index=False,sep="\t")





# esta funcion arranca el programa (que ya no se apaga) y lo lanza cada dia a las 17:45, hora de madrid cuando se cierra la bolsa 
def lanzarScraping():
    today=datetime.datetime.now(gettz("Europe/Madrid")).isoformat()[1:10]
  
    #PERIOD_OF_TIME = 82800 # 24h 

    while True :
    
        horaMadrid=datetime.datetime.now(gettz("Europe/Madrid")).isoformat()[11:16]
        
        if horaMadrid > '17:45':
            
            programaRecogida()

            #una vez lanzado el programa y modificado el csv el programa espera hasta el dia siguiente para relanzar 
            sleep(82740)    #23:59h en minutos 



lanzarScraping()

#borrarUltimaColumna()


# In[43]:


#borrarUltimaColumna()


# In[ ]:




