#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
from math import radians, cos, sin, asin, sqrt
from datetime import datetime
import time
import sys


# In[2]:


def haversine(lon1, lat1, lon2, lat2):
     
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 
    return c * r

def is_inside_pois(lat1, lon1, lat2, lon2, radius):

    lat1 = lat1 
    lon1 = lon1 
    lat2 = lat2
    lon2 = lon2 
    radius = radius 

    a = haversine(lon1, lat1, lon2, lat2)

    if a <= radius:
        return True 
    else:
        return False 

def verificar(latitudePosicaoPresente, longitudePosicaoPresente):
    for index2, row2 in base_pois_def.iterrows():
        latitudePOIS= float(row2['latitude'])
        longitudePOIS = float(row2['longitude'])
        radius = row2['raio'] / 1000
        
        a = haversine(longitudePOIS, latitudePOIS, longitudePosicaoPresente, latitudePosicaoPresente)

        if a <= radius:
            return row2['nome']
    return 'NaN'
    
def tempoParadoPOI(df, placa, poi, datainicio):

    newdf = df[(df.velocidade >= 5) & (df.placa == placa) & (df.poi == poi) & (df.ignicao == True) & (df.data_posicao > datainicio)]
    if newdf.first_valid_index() != None:
        return df['data_posicao'].iloc[newdf.first_valid_index()]
    else:
        newdf = df[(df.placa == placa) & (df.poi == poi)]
        return df['data_posicao'].iloc[newdf.last_valid_index()]
    
def DentroPOI(df, placa, poi, datainicio):

    newdf = df[(df.placa == placa) & (df.poi == poi) & (df.data_posicao > datainicio)]
    if newdf.first_valid_index() != None:
        return df['data_posicao'].iloc[newdf.first_valid_index()]
    else:
        newdf = df[(df.placa == placa) & (df.poi == poi)]
        return df['data_posicao'].iloc[newdf.last_valid_index()]
    


# In[3]:


base_pois_def = pd.read_csv('C:/teste/base_pois_def.csv', decimal=",")
posicoes = pd.read_csv('C:/teste/posicoes.csv', decimal=",")


# In[4]:


poi = []
dataformated = []

for index, row in posicoes.iterrows():
    latitudePosicaoPresente = float(row['latitude'])
    longitudePosicaoPresente = float(row['longitude'])
    
    inside = verificar(latitudePosicaoPresente, longitudePosicaoPresente)
    
    poi.append(inside)
    
    dataformatada = row['data_posicao'].replace(' GMT-0200 (Hora oficial do Brasil)', '')
    date_time_obj = datetime.strptime(dataformatada, '%a %b %d %Y %H:%M:%S')
    dataformated.append(date_time_obj)        

posicoes['data_posicao'] = dataformated
posicoes['poi'] = poi
posicoes = posicoes.drop('longitude', 1)
posicoes = posicoes.drop('latitude', 1)
posicoes.sort_values(by=['placa','data_posicao'], inplace=True)
posicoes = posicoes.reset_index(drop=True)


# In[5]:


ultimadata = []
for index, row in posicoes.iterrows():
    ultimadata.append(tempoParadoPOI(posicoes, row['placa'], row['poi'], row['data_posicao']))
    
posicoes['ultimadata'] = ultimadata
veiculosParados = posicoes[(posicoes.velocidade < 5) & (posicoes.ignicao == True)]
veiculosParados['TempoParado'] = ((veiculosParados['ultimadata'] - veiculosParados['data_posicao'])).astype('timedelta64[m]')


# In[6]:


veiculosParadosPoi = veiculosParados.groupby(by=['placa', 'poi', 'ultimadata'])
veiculosParadosPoi = veiculosParadosPoi.apply(lambda g: g[g['data_posicao'] == g['data_posicao'].min()])
veiculosParadosPoi = veiculosParadosPoi.reset_index(drop=True)
veiculosParadosPoi = veiculosParadosPoi.drop(['data_posicao', 'velocidade', 'ignicao', 'ultimadata'], axis=1)
veiculosParadosPoi.groupby(['placa','poi']).sum()
veiculosParadosPoi.to_csv('veiculosParados.csv')


# In[7]:


ultimadata = []
for index, row in posicoes.iterrows():
    ultimadata.append(DentroPOI(posicoes, row['placa'], row['poi'], row['data_posicao']))
    
posicoes['ultimadata'] = ultimadata
veiculosPoi = posicoes[(posicoes.poi != 'NaN')]
veiculosPoi['TempoPOI'] = ((veiculosPoi['ultimadata'] - veiculosPoi['data_posicao'])).astype('timedelta64[m]')


# In[8]:


veiculosDentroPoi = veiculosPoi.groupby(by=['placa', 'poi', 'ultimadata'])
veiculosDentroPoi = veiculosDentroPoi.apply(lambda g: g[g['data_posicao'] == g['data_posicao'].min()])
veiculosDentroPoi = veiculosDentroPoi.reset_index(drop=True)
veiculosDentroPoi = veiculosDentroPoi.drop(['data_posicao', 'velocidade', 'ignicao', 'ultimadata'], axis=1)
veiculosDentroPoi.groupby(['placa','poi']).sum()
veiculosDentroPoi.to_csv('veiculosDentroPoi.csv')


# In[9]:


frotaParadoPoi = veiculosParados.groupby(by=['placa', 'poi', 'ultimadata'])
frotaParadoPoi = frotaParadoPoi.apply(lambda g: g[g['data_posicao'] == g['data_posicao'].min()])
frotaParadoPoi = frotaParadoPoi.reset_index(drop=True)
frotaParadoPoi = frotaParadoPoi.drop(['data_posicao', 'velocidade', 'ignicao', 'ultimadata', 'placa'], axis=1)
frotaParadoPoi.groupby(['poi']).sum()
frotaParadoPoi.to_csv('frotaParadoPoi.csv')


# In[10]:


tempoParadoVeiculo = veiculosParados.groupby(by=['placa', 'poi', 'ultimadata'])
tempoParadoVeiculo = tempoParadoVeiculo.apply(lambda g: g[g['data_posicao'] == g['data_posicao'].min()])
tempoParadoVeiculo = tempoParadoVeiculo.reset_index(drop=True)
tempoParadoVeiculo = tempoParadoVeiculo.drop(['data_posicao', 'velocidade', 'ignicao', 'ultimadata', 'poi'], axis=1)
tempoParadoVeiculo.groupby(['placa']).sum()
tempoParadoVeiculo.to_csv('tempoParadoVeiculo.csv')


# In[ ]:




