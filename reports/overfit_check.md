# ¿Ventaja o suerte? · pruebas sobre 2023-12-11 a 2026-11-06

R diario de las 18 variantes momentum (0 los días sin operación), stop al precio real del tick y abiertas cerradas a las 24 h. Bootstrap estacionario con bloques de 10 días, 5000 repeticiones, semilla 20261118. La variante del servidor es «momentum pull 5.5 sl 10 min 0».

Cómo leerlo: **p del Reality Check** = probabilidad de ver una mejor variante así de buena si ninguna tuviera ventaja real (menos de 0.05 = difícil de explicar por suerte). **PBO** = de todas las formas de partir la historia en dos mitades, en qué fracción la variante elegida en una mitad queda en la mitad de abajo del ranking en la otra (50 % = elegir no sirve).

## Puntos escalados a la volatilidad · costo extra 0.00 puntos

### Manejo: sin mover el stop

| Tramo | Días | Mejor variante: R total | Mediana de las 18 | p del Reality Check | p conservador | Variante del servidor: R total | IC 95 % | Prob. de total ≤ 0 |
|---|---|---|---|---|---|---|---|---|
| Tres años completos | 751 | +1.7 | -32.5 | 0.865 | 0.878 | -61.6 | -146.9 a +20.3 | 92% |
| Antes de la ventana de selección (hasta 2026-05-10) | 621 | -16.7 | -51.6 | 0.963 | 0.981 | -84.1 | -155.1 a -10.3 | 99% |
| Ventana de selección (desde 2026-05-11) | 130 | +46.5 | +16.7 | 0.002 | 0.002 | +22.5 | -3.1 a +49.6 | 5% |

Variante del servidor por dirección (el oro pasó de unos 1,950 a más de 4,000 en estos tres años, así que comprar con stop ancho y cerrar a las 24 h gana aunque la señal no aporte nada):

| Tramo | Dirección | Días | Operaciones | R total | IC 95 % | Prob. de total ≤ 0 | Abiertas a 24 h | R de las abiertas |
|---|---|---|---|---|---|---|---|---|
| Tres años completos | Compras | 430 | 378 | -35.6 | -90.2 a +19.9 | 89% | 12 | +4.3 |
| Tres años completos | Ventas | 321 | 285 | -26.0 | -85.9 a +35.0 | 79% | 3 | +0.1 |
| Antes de la ventana de selección (hasta 2026-05-10) | Compras | 371 | 325 | -33.7 | -85.7 a +22.0 | 89% | 10 | +3.6 |
| Antes de la ventana de selección (hasta 2026-05-10) | Ventas | 250 | 224 | -50.4 | -96.0 a +2.9 | 97% | 3 | +0.1 |
| Ventana de selección (desde 2026-05-11) | Compras | 59 | 53 | -2.0 | -15.3 a +11.0 | 62% | 2 | +0.7 |
| Ventana de selección (desde 2026-05-11) | Ventas | 71 | 61 | +24.5 | +6.9 a +41.6 | 0% | 0 | +0.0 |

Sobreajuste (CSCV, 16 tramos, 12870 particiones): **PBO 33%**. La variante elegida en la mitad de entrenamiento rinde +0.029 R por día ahí y -0.038 R por día en la otra mitad (la variante mediana rinde -0.043 fuera de muestra); en el 76% de las particiones la elegida pierde fuera de muestra.

### Manejo: stop a entrada a los 10 min

| Tramo | Días | Mejor variante: R total | Mediana de las 18 | p del Reality Check | p conservador | Variante del servidor: R total | IC 95 % | Prob. de total ≤ 0 |
|---|---|---|---|---|---|---|---|---|
| Tres años completos | 751 | -10.0 | -40.6 | 0.959 | 0.985 | -31.3 | -75.2 a +12.8 | 92% |
| Antes de la ventana de selección (hasta 2026-05-10) | 621 | -14.9 | -43.5 | 0.952 | 0.991 | -26.5 | -68.0 a +15.9 | 89% |
| Ventana de selección (desde 2026-05-11) | 130 | +10.1 | -0.2 | 0.433 | 0.433 | -4.8 | -15.7 a +7.2 | 79% |

Sobreajuste (CSCV, 16 tramos, 12870 particiones): **PBO 16%**. La variante elegida en la mitad de entrenamiento rinde -0.003 R por día ahí y -0.038 R por día en la otra mitad (la variante mediana rinde -0.057 fuera de muestra); en el 93% de las particiones la elegida pierde fuera de muestra.

## Puntos escalados a la volatilidad · costo extra 0.30 puntos

### Manejo: sin mover el stop

| Tramo | Días | Mejor variante: R total | Mediana de las 18 | p del Reality Check | p conservador | Variante del servidor: R total | IC 95 % | Prob. de total ≤ 0 |
|---|---|---|---|---|---|---|---|---|
| Tres años completos | 751 | -18.1 | -69.3 | 0.974 | 0.985 | -96.2 | -177.2 a -17.7 | 99% |
| Antes de la ventana de selección (hasta 2026-05-10) | 621 | -38.2 | -89.3 | 0.998 | 0.999 | -112.5 | -179.7 a -44.7 | 100% |
| Ventana de selección (desde 2026-05-11) | 130 | +43.1 | +14.1 | 0.017 | 0.017 | +16.3 | -9.4 a +43.6 | 12% |

Variante del servidor por dirección (el oro pasó de unos 1,950 a más de 4,000 en estos tres años, así que comprar con stop ancho y cerrar a las 24 h gana aunque la señal no aporte nada):

| Tramo | Dirección | Días | Operaciones | R total | IC 95 % | Prob. de total ≤ 0 | Abiertas a 24 h | R de las abiertas |
|---|---|---|---|---|---|---|---|---|
| Tres años completos | Compras | 430 | 375 | -53.8 | -102.8 a -4.4 | 98% | 10 | +2.7 |
| Tres años completos | Ventas | 321 | 279 | -42.5 | -101.1 a +17.8 | 92% | 2 | +0.2 |
| Antes de la ventana de selección (hasta 2026-05-10) | Compras | 371 | 322 | -48.4 | -95.9 a +1.1 | 97% | 8 | +2.0 |
| Antes de la ventana de selección (hasta 2026-05-10) | Ventas | 250 | 219 | -64.1 | -106.5 a -15.1 | 100% | 2 | +0.2 |
| Ventana de selección (desde 2026-05-11) | Compras | 59 | 53 | -5.4 | -18.7 a +8.1 | 79% | 2 | +0.7 |
| Ventana de selección (desde 2026-05-11) | Ventas | 71 | 60 | +21.6 | +3.0 a +40.0 | 1% | 0 | +0.0 |

Sobreajuste (CSCV, 16 tramos, 12870 particiones): **PBO 26%**. La variante elegida en la mitad de entrenamiento rinde -0.007 R por día ahí y -0.171 R por día en la otra mitad (la variante mediana rinde -0.095 fuera de muestra); en el 92% de las particiones la elegida pierde fuera de muestra.

### Manejo: stop a entrada a los 10 min

| Tramo | Días | Mejor variante: R total | Mediana de las 18 | p del Reality Check | p conservador | Variante del servidor: R total | IC 95 % | Prob. de total ≤ 0 |
|---|---|---|---|---|---|---|---|---|
| Tres años completos | 751 | -21.1 | -80.3 | 0.985 | 0.999 | -81.7 | -122.7 a -40.9 | 100% |
| Antes de la ventana de selección (hasta 2026-05-10) | 621 | -33.8 | -73.1 | 0.994 | 0.999 | -72.5 | -111.7 a -32.2 | 100% |
| Ventana de selección (desde 2026-05-11) | 130 | +12.7 | -4.9 | 0.229 | 0.245 | -9.2 | -20.3 a +2.1 | 94% |

Sobreajuste (CSCV, 16 tramos, 12870 particiones): **PBO 11%**. La variante elegida en la mitad de entrenamiento rinde -0.024 R por día ahí y -0.051 R por día en la otra mitad (la variante mediana rinde -0.103 fuera de muestra); en el 93% de las particiones la elegida pierde fuera de muestra.

## Puntos fijos (la regla tal como corre hoy) · costo extra 0.00 puntos

### Manejo: sin mover el stop

| Tramo | Días | Mejor variante: R total | Mediana de las 18 | p del Reality Check | p conservador | Variante del servidor: R total | IC 95 % | Prob. de total ≤ 0 |
|---|---|---|---|---|---|---|---|---|
| Tres años completos | 751 | +91.6 | +53.1 | 0.042 | 0.042 | +76.2 | +0.0 a +152.9 | 2% |
| Antes de la ventana de selección (hasta 2026-05-10) | 621 | +56.6 | +30.4 | 0.199 | 0.199 | +34.0 | -33.4 a +101.3 | 16% |
| Ventana de selección (desde 2026-05-11) | 130 | +42.2 | +26.6 | 0.034 | 0.034 | +42.2 | +14.3 a +69.0 | 0% |

Variante del servidor por dirección (el oro pasó de unos 1,950 a más de 4,000 en estos tres años, así que comprar con stop ancho y cerrar a las 24 h gana aunque la señal no aporte nada):

| Tramo | Dirección | Días | Operaciones | R total | IC 95 % | Prob. de total ≤ 0 | Abiertas a 24 h | R de las abiertas |
|---|---|---|---|---|---|---|---|---|
| Tres años completos | Compras | 430 | 332 | +66.0 | +18.7 a +114.2 | 0% | 87 | +58.6 |
| Tres años completos | Ventas | 321 | 265 | +10.1 | -45.1 a +68.6 | 36% | 49 | +22.0 |
| Antes de la ventana de selección (hasta 2026-05-10) | Compras | 371 | 279 | +61.1 | +16.3 a +108.6 | 0% | 85 | +57.9 |
| Antes de la ventana de selección (hasta 2026-05-10) | Ventas | 250 | 203 | -27.1 | -62.0 a +7.4 | 93% | 49 | +22.0 |
| Ventana de selección (desde 2026-05-11) | Compras | 59 | 53 | +4.9 | -6.0 a +15.7 | 18% | 2 | +0.6 |
| Ventana de selección (desde 2026-05-11) | Ventas | 71 | 62 | +37.2 | +16.8 a +56.4 | 0% | 0 | +0.0 |

Sobreajuste (CSCV, 16 tramos, 12870 particiones): **PBO 50%**. La variante elegida en la mitad de entrenamiento rinde +0.134 R por día ahí y +0.071 R por día en la otra mitad (la variante mediana rinde +0.075 fuera de muestra); en el 11% de las particiones la elegida pierde fuera de muestra.

### Manejo: stop a entrada a los 10 min

| Tramo | Días | Mejor variante: R total | Mediana de las 18 | p del Reality Check | p conservador | Variante del servidor: R total | IC 95 % | Prob. de total ≤ 0 |
|---|---|---|---|---|---|---|---|---|
| Tres años completos | 751 | +13.4 | -3.5 | 0.674 | 0.681 | -2.0 | -32.8 a +30.3 | 56% |
| Antes de la ventana de selección (hasta 2026-05-10) | 621 | +9.7 | +1.7 | 0.739 | 0.746 | +4.4 | -24.1 a +34.3 | 38% |
| Ventana de selección (desde 2026-05-11) | 130 | +8.4 | -1.2 | 0.296 | 0.343 | -6.4 | -17.3 a +4.9 | 87% |

Sobreajuste (CSCV, 16 tramos, 12870 particiones): **PBO 66%**. La variante elegida en la mitad de entrenamiento rinde +0.034 R por día ahí y -0.014 R por día en la otra mitad (la variante mediana rinde -0.004 fuera de muestra); en el 75% de las particiones la elegida pierde fuera de muestra.

## Puntos fijos (la regla tal como corre hoy) · costo extra 0.30 puntos

### Manejo: sin mover el stop

| Tramo | Días | Mejor variante: R total | Mediana de las 18 | p del Reality Check | p conservador | Variante del servidor: R total | IC 95 % | Prob. de total ≤ 0 |
|---|---|---|---|---|---|---|---|---|
| Tres años completos | 751 | +66.8 | +41.4 | 0.136 | 0.136 | +66.8 | -11.3 a +144.0 | 5% |
| Antes de la ventana de selección (hasta 2026-05-10) | 621 | +25.5 | +19.6 | 0.511 | 0.511 | +24.7 | -43.3 a +92.4 | 23% |
| Ventana de selección (desde 2026-05-11) | 130 | +42.2 | +19.8 | 0.028 | 0.028 | +42.2 | +14.4 a +69.0 | 0% |

Variante del servidor por dirección (el oro pasó de unos 1,950 a más de 4,000 en estos tres años, así que comprar con stop ancho y cerrar a las 24 h gana aunque la señal no aporte nada):

| Tramo | Dirección | Días | Operaciones | R total | IC 95 % | Prob. de total ≤ 0 | Abiertas a 24 h | R de las abiertas |
|---|---|---|---|---|---|---|---|---|
| Tres años completos | Compras | 430 | 331 | +58.6 | +11.1 a +107.0 | 1% | 87 | +57.5 |
| Tres años completos | Ventas | 321 | 263 | +8.2 | -47.5 a +67.2 | 39% | 46 | +21.4 |
| Antes de la ventana de selección (hasta 2026-05-10) | Compras | 371 | 278 | +53.8 | +9.6 a +100.4 | 1% | 85 | +56.9 |
| Antes de la ventana de selección (hasta 2026-05-10) | Ventas | 250 | 201 | -29.1 | -63.8 a +5.7 | 95% | 46 | +21.4 |
| Ventana de selección (desde 2026-05-11) | Compras | 59 | 53 | +4.8 | -6.1 a +15.5 | 18% | 2 | +0.6 |
| Ventana de selección (desde 2026-05-11) | Ventas | 71 | 62 | +37.3 | +16.9 a +56.5 | 0% | 0 | +0.0 |

Sobreajuste (CSCV, 16 tramos, 12870 particiones): **PBO 61%**. La variante elegida en la mitad de entrenamiento rinde +0.109 R por día ahí y +0.041 R por día en la otra mitad (la variante mediana rinde +0.052 fuera de muestra); en el 20% de las particiones la elegida pierde fuera de muestra.

### Manejo: stop a entrada a los 10 min

| Tramo | Días | Mejor variante: R total | Mediana de las 18 | p del Reality Check | p conservador | Variante del servidor: R total | IC 95 % | Prob. de total ≤ 0 |
|---|---|---|---|---|---|---|---|---|
| Tres años completos | 751 | +1.1 | -21.7 | 0.949 | 0.957 | -15.2 | -45.1 a +16.8 | 83% |
| Antes de la ventana de selección (hasta 2026-05-10) | 621 | +2.2 | -14.5 | 0.892 | 0.913 | -8.8 | -36.1 a +20.0 | 73% |
| Ventana de selección (desde 2026-05-11) | 130 | +6.5 | -2.1 | 0.537 | 0.576 | -6.4 | -17.8 a +5.2 | 86% |

Sobreajuste (CSCV, 16 tramos, 12870 particiones): **PBO 40%**. La variante elegida en la mitad de entrenamiento rinde +0.013 R por día ahí y -0.024 R por día en la otra mitad (la variante mediana rinde -0.025 fuera de muestra); en el 86% de las particiones la elegida pierde fuera de muestra.

## Agente · cuántas señales hacen falta

Replay del agente (2026-09-01 a 2026-10-30): 37 señales emitidas en 44 días hábiles, 32 cerradas (11 ganadas, 21 perdidas), +7.63 R en total. Media +0.239 R por señal cerrada, desviación 1.74 R. IC 95 % de la media (bootstrap): -0.33 a +0.84 R; probabilidad de que la media real sea ≤ 0: 21%.

Señales cerradas necesarias para distinguir de cero una ventaja real dada (prueba de una cola al 5 %, 80 % de probabilidad de detectarla), con esa desviación y a 15.3 señales cerradas por mes:

| Ventaja real por señal | Señales cerradas | Meses |
|---|---|---|
| +0.24 R (la observada en el replay) | 330 | 22 |
| +0.10 R | 1877 | 123 |
| +0.20 R | 469 | 31 |
| +0.30 R | 209 | 14 |
| +0.50 R | 75 | 5 |

