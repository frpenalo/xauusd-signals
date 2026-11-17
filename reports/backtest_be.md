# Stop a entrada a los 10 minutos, con precios reales y costos · 2023-11-13 a 2026-11-06

Variantes momentum de backtest.py, corte 7:00 AM ET, posición completa, TP3 a 3R. Las abiertas a las 24 h se cierran al último precio. R = múltiplos del riesgo. Cada celda de manejo trae tres números: R de la variante del servidor (momentum pull 5.5 sl 10 min 0), cuántas de las 18 variantes momentum quedan en positivo, y la mediana de R entre ellas.

Días por tramo: 2023-11-13 a 2024-11-12: 239; 2024-11-13 a 2025-11-12: 258; 2025-11-13 a 2026-05-10: 124; 2026-05-11 a 2026-11-06: 130.
Spread de Dukascopy (mediana diaria, promedio del tramo, en puntos): 2023-11-13 a 2024-11-12: 0.37; 2024-11-13 a 2025-11-12: 0.57; 2025-11-13 a 2026-05-10: 0.74; 2026-05-11 a 2026-11-06: 0.61.
Riesgo medio por operación de la variante del servidor (puntos, entrada al stop): 2023-11-13 a 2024-11-12: fijo 11.5, escalado 3.8; 2024-11-13 a 2025-11-12: fijo 11.5, escalado 6.4; 2025-11-13 a 2026-05-10: fijo 11.5, escalado 15.8; 2026-05-11 a 2026-11-06: fijo 11.5, escalado 11.5.

## Puntos escalados a la volatilidad

### Costo extra por operación: 0.00 puntos (solo el spread de Dukascopy)

| Tramo | Operaciones | Sin mover el stop: R servidor | en positivo | mediana | Stop a entrada cuando se puede: R servidor | en positivo | mediana | Cierre a mercado si va perdiendo: R servidor | en positivo | mediana |
|---|---|---|---|---|---|---|---|---|---|---|
| 2023-11-13 a 2024-11-12 | 212 | -65.3 | 0/18 | -36.2 | -30.7 | 0/18 | -24.4 | -29.0 | 0/18 | -24.1 |
| 2024-11-13 a 2025-11-12 | 228 | -10.6 | 1/18 | -13.2 | -5.9 | 0/18 | -18.5 | -5.2 | 0/18 | -15.7 |
| 2025-11-13 a 2026-05-10 | 109 | -8.2 | 8/18 | -1.0 | +10.1 | 10/18 | +4.6 | +8.5 | 9/18 | +2.2 |
| 2026-05-11 a 2026-11-06 | 114 | +22.5 | 18/18 | +17.0 | -4.8 | 8/18 | -0.1 | -6.9 | 5/18 | -3.5 |
| Total | 663 | -61.6 | 1/18 | -30.9 | -31.3 | 0/18 | -40.1 | -32.6 | 0/18 | -42.8 |

### Costo extra por operación: 0.10 puntos

| Tramo | Operaciones | Sin mover el stop: R servidor | en positivo | mediana | Stop a entrada cuando se puede: R servidor | en positivo | mediana | Cierre a mercado si va perdiendo: R servidor | en positivo | mediana |
|---|---|---|---|---|---|---|---|---|---|---|
| 2023-11-13 a 2024-11-12 | 210 | -70.7 | 0/18 | -42.2 | -35.4 | 0/18 | -30.0 | -36.2 | 0/18 | -30.6 |
| 2024-11-13 a 2025-11-12 | 227 | -12.5 | 1/18 | -13.8 | -11.0 | 0/18 | -19.6 | -7.5 | 0/18 | -18.9 |
| 2025-11-13 a 2026-05-10 | 109 | -8.0 | 7/18 | -2.3 | +10.2 | 10/18 | +4.3 | +8.7 | 9/18 | +2.4 |
| 2026-05-11 a 2026-11-06 | 113 | +16.4 | 18/18 | +15.9 | -7.4 | 7/18 | -2.1 | -9.8 | 5/18 | -6.2 |
| Total | 659 | -74.8 | 0/18 | -41.6 | -43.5 | 0/18 | -47.4 | -44.7 | 0/18 | -51.3 |

### Costo extra por operación: 0.20 puntos

| Tramo | Operaciones | Sin mover el stop: R servidor | en positivo | mediana | Stop a entrada cuando se puede: R servidor | en positivo | mediana | Cierre a mercado si va perdiendo: R servidor | en positivo | mediana |
|---|---|---|---|---|---|---|---|---|---|---|
| 2023-11-13 a 2024-11-12 | 209 | -74.7 | 0/18 | -48.5 | -46.9 | 0/18 | -36.3 | -38.4 | 0/18 | -35.0 |
| 2024-11-13 a 2025-11-12 | 226 | -20.3 | 0/18 | -20.3 | -22.1 | 0/18 | -22.1 | -16.4 | 0/18 | -20.6 |
| 2025-11-13 a 2026-05-10 | 109 | -8.0 | 7/18 | -2.4 | +10.1 | 9/18 | +4.1 | +8.7 | 9/18 | +1.7 |
| 2026-05-11 a 2026-11-06 | 113 | +16.3 | 18/18 | +14.4 | -10.9 | 7/18 | -3.4 | -10.9 | 5/18 | -6.8 |
| Total | 657 | -86.6 | 0/18 | -54.8 | -69.8 | 0/18 | -62.8 | -56.9 | 0/18 | -61.6 |

### Costo extra por operación: 0.30 puntos

| Tramo | Operaciones | Sin mover el stop: R servidor | en positivo | mediana | Stop a entrada cuando se puede: R servidor | en positivo | mediana | Cierre a mercado si va perdiendo: R servidor | en positivo | mediana |
|---|---|---|---|---|---|---|---|---|---|---|
| 2023-11-13 a 2024-11-12 | 209 | -76.4 | 0/18 | -54.3 | -50.8 | 0/18 | -43.1 | -44.8 | 0/18 | -42.3 |
| 2024-11-13 a 2025-11-12 | 223 | -28.1 | 0/18 | -23.0 | -30.8 | 0/18 | -24.6 | -25.5 | 0/18 | -25.2 |
| 2025-11-13 a 2026-05-10 | 109 | -8.1 | 6/18 | -2.6 | +9.1 | 9/18 | +1.1 | +8.0 | 8/18 | -1.3 |
| 2026-05-11 a 2026-11-06 | 113 | +16.3 | 17/18 | +14.4 | -9.2 | 6/18 | -4.5 | -11.6 | 4/18 | -7.9 |
| Total | 654 | -96.2 | 0/18 | -68.7 | -81.7 | 0/18 | -79.0 | -74.0 | 0/18 | -74.2 |

### Costo extra por operación: 0.50 puntos

| Tramo | Operaciones | Sin mover el stop: R servidor | en positivo | mediana | Stop a entrada cuando se puede: R servidor | en positivo | mediana | Cierre a mercado si va perdiendo: R servidor | en positivo | mediana |
|---|---|---|---|---|---|---|---|---|---|---|
| 2023-11-13 a 2024-11-12 | 206 | -84.5 | 0/18 | -59.7 | -62.6 | 0/18 | -48.7 | -54.2 | 0/18 | -45.7 |
| 2024-11-13 a 2025-11-12 | 223 | -28.4 | 0/18 | -27.1 | -33.3 | 0/18 | -30.2 | -26.8 | 0/18 | -28.4 |
| 2025-11-13 a 2026-05-10 | 109 | -7.2 | 7/18 | -4.2 | +6.5 | 9/18 | +0.1 | +5.8 | 8/18 | -2.6 |
| 2026-05-11 a 2026-11-06 | 112 | +13.5 | 15/18 | +10.7 | -9.1 | 4/18 | -6.3 | -12.3 | 2/18 | -8.9 |
| Total | 650 | -106.6 | 0/18 | -73.1 | -98.6 | 0/18 | -87.3 | -87.5 | 0/18 | -85.2 |

### Cómo terminan las operaciones de la variante del servidor (total, por costo)

| Costo | Manejo | Operaciones | TP3 | Stop | En entrada | Abiertas a 24 h | R total | R por operación | Drawdown máx |
|---|---|---|---|---|---|---|---|---|---|
| 0.00 | Sin mover el stop | 663 | 167 | 481 | 0 | 15 | -61.6 | -0.093 | 105.3R |
| 0.00 | Stop a entrada cuando se puede | 663 | 43 | 134 | 486 | 0 | -31.3 | -0.047 | 47.8R |
| 0.00 | Cierre a mercado si va perdiendo | 663 | 40 | 46 | 577 | 0 | -32.6 | -0.049 | 46.8R |
| 0.10 | Sin mover el stop | 659 | 162 | 482 | 0 | 15 | -74.8 | -0.113 | 111.5R |
| 0.10 | Stop a entrada cuando se puede | 659 | 41 | 141 | 477 | 0 | -43.5 | -0.066 | 54.9R |
| 0.10 | Cierre a mercado si va perdiendo | 659 | 38 | 48 | 573 | 0 | -44.7 | -0.068 | 54.2R |
| 0.20 | Sin mover el stop | 657 | 159 | 485 | 0 | 13 | -86.6 | -0.132 | 123.1R |
| 0.20 | Stop a entrada cuando se puede | 657 | 36 | 154 | 467 | 0 | -69.8 | -0.106 | 77.6R |
| 0.20 | Cierre a mercado si va perdiendo | 657 | 36 | 50 | 571 | 0 | -56.9 | -0.087 | 65.4R |
| 0.30 | Sin mover el stop | 654 | 156 | 486 | 0 | 12 | -96.2 | -0.147 | 132.4R |
| 0.30 | Stop a entrada cuando se puede | 654 | 34 | 161 | 459 | 0 | -81.7 | -0.125 | 87.7R |
| 0.30 | Cierre a mercado si va perdiendo | 654 | 32 | 51 | 571 | 0 | -74.0 | -0.113 | 78.0R |
| 0.50 | Sin mover el stop | 650 | 152 | 486 | 0 | 12 | -106.6 | -0.164 | 138.0R |
| 0.50 | Stop a entrada cuando se puede | 650 | 32 | 173 | 445 | 0 | -98.6 | -0.152 | 102.9R |
| 0.50 | Cierre a mercado si va perdiendo | 650 | 31 | 54 | 565 | 0 | -87.5 | -0.135 | 89.7R |

### Sensibilidad a los minutos (total; mismas tres cifras por celda)

| Costo | Minutos | Stop a entrada cuando se puede: R servidor | en positivo | mediana | Cierre a mercado si va perdiendo: R servidor | en positivo | mediana |
|---|---|---|---|---|---|---|---|
| 0.00 | 5 | -23.6 | 0/18 | -37.4 | -32.7 | 0/18 | -48.7 |
| 0.00 | 10 | -31.3 | 0/18 | -40.1 | -32.6 | 0/18 | -42.8 |
| 0.00 | 20 | -34.1 | 0/18 | -34.1 | -26.2 | 0/18 | -33.3 |
| 0.10 | 5 | -43.3 | 0/18 | -55.0 | -45.4 | 0/18 | -53.6 |
| 0.10 | 10 | -43.5 | 0/18 | -47.4 | -44.7 | 0/18 | -51.3 |
| 0.10 | 20 | -49.9 | 0/18 | -41.6 | -39.5 | 0/18 | -48.8 |
| 0.20 | 5 | -59.8 | 0/18 | -65.1 | -52.7 | 0/18 | -68.7 |
| 0.20 | 10 | -69.8 | 0/18 | -62.8 | -56.9 | 0/18 | -61.6 |
| 0.20 | 20 | -69.7 | 0/18 | -57.1 | -52.3 | 0/18 | -53.8 |
| 0.30 | 5 | -72.5 | 0/18 | -74.6 | -66.2 | 0/18 | -78.7 |
| 0.30 | 10 | -81.7 | 0/18 | -79.0 | -74.0 | 0/18 | -74.2 |
| 0.30 | 20 | -83.3 | 0/18 | -72.1 | -71.6 | 0/18 | -71.6 |
| 0.50 | 5 | -91.9 | 0/18 | -92.8 | -81.8 | 0/18 | -88.0 |
| 0.50 | 10 | -98.6 | 0/18 | -87.3 | -87.5 | 0/18 | -85.2 |
| 0.50 | 20 | -101.5 | 0/18 | -90.8 | -86.5 | 0/18 | -85.0 |

## Puntos fijos (la regla tal como corre hoy)

### Costo extra por operación: 0.00 puntos (solo el spread de Dukascopy)

| Tramo | Operaciones | Sin mover el stop: R servidor | en positivo | mediana | Stop a entrada cuando se puede: R servidor | en positivo | mediana | Cierre a mercado si va perdiendo: R servidor | en positivo | mediana |
|---|---|---|---|---|---|---|---|---|---|---|
| 2023-11-13 a 2024-11-12 | 170 | +9.1 | 18/18 | +14.0 | -9.6 | 7/18 | -1.3 | -8.7 | 3/18 | -2.9 |
| 2024-11-13 a 2025-11-12 | 200 | +27.2 | 17/18 | +24.1 | +8.7 | 11/18 | +3.7 | +0.7 | 6/18 | -1.8 |
| 2025-11-13 a 2026-05-10 | 112 | -2.3 | 6/18 | -2.5 | +5.2 | 9/18 | +0.6 | +6.2 | 6/18 | -1.0 |
| 2026-05-11 a 2026-11-06 | 115 | +42.2 | 17/18 | +27.2 | -6.4 | 5/18 | -1.2 | -7.9 | 5/18 | -4.4 |
| Total | 597 | +76.2 | 18/18 | +54.1 | -2.0 | 7/18 | -2.0 | -9.7 | 0/18 | -9.7 |

### Costo extra por operación: 0.10 puntos

| Tramo | Operaciones | Sin mover el stop: R servidor | en positivo | mediana | Stop a entrada cuando se puede: R servidor | en positivo | mediana | Cierre a mercado si va perdiendo: R servidor | en positivo | mediana |
|---|---|---|---|---|---|---|---|---|---|---|
| 2023-11-13 a 2024-11-12 | 169 | +8.1 | 17/18 | +13.9 | -9.6 | 7/18 | -1.2 | -8.4 | 3/18 | -3.1 |
| 2024-11-13 a 2025-11-12 | 200 | +27.0 | 17/18 | +17.9 | +5.1 | 8/18 | -1.6 | -0.4 | 3/18 | -4.3 |
| 2025-11-13 a 2026-05-10 | 112 | -6.1 | 1/18 | -3.3 | +5.2 | 8/18 | -0.5 | +5.8 | 5/18 | -1.3 |
| 2026-05-11 a 2026-11-06 | 115 | +42.0 | 17/18 | +27.3 | -5.4 | 5/18 | -2.8 | -8.5 | 3/18 | -4.8 |
| Total | 596 | +70.9 | 18/18 | +50.0 | -4.8 | 4/18 | -6.5 | -11.5 | 0/18 | -14.8 |

### Costo extra por operación: 0.20 puntos

| Tramo | Operaciones | Sin mover el stop: R servidor | en positivo | mediana | Stop a entrada cuando se puede: R servidor | en positivo | mediana | Cierre a mercado si va perdiendo: R servidor | en positivo | mediana |
|---|---|---|---|---|---|---|---|---|---|---|
| 2023-11-13 a 2024-11-12 | 168 | +5.0 | 16/18 | +14.1 | -13.3 | 5/18 | -3.2 | -11.9 | 1/18 | -4.5 |
| 2024-11-13 a 2025-11-12 | 200 | +26.9 | 17/18 | +17.8 | +5.1 | 6/18 | -1.7 | -0.5 | 2/18 | -4.5 |
| 2025-11-13 a 2026-05-10 | 112 | -6.0 | 0/18 | -5.5 | +4.4 | 6/18 | -2.6 | +5.4 | 4/18 | -3.0 |
| 2026-05-11 a 2026-11-06 | 115 | +42.2 | 17/18 | +23.9 | -6.2 | 5/18 | -2.5 | -9.7 | 3/18 | -4.9 |
| Total | 595 | +68.1 | 18/18 | +48.3 | -10.0 | 1/18 | -15.9 | -16.7 | 0/18 | -21.6 |

### Costo extra por operación: 0.30 puntos

| Tramo | Operaciones | Sin mover el stop: R servidor | en positivo | mediana | Stop a entrada cuando se puede: R servidor | en positivo | mediana | Cierre a mercado si va perdiendo: R servidor | en positivo | mediana |
|---|---|---|---|---|---|---|---|---|---|---|
| 2023-11-13 a 2024-11-12 | 167 | +4.3 | 15/18 | +13.1 | -17.1 | 5/18 | -3.2 | -15.5 | 1/18 | -4.9 |
| 2024-11-13 a 2025-11-12 | 200 | +26.6 | 15/18 | +16.8 | +4.0 | 4/18 | -4.5 | -1.6 | 1/18 | -5.9 |
| 2025-11-13 a 2026-05-10 | 112 | -6.2 | 0/18 | -5.9 | +4.3 | 6/18 | -1.7 | +4.7 | 6/18 | -1.5 |
| 2026-05-11 a 2026-11-06 | 115 | +42.2 | 17/18 | +20.3 | -6.4 | 6/18 | -2.0 | -9.6 | 3/18 | -3.8 |
| Total | 594 | +66.8 | 18/18 | +41.7 | -15.2 | 2/18 | -18.5 | -22.1 | 0/18 | -23.4 |

### Costo extra por operación: 0.50 puntos

| Tramo | Operaciones | Sin mover el stop: R servidor | en positivo | mediana | Stop a entrada cuando se puede: R servidor | en positivo | mediana | Cierre a mercado si va perdiendo: R servidor | en positivo | mediana |
|---|---|---|---|---|---|---|---|---|---|---|
| 2023-11-13 a 2024-11-12 | 165 | +1.1 | 14/18 | +11.6 | -18.5 | 3/18 | -3.9 | -19.2 | 1/18 | -5.7 |
| 2024-11-13 a 2025-11-12 | 199 | +23.6 | 15/18 | +16.7 | -1.5 | 1/18 | -6.5 | -5.3 | 0/18 | -8.2 |
| 2025-11-13 a 2026-05-10 | 112 | -5.5 | 0/18 | -7.7 | +4.1 | 6/18 | -4.6 | +4.9 | 4/18 | -6.3 |
| 2026-05-11 a 2026-11-06 | 114 | +39.4 | 16/18 | +20.3 | -8.9 | 5/18 | -2.9 | -12.6 | 4/18 | -5.6 |
| Total | 590 | +58.5 | 17/18 | +29.9 | -24.8 | 0/18 | -24.8 | -32.3 | 0/18 | -31.3 |

### Cómo terminan las operaciones de la variante del servidor (total, por costo)

| Costo | Manejo | Operaciones | TP3 | Stop | En entrada | Abiertas a 24 h | R total | R por operación | Drawdown máx |
|---|---|---|---|---|---|---|---|---|---|
| 0.00 | Sin mover el stop | 597 | 130 | 331 | 0 | 136 | +76.2 | +0.128 | 41.1R |
| 0.00 | Stop a entrada cuando se puede | 597 | 26 | 80 | 477 | 14 | -2.0 | -0.003 | 15.6R |
| 0.00 | Cierre a mercado si va perdiendo | 597 | 24 | 21 | 538 | 14 | -9.7 | -0.016 | 16.9R |
| 0.10 | Sin mover el stop | 596 | 129 | 333 | 0 | 134 | +70.9 | +0.119 | 41.2R |
| 0.10 | Stop a entrada cuando se puede | 596 | 25 | 81 | 475 | 15 | -4.8 | -0.008 | 18.0R |
| 0.10 | Cierre a mercado si va perdiendo | 596 | 24 | 21 | 536 | 15 | -11.5 | -0.019 | 17.9R |
| 0.20 | Sin mover el stop | 595 | 128 | 333 | 0 | 134 | +68.1 | +0.114 | 41.0R |
| 0.20 | Stop a entrada cuando se puede | 595 | 24 | 84 | 472 | 15 | -10.0 | -0.017 | 18.9R |
| 0.20 | Cierre a mercado si va perdiendo | 595 | 23 | 22 | 535 | 15 | -16.7 | -0.028 | 18.9R |
| 0.30 | Sin mover el stop | 594 | 128 | 333 | 0 | 133 | +66.8 | +0.113 | 41.2R |
| 0.30 | Stop a entrada cuando se puede | 594 | 24 | 86 | 471 | 13 | -15.2 | -0.026 | 22.1R |
| 0.30 | Cierre a mercado si va perdiendo | 594 | 23 | 22 | 536 | 13 | -22.1 | -0.037 | 22.6R |
| 0.50 | Sin mover el stop | 590 | 126 | 333 | 0 | 131 | +58.5 | +0.099 | 43.6R |
| 0.50 | Stop a entrada cuando se puede | 590 | 22 | 88 | 469 | 11 | -24.8 | -0.042 | 28.7R |
| 0.50 | Cierre a mercado si va perdiendo | 590 | 21 | 23 | 535 | 11 | -32.3 | -0.055 | 32.3R |

### Sensibilidad a los minutos (total; mismas tres cifras por celda)

| Costo | Minutos | Stop a entrada cuando se puede: R servidor | en positivo | mediana | Cierre a mercado si va perdiendo: R servidor | en positivo | mediana |
|---|---|---|---|---|---|---|---|
| 0.00 | 5 | -4.6 | 4/18 | -4.6 | -5.7 | 1/18 | -13.6 |
| 0.00 | 10 | -2.0 | 7/18 | -2.0 | -9.7 | 0/18 | -9.7 |
| 0.00 | 20 | +9.9 | 12/18 | +6.9 | +2.2 | 7/18 | -2.1 |
| 0.10 | 5 | -4.8 | 1/18 | -8.9 | -7.1 | 0/18 | -19.9 |
| 0.10 | 10 | -4.8 | 4/18 | -6.5 | -11.5 | 0/18 | -14.8 |
| 0.10 | 20 | +7.1 | 9/18 | +1.6 | +0.0 | 7/18 | -5.2 |
| 0.20 | 5 | -7.4 | 1/18 | -16.6 | -10.9 | 0/18 | -24.3 |
| 0.20 | 10 | -10.0 | 1/18 | -15.9 | -16.7 | 0/18 | -21.6 |
| 0.20 | 20 | +2.7 | 8/18 | -4.6 | -5.4 | 6/18 | -9.3 |
| 0.30 | 5 | -9.9 | 1/18 | -19.1 | -15.8 | 0/18 | -26.1 |
| 0.30 | 10 | -15.2 | 2/18 | -18.5 | -22.1 | 0/18 | -23.4 |
| 0.30 | 20 | +0.7 | 8/18 | -3.3 | -7.8 | 6/18 | -7.8 |
| 0.50 | 5 | -21.0 | 0/18 | -23.8 | -29.4 | 0/18 | -33.1 |
| 0.50 | 10 | -24.8 | 0/18 | -24.8 | -32.3 | 0/18 | -31.3 |
| 0.50 | 20 | -12.0 | 4/18 | -12.0 | -22.5 | 3/18 | -22.5 |

## Control contra el simulador viejo (costo 0, salidas al nivel exacto, variante del servidor)

Debe coincidir con reports/backtest_3y.md: resueltas y su R, abiertas y su R, y la columna «R BE10».

| Familia | Tramo | Resueltas | R resueltas | Abiertas a 24 h | R de las abiertas | R BE10 viejo |
|---|---|---|---|---|---|---|
| fijo | 2023-11-13 a 2024-11-12 | 87 | -33.6 | 83 | +43.4 | -2.5 |
| fijo | 2024-11-13 a 2025-11-12 | 150 | -7.4 | 50 | +36.7 | +15.5 |
| fijo | 2025-11-13 a 2026-05-10 | 111 | +0.5 | 1 | -0.1 | +19.6 |
| fijo | 2026-05-11 a 2026-11-06 | 113 | +44.3 | 2 | +0.6 | +8.4 |
| fijo | Total | 461 | +3.7 | 136 | +80.6 | +40.9 |
| escalado | 2023-11-13 a 2024-11-12 | 209 | -58.7 | 3 | +0.1 | -2.2 |
| escalado | 2024-11-13 a 2025-11-12 | 222 | -8.1 | 6 | +1.4 | +29.0 |
| escalado | 2025-11-13 a 2026-05-10 | 105 | -8.5 | 4 | +2.1 | +21.4 |
| escalado | 2026-05-11 a 2026-11-06 | 112 | +23.8 | 2 | +0.7 | +8.8 |
| escalado | Total | 648 | -51.5 | 15 | +4.4 | +57.1 |
