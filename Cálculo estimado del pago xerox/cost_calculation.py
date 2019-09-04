# -*- coding: utf-8 -*-
"""
Created on Thu May  9 13:06:26 2019

@author: aaguilar
"""

import numpy as np
import pandas as pd
condiciones_contrato=pd.read_excel('Condiciones contrato XEROX.xlsx',sheet_name='Matriz global')
familias=condiciones_contrato.iloc[2:,3:13]
familias.index=condiciones_contrato.iloc[2:,2]
familias.columns=condiciones_contrato.iloc[1,3:13]

lista_productos=pd.read_excel('ListaProductos.xlsx',sheet_name='ListaProductosXEROX',index_col=None)
ind=list(map(lambda x:str(x),lista_productos.Modelo))
lista_productos=lista_productos.iloc[:,[0,1,2,3,5,16]]
lista_productos.index=ind

servicios=pd.read_excel('Reporte_Tiempo_respuesta_217317171961880.xlsx',index_col=2)

a=np.unique(list(map(lambda x:str(x),servicios.loc[list(map(lambda x:x not in lista_productos.index,servicios.index))].index)))

servicios=servicios.loc[list(map(lambda x:x in lista_productos.index,servicios.index))]

tiempos_Respuesta=pd.concat([lista_productos.loc[servicios.index],servicios],axis=1)
costos=familias.loc[tiempos_Respuesta['familia matriz global']]
temp=tiempos_Respuesta.drop(['familia matriz global'],axis=1)
ind=tiempos_Respuesta['familia matriz global']
temp.index=ind
temp2=pd.concat([temp,costos],axis=1)
respuesta=temp2.iloc[:,:]
respuesta['familia_matriz_global']=temp2.index
respuesta.index=tiempos_Respuesta.index

data = pd.ExcelFile('PITSS MIF ene a dic 2018.xlsx')
sheet_to_df_map = {}
z=list(map(lambda sheet:data.parse(sheet,index_col=6),data.sheet_names[2:14]))

full_data=z[0][['F_INICIO','Business Team','MES','REQUEST_TY','MODELO', 'EMPLEADO','RESIDENTE/FIJO', 'REGION', 'Dias/Llam',
      'LOC','Loc TR','Rango dias entre servicios', 'Fiabilidad', 'Pago por servicio final','TR Real',
       'TR_OBJ','Monto penalización TR', 'Fecha fin Serv', 'Fecha documentación',
       'Dias documentación', 'Rango documentación', '% penalización TD','TD_Malus','Pago final - penalización']].iloc[:-7,:]
for element in z[1:]:
    full_data=full_data.append(element[['F_INICIO','Business Team','MES','REQUEST_TY','MODELO', 'EMPLEADO','RESIDENTE/FIJO', 'REGION', 'Dias/Llam',
      'LOC','Loc TR','Rango dias entre servicios', 'Fiabilidad', 'Pago por servicio final','TR Real',
       'TR_OBJ','Monto penalización TR', 'Fecha fin Serv', 'Fecha documentación',
       'Dias documentación', 'Rango documentación', '% penalización TD','TD_Malus','Pago final - penalización']].iloc[:-7,:])
#%%

mif_2019=pd.read_excel('PITSS MIF AL 2019.xlsx',sheet_name='DETALLE')
mif_series=mif_2019.SERIE


#%%
t=mif_2019[['F_INICIO','Business Team','MES','REQUEST_TY','MODELO', 'EMPLEADO','RESIDENTE/FIJO', 'REGION', 'Dias/Llam',
      'LOC','Loc TR','Rango dias entre servicios', 'Fiabilidad', 'Pago por servicio final','TR Real',
       'TR_OBJ','Monto penalización TR', 'Fecha fin Serv', 'Fecha documentación',
       'Dias documentación', 'Rango documentación', '% penalización TD','TD_Malus','Pago por servicio final']]
t.columns=['F_INICIO','Business Team','MES','REQUEST_TY','MODELO', 'EMPLEADO','RESIDENTE/FIJO', 'REGION', 'Dias/Llam',
      'LOC','Loc TR','Rango dias entre servicios', 'Fiabilidad', 'Pago por servicio final','TR Real',
       'TR_OBJ','Monto penalización TR', 'Fecha fin Serv', 'Fecha documentación',
       'Dias documentación', 'Rango documentación', '% penalización TD','TD_Malus','Pago final - penalización']
full_data=full_data.append(t)

#%%
temp2=pd.DataFrame(full_data.index,index=full_data['Business Team'],columns=['SERIE'])
temp2=temp2.drop(['Soho Product','CF Mono','3rd Party Equipment & Software'])
#%%
temp=full_data
temp.index=full_data['Business Team']
temp=temp.drop(['Soho Product','CF Mono','3rd Party Equipment & Software'])

full_data_familias=temp2

full_data_cost=familias.loc[full_data_familias.index]

working_data=pd.concat([temp2,full_data_cost,temp],axis=1)
working_data.F_INICIO=pd.to_datetime(working_data.F_INICIO,dayfirst=True)

working_data['NUMBER']=range(len(working_data))

working_data['PAGO_BASE']=list(map(lambda x:working_data['Pago Base CDMX y área metropolitana'][x] if working_data.REGION[x]=='METRO' else working_data['Pago Base Interior'][x],range(len(working_data))))
working_data['DAYS_BETWEEN']=0
#%%
working_data.SERIE[13369:]=mif_series
#%%
def day_calculation(serie):
    temp=working_data.loc[working_data.SERIE==serie].sort_values(by='F_INICIO')
    days=temp.F_INICIO[1:]-temp.F_INICIO[:-1]
    days=list(map(lambda x:x.ceil('D').days,days))
    days.insert(0,temp['Dias/Llam'].iloc[0])
    return pd.DataFrame(days,index=temp.NUMBER)

r=day_calculation(np.unique(working_data.SERIE)[0])
for serie in np.unique(working_data.SERIE)[1:]:
    r=r.append(day_calculation(serie))
#%%    
r=r.sort_index()
working_data.DAYS_BETWEEN=list(r[0])
for num in working_data.loc[working_data.REQUEST_TY=='SR INSTALACION DE EQUIPO']['NUMBER']:
    working_data.iloc[num,37]=' '
    
def pago_fiabilidad(x):
    if working_data.REQUEST_TY[x]=='SR MANTENIMIENTO CORRECTIVO':
        if type(working_data.DAYS_BETWEEN[x])==str:
            r=working_data.PAGO_BASE[x]
        elif working_data.DAYS_BETWEEN[x]<3:
            r=working_data.PAGO_BASE[x]*working_data['menos de 3 días'][x]
        elif working_data.DAYS_BETWEEN[x]<7:
            r=working_data.PAGO_BASE[x]*working_data['entre 3 y 6 días'][x]
        elif working_data.DAYS_BETWEEN[x]<16:
            r=working_data.PAGO_BASE[x]*working_data['entre 7 y 15 días'][x]
        elif working_data.DAYS_BETWEEN[x]<31:
            r=working_data.PAGO_BASE[x]*working_data['entre 16 y 30 días'][x]
        elif working_data.DAYS_BETWEEN[x]<60:
            r=working_data.PAGO_BASE[x]*working_data['entre 31 y 59 días'][x]
        else:
            r=working_data.PAGO_BASE[x]*working_data['60 días o más'][x]
    else:
        r=working_data.PAGO_BASE[x]
    return r
working_data['PAGO_PENALIZACION_FIABILIDAD']=list(map(lambda x:pago_fiabilidad(x),range(len(working_data))))

#%%
t=np.array(list(map(lambda x:len(np.unique(working_data.loc[working_data.SERIE==x]['Loc TR'])),np.unique(working_data.SERIE))))>1
#%%
s=np.unique(working_data.SERIE)[t]
s=np.delete(s,57)
s=np.delete(s,33)
s=np.delete(s,32)
s=np.delete(s,32)
s=np.delete(s,32)
s=np.delete(s,19)
s=np.delete(s,2)
    
error=list(map(lambda x:np.unique(working_data.loc[working_data.SERIE==x]['LOC'])[0],s))

exceptions=pd.DataFrame(['Otras','Otras','Otras','Otras','Otras','Otras','Otras','Otras','Otras','Otras','Otras','Otras','Otras','Otras','Otras'],index=list(np.unique(error)),columns=['LOC TR'])
#%%
def veces_obj(i):
    if not(working_data.SERIE[i] in s):
        r= np.round(working_data['TR Real'][i]/(working_data['TR Ciudades principales'][i]-1),1)if working_data['Loc TR'][i]=='Ciudad principal' else np.round(working_data['TR Real'][i]/(working_data['TR Otras ciudades'][i]-1),1)
    else:
        r= np.round(working_data['TR Real'][i]/(working_data['TR Ciudades principales'][i]-1),1)if exceptions.loc[working_data.LOC[i]][0]=='Ciudad principal' else np.round(working_data['TR Real'][i]//(working_data['TR Otras ciudades'][i]-1),1)
    return r

working_data['VECES_OBJ']=list(map(lambda x: veces_obj(x),range(len(working_data))))

porcentajes=pd.DataFrame(np.arange(0,.525,.025),index=np.round(np.arange(1,3.1,.1),1),columns=['percentage'])
def penalizacion_TR(fila):
    if fila.VECES_OBJ<1:
        result=fila.PAGO_PENALIZACION_FIABILIDAD
    elif fila.VECES_OBJ<3:
        result=fila.PAGO_PENALIZACION_FIABILIDAD-(fila.PAGO_BASE*porcentajes.loc[fila.VECES_OBJ][0])
    else:
        result=fila.PAGO_PENALIZACION_FIABILIDAD-fila.PAGO_BASE
    return result
working_data['PAGO_PENALIZACION_TR']=list(map(lambda x:penalizacion_TR(working_data.iloc[x,:]),range(len(working_data))))
