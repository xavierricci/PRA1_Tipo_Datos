#!/usr/bin/env python
# coding: utf-8

# Recogida de datos del Ibex35

# In[1]:


# Cargando librerias
import os
import requests
import argparse
import numpy
import csv
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import timedelta
import pandas as pd


# In[2]:


#indicamos la web
url_page = 'http://www.bolsamadrid.es/esp/aspx/Mercados/Precios.aspx?indice=ESI100000000'

#introducimos el html en un objeto beautifulSoap
page = requests.get(url_page).text 
soup = BeautifulSoup(page, "lxml")


# In[3]:



#seleccionamos la tabla a partir del Xpath //*[@id="ctl00_Contenido_tblAcciones"] que copiamos con el boton derecho sobre el inspector de html de firefox
tabla = soup.find('table', attrs={'id': "ctl00_Contenido_tblAcciones"})

#tabla2 = soup.find('table', attrs={'id': "ctl00_Contenido_tblÍndice"})


# In[16]:


#creamos una funcion para iterar por los datos que nos interesan
#vemos que el primer nombre esta en /html/body/div[1]/table/tbody/tr[4]/td[2]/div[1]/form/div[6]/table/tbody/tr[2]/td[1]
#y que su precio de cierre está en  /html/body/div[1]/table/tbody/tr[4]/td[2]/div[1]/form/div[6]/table/tbody/tr[2]/td[2]
#y que su volumen  está en          /html/body/div[1]/table/tbody/tr[4]/td[2]/div[1]/form/div[6]/table/tbody/tr[2]/td[6]
#y la fecha de la sesión está en    /html/body/div[1]/table/tbody/tr[4]/td[2]/div[1]/form/div[6]/table/tbody/tr[2]/td[8]


def iteracionTabla(x):
    listado = []
    name=""
    price=""
    vol =""
    date =""
    #creamos un contador para recorrer las filas identificadas en el html con 'tr'
    nroFila=-1
    for fila in tabla.find_all('tr'):
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
                if nroCelda==5:
                    vol=celda.text
                    listado.append(vol)
                if nroCelda==7:
                    date=celda.text
                    listado.append(date)
                nroCelda=nroCelda+1
        nroFila=nroFila+1
    return listado

#anadimos los resultados a una sola lista 
def listadoDiario():
    listadoTotal=[]
    headerList=["Valor","Cierre","Volumen","Fecha"] 
    listadoTotal.append(headerList) 
    #listadoTotal.append(ibexTotal()) 
    for x in range(35):  
        listadoTotal.append(iteracionTabla(x))    
    return listadoTotal

# GM Un solo documento continene las 35 empresasa y la fecha 
listadoDEF = listadoDiario()

# GM Creamos dataset
dataset = pd.DataFrame(listadoDEF)
dataset.to_csv("Dataset2.csv", mode ='a', index = False)