# Carga de paqueterías y limpieza del entorno ####
rm(list = ls())
library("readxl")
library("dplyr")
library("lubridate")
library("xts")
library("scales")
library("ggplot2")
# Carga de datos ####
setwd("C:/Users/behep/Seiton de México/Dirección PITSS - Documentos/Servicio")
# Reporte de "Equipos en contratos vigentes" del Santi
eq.vigentes <- read.csv("ReporteEquiposVigentes.csv")
# Mantener solo las columnas necesarias
eq.vigentes <- eq.vigentes[,c(-(4:7),-10,-(15:22),-(26:27))]
# Reporte de "Tiempos de respuesta" del Santi
tiempos.os <- read.csv("Reporte de tiempos de respuesta.csv")
# Formato de fecha
tiempos.os$Fecha.recepción <- dmy_hm(tiempos.os$Fecha.recepción)
tiempos.os$Fecha.cierre <- dmy_hm(tiempos.os$Fecha.cierre)
tiempos.os$mes <- as.yearmon(tiempos.os$Fecha.recepción)
tiempos.os$fecha <- as.factor(tiempos.os$mes)
  #paste(year(tiempos.os$Fecha.recepción),
  # month(tiempos.os$Fecha.recepción),sep = "-")
tiempos.os1 <- tiempos.os %>% group_by(N..de.serie,mes) %>%
  summarise(TST = sum(TST)) 

tiempos.os2 <- tiempos.os %>% group_by(mes) %>%
  summarise(TST = sum(TST)) 


uptime <- xts((1-(tiempos.os2$TST)/(12501*160))*100,
              order.by = tiempos.os2$mes)
plot(uptime)

# TST <- xts(tiempos.os2$TST, order.by = tiempos.os2$mes)

boxplot_tst <- ggplot(data = tiempos.os, aes(x = fecha,
                                             y = TST))+
  geom_boxplot(fill = "grey80", col = "blue")+
  scale_x_discrete()+ xlab("Mes") + ylab("TST")

