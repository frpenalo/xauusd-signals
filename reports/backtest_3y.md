# Backtest mecánico XAUUSD por año · 2023-11-13 a 2026-11-06

Corte a las 7:00 AM ET, TP a 1R/2R/3R, posición completa sin BE. Las columnas desde «Resueltas» son la variante que corre en el servidor (momentum pull 5.5 sl 10 min 0). «Resueltas» = TP3 o stop dentro de 24 h; las que seguían abiertas a las 24 h se cierran a precio de mercado y se suman en «R total».

Factor de escala por tramo (rango diario medio de 20 días / 95.5 puntos del periodo de referencia 2026-05-11 a 2026-11-06): 2023-11-13 a 2024-11-12: 0.33 medio, 0.19 a 0.48; 2024-11-13 a 2025-11-12: 0.56 medio, 0.29 a 1.26; 2025-11-13 a 2026-11-06: 1.18 medio, 0.62 a 2.57.

## Puntos fijos (la regla tal como corre hoy)

Retroceso, zona y stop en los mismos puntos todos los años.

| Tramo | Días | Momentum en positivo | Mediana momentum | Resueltas | Gana | Pierde | % acierto | R resueltas | Abiertas a 24 h | R de las abiertas | R total | R/señal | Peor racha | Drawdown máx |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2023-11-13 a 2024-11-12 | 239 | 18/18 | +15.4 | 87 | 15 | 72 | 17% | -33.6 | 83 | +43.4 | +9.8 | +0.06 | 17 | 37.7R |
| 2024-11-13 a 2025-11-12 | 258 | 18/18 | +26.1 | 150 | 40 | 110 | 27% | -7.4 | 50 | +36.7 | +29.2 | +0.15 | 17 | 38.1R |
| 2025-11-13 a 2026-11-06 | 254 | 17/18 | +24.9 | 224 | 75 | 149 | 33% | +44.7 | 3 | +0.5 | +45.3 | +0.20 | 20 | 28.5R |
| Total | 751 | 18/18 | +65.2 | 461 | 130 | 331 | 28% | +3.7 | 136 | +80.6 | +84.3 | +0.14 | 20 | 65.4R |

## Puntos escalados a la volatilidad

Los mismos parámetros multiplicados por el factor de escala de cada día.

| Tramo | Días | Momentum en positivo | Mediana momentum | Resueltas | Gana | Pierde | % acierto | R resueltas | Abiertas a 24 h | R de las abiertas | R total | R/señal | Peor racha | Drawdown máx |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2023-11-13 a 2024-11-12 | 239 | 0/18 | -29.0 | 209 | 42 | 167 | 20% | -58.6 | 3 | +0.1 | -58.5 | -0.28 | 16 | 67.6R |
| 2024-11-13 a 2025-11-12 | 258 | 5/18 | -8.9 | 222 | 60 | 162 | 27% | -8.1 | 6 | +1.4 | -6.7 | -0.03 | 13 | 23.8R |
| 2025-11-13 a 2026-11-06 | 254 | 18/18 | +24.1 | 217 | 65 | 152 | 30% | +15.3 | 6 | +2.9 | +18.2 | +0.08 | 20 | 27.0R |
| Total | 751 | 5/18 | -14.4 | 648 | 167 | 481 | 26% | -51.5 | 15 | +4.4 | -47.0 | -0.07 | 20 | 95.4R |

## Detalle fijo · solo resueltas

239 días hábiles con mercado al corte (7:00 AM ET). Zona de 3 puntos; TP a 1R/2R/3R. R = resultado en múltiplos del riesgo, posición completa sin BE salvo donde se indica.

| Variante | Señales | Llenadas | Gana | Pierde | % acierto | R total | R/señal | R tercios | R BE10 | R BE tras TP1 | Peor racha | Drawdown máx |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| momentum pull 8 sl 6 min 10 | 79 | 35 | 12 | 23 | 34% | +5.8 | +0.16 | +2.7 | +2.3 | +9.1 | 9 | 9.7R |
| momentum pull 8 sl 10 min 10 | 79 | 20 | 7 | 13 | 35% | +5.2 | +0.26 | +0.7 | +2.5 | +3.1 | 5 | 5.0R |
| momentum pull 8 sl 8 min 10 | 79 | 32 | 10 | 22 | 31% | +3.1 | +0.10 | -1.3 | +2.5 | +1.7 | 8 | 8.5R |
| momentum pull 5.5 sl 8 min 10 | 79 | 36 | 11 | 25 | 31% | +2.3 | +0.06 | -1.8 | +0.0 | -4.7 | 10 | 10.0R |
| momentum pull 5.5 sl 6 min 10 | 79 | 45 | 14 | 31 | 31% | +2.0 | +0.04 | +0.0 | +6.1 | +3.2 | 8 | 10.7R |
| momentum pull 3 sl 10 min 10 | 79 | 38 | 10 | 28 | 26% | -2.5 | -0.06 | -9.6 | +0.0 | -4.6 | 12 | 12.5R |
| momentum pull 5.5 sl 10 min 10 | 79 | 31 | 8 | 23 | 26% | -2.5 | -0.08 | -6.1 | +0.0 | -4.2 | 11 | 11.0R |
| momentum pull 3 sl 6 min 10 | 79 | 54 | 15 | 39 | 28% | -3.7 | -0.07 | -2.3 | +2.3 | -1.2 | 11 | 11.7R |
| momentum pull 8 sl 8 min 0 | 239 | 88 | 22 | 66 | 25% | -5.1 | -0.06 | -15.0 | +16.9 | -0.5 | 12 | 12.0R |
| contra pull 8 sl 6 min 10 | 79 | 37 | 9 | 28 | 24% | -6.7 | -0.18 | -7.2 | -0.2 | -10.6 | 8 | 12.9R |
| momentum pull 3 sl 8 min 10 | 79 | 45 | 11 | 34 | 24% | -6.8 | -0.15 | -8.3 | +2.5 | +4.7 | 14 | 14.0R |
| momentum pull 8 sl 10 min 0 | 239 | 68 | 15 | 53 | 22% | -9.7 | -0.14 | -16.8 | +16.9 | -6.4 | 14 | 17.5R |
| momentum pull 5.5 sl 6 min 0 | 239 | 125 | 34 | 91 | 27% | -10.6 | -0.09 | -20.8 | +9.1 | -14.3 | 8 | 21.5R |
| momentum pull 8 sl 6 min 0 | 239 | 96 | 24 | 72 | 25% | -14.7 | -0.15 | -16.3 | +2.6 | -4.8 | 12 | 20.3R |
| momentum pull 5.5 sl 8 min 0 | 239 | 102 | 24 | 78 | 24% | -18.5 | -0.18 | -27.2 | +2.5 | -30.2 | 17 | 29.2R |
| contra pull 8 sl 8 min 10 | 79 | 30 | 3 | 27 | 10% | -19.5 | -0.65 | -15.4 | -0.4 | -17.4 | 19 | 19.5R |
| contra pull 5.5 sl 6 min 10 | 79 | 47 | 8 | 39 | 17% | -20.0 | -0.43 | -16.9 | -0.5 | -16.4 | 15 | 23.9R |
| momentum pull 3 sl 6 min 0 | 239 | 152 | 39 | 113 | 26% | -21.4 | -0.14 | -28.4 | +2.0 | -12.6 | 12 | 27.4R |
| contra pull 8 sl 10 min 10 | 79 | 26 | 1 | 25 | 4% | -22.5 | -0.86 | -20.4 | -1.0 | -20.0 | 17 | 22.5R |
| contra pull 8 sl 6 min 0 | 239 | 103 | 23 | 80 | 22% | -23.9 | -0.23 | -27.7 | +8.1 | -19.6 | 21 | 37.9R |
| contra pull 5.5 sl 8 min 10 | 79 | 35 | 3 | 32 | 9% | -24.2 | -0.69 | -21.1 | +1.6 | -19.9 | 15 | 24.2R |
| contra pull 5.5 sl 10 min 10 | 79 | 33 | 2 | 31 | 6% | -25.7 | -0.78 | -23.9 | +1.6 | -22.4 | 22 | 25.7R |
| contra pull 5.5 sl 6 min 0 | 239 | 132 | 31 | 101 | 23% | -27.8 | -0.21 | -35.1 | +16.8 | -18.2 | 19 | 42.9R |
| momentum pull 3 sl 8 min 0 | 239 | 128 | 28 | 100 | 22% | -30.9 | -0.24 | -37.0 | +4.4 | -13.8 | 17 | 38.2R |
| contra pull 3 sl 6 min 10 | 79 | 57 | 7 | 50 | 12% | -32.8 | -0.58 | -24.5 | +1.1 | -16.5 | 25 | 32.8R |
| contra pull 3 sl 10 min 10 | 79 | 41 | 2 | 39 | 5% | -33.4 | -0.81 | -28.4 | +2.1 | -23.4 | 31 | 33.4R |
| momentum pull 5.5 sl 10 min 0 | 239 | 87 | 15 | 72 | 17% | -33.6 | -0.39 | -38.6 | -2.5 | -32.8 | 17 | 37.7R |
| contra pull 3 sl 8 min 10 | 79 | 49 | 4 | 45 | 8% | -34.5 | -0.70 | -28.8 | +1.1 | -21.5 | 22 | 34.5R |
| momentum pull 3 sl 10 min 0 | 239 | 106 | 20 | 86 | 19% | -35.0 | -0.33 | -43.0 | +3.1 | -30.6 | 17 | 42.7R |
| contra pull 5.5 sl 8 min 0 | 239 | 110 | 20 | 90 | 18% | -40.1 | -0.36 | -43.1 | +11.1 | -31.1 | 22 | 41.9R |
| contra pull 3 sl 6 min 0 | 239 | 166 | 37 | 129 | 22% | -41.2 | -0.25 | -43.5 | +5.7 | -23.7 | 20 | 46.8R |
| contra pull 8 sl 8 min 0 | 239 | 88 | 13 | 75 | 15% | -41.5 | -0.47 | -40.0 | +6.6 | -34.0 | 18 | 44.6R |
| contra pull 8 sl 10 min 0 | 239 | 73 | 8 | 65 | 11% | -44.5 | -0.61 | -45.1 | +4.6 | -38.7 | 25 | 44.5R |
| contra pull 3 sl 8 min 0 | 239 | 141 | 26 | 115 | 18% | -50.2 | -0.36 | -52.6 | +4.5 | -28.6 | 21 | 52.0R |
| contra pull 5.5 sl 10 min 0 | 239 | 93 | 11 | 82 | 12% | -53.6 | -0.58 | -54.0 | +7.4 | -48.4 | 20 | 53.6R |
| contra pull 3 sl 10 min 0 | 239 | 114 | 13 | 101 | 11% | -67.3 | -0.59 | -65.8 | +1.7 | -50.8 | 29 | 67.4R |

Mediana de R total entre las 36 variantes: -21.4. Con 36 variantes probadas, la mejor fila siempre luce bien por azar: lo que cuenta es si la mayoría está por encima de cero.

## Detalle fijo · solo resueltas

258 días hábiles con mercado al corte (7:00 AM ET). Zona de 3 puntos; TP a 1R/2R/3R. R = resultado en múltiplos del riesgo, posición completa sin BE salvo donde se indica.

| Variante | Señales | Llenadas | Gana | Pierde | % acierto | R total | R/señal | R tercios | R BE10 | R BE tras TP1 | Peor racha | Drawdown máx |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| momentum pull 3 sl 6 min 0 | 258 | 216 | 75 | 141 | 35% | +36.3 | +0.17 | +11.0 | +33.7 | +6.0 | 11 | 24.3R |
| momentum pull 3 sl 6 min 10 | 157 | 136 | 49 | 87 | 36% | +28.7 | +0.21 | +12.5 | +27.7 | +10.0 | 12 | 18.5R |
| momentum pull 3 sl 8 min 0 | 258 | 198 | 62 | 136 | 31% | +17.7 | +0.09 | -5.5 | +28.2 | +0.9 | 16 | 21.1R |
| momentum pull 5.5 sl 6 min 0 | 258 | 182 | 58 | 124 | 32% | +13.2 | +0.07 | -2.4 | +21.2 | +3.9 | 16 | 30.4R |
| momentum pull 8 sl 8 min 0 | 258 | 146 | 45 | 101 | 31% | +10.8 | +0.07 | -2.5 | +4.5 | +22.0 | 15 | 16.1R |
| momentum pull 3 sl 8 min 10 | 157 | 126 | 39 | 87 | 31% | +9.6 | +0.08 | +0.4 | +24.2 | +6.3 | 14 | 21.2R |
| momentum pull 8 sl 6 min 0 | 258 | 153 | 47 | 106 | 31% | +5.4 | +0.04 | -2.4 | +2.0 | +14.0 | 15 | 18.6R |
| momentum pull 5.5 sl 6 min 10 | 157 | 116 | 36 | 80 | 31% | +5.1 | +0.04 | -2.1 | +12.5 | -7.3 | 10 | 21.5R |
| momentum pull 8 sl 10 min 10 | 157 | 86 | 25 | 61 | 29% | +3.2 | +0.04 | -6.0 | +7.8 | +6.4 | 17 | 19.2R |
| momentum pull 8 sl 8 min 10 | 157 | 96 | 28 | 68 | 29% | +1.7 | +0.02 | -5.0 | +7.8 | +14.8 | 9 | 15.6R |
| momentum pull 3 sl 10 min 10 | 157 | 113 | 32 | 81 | 28% | +0.9 | +0.01 | -10.6 | +15.0 | -14.4 | 13 | 20.3R |
| momentum pull 8 sl 6 min 10 | 157 | 98 | 29 | 69 | 30% | -0.2 | -0.00 | -4.7 | +3.2 | +5.9 | 9 | 14.3R |
| momentum pull 3 sl 10 min 0 | 258 | 175 | 49 | 126 | 28% | -0.4 | -0.00 | -20.6 | +14.0 | -23.3 | 16 | 23.9R |
| momentum pull 8 sl 10 min 0 | 258 | 129 | 35 | 94 | 27% | -4.2 | -0.03 | -18.7 | +5.5 | -2.6 | 15 | 28.1R |
| momentum pull 5.5 sl 10 min 10 | 157 | 99 | 26 | 73 | 26% | -6.4 | -0.06 | -12.3 | +8.3 | -12.1 | 18 | 26.3R |
| momentum pull 5.5 sl 10 min 0 | 258 | 150 | 40 | 110 | 27% | -7.4 | -0.05 | -17.8 | +15.5 | -9.2 | 17 | 38.1R |
| momentum pull 5.5 sl 8 min 10 | 157 | 105 | 27 | 78 | 26% | -10.9 | -0.10 | -11.5 | +5.9 | -17.1 | 18 | 28.1R |
| momentum pull 5.5 sl 8 min 0 | 258 | 163 | 43 | 120 | 26% | -13.0 | -0.08 | -17.1 | +12.8 | -14.7 | 15 | 34.8R |
| contra pull 8 sl 6 min 10 | 157 | 103 | 23 | 80 | 22% | -25.2 | -0.24 | -19.0 | +5.0 | -5.0 | 12 | 30.2R |
| contra pull 5.5 sl 6 min 10 | 157 | 120 | 28 | 92 | 23% | -25.4 | -0.21 | -26.1 | +4.4 | -28.8 | 17 | 31.4R |
| contra pull 8 sl 8 min 10 | 157 | 96 | 20 | 76 | 21% | -26.0 | -0.27 | -21.4 | +9.9 | -4.7 | 12 | 31.3R |
| contra pull 3 sl 6 min 10 | 157 | 137 | 32 | 105 | 23% | -29.1 | -0.21 | -29.7 | -0.0 | -27.9 | 20 | 44.9R |
| contra pull 8 sl 10 min 10 | 157 | 91 | 17 | 74 | 19% | -30.1 | -0.33 | -24.8 | +10.4 | -8.5 | 10 | 32.6R |
| contra pull 5.5 sl 10 min 10 | 157 | 107 | 21 | 86 | 20% | -31.4 | -0.29 | -28.6 | +3.8 | -23.4 | 13 | 34.6R |
| contra pull 3 sl 10 min 10 | 157 | 119 | 23 | 96 | 19% | -36.8 | -0.31 | -42.5 | +3.7 | -43.6 | 33 | 46.5R |
| contra pull 3 sl 8 min 10 | 157 | 130 | 26 | 104 | 20% | -39.3 | -0.30 | -40.1 | +2.1 | -37.1 | 20 | 48.0R |
| contra pull 5.5 sl 8 min 10 | 157 | 110 | 19 | 91 | 17% | -43.6 | -0.40 | -31.9 | +3.1 | -31.5 | 24 | 46.6R |
| contra pull 8 sl 6 min 0 | 258 | 158 | 33 | 125 | 21% | -46.6 | -0.29 | -35.1 | +7.7 | -16.5 | 21 | 51.6R |
| contra pull 8 sl 8 min 0 | 258 | 145 | 27 | 118 | 19% | -50.6 | -0.35 | -43.1 | +12.9 | -17.9 | 15 | 53.1R |
| contra pull 3 sl 6 min 0 | 258 | 216 | 48 | 168 | 22% | -54.1 | -0.25 | -43.7 | -1.0 | -37.3 | 24 | 72.6R |
| contra pull 3 sl 10 min 0 | 258 | 187 | 37 | 150 | 20% | -54.9 | -0.29 | -61.7 | +2.7 | -48.3 | 33 | 65.0R |
| contra pull 5.5 sl 6 min 0 | 258 | 183 | 37 | 146 | 20% | -57.9 | -0.32 | -46.9 | +5.1 | -45.3 | 36 | 63.1R |
| contra pull 3 sl 8 min 0 | 258 | 205 | 42 | 163 | 20% | -58.6 | -0.29 | -57.6 | +1.1 | -37.5 | 24 | 66.8R |
| contra pull 8 sl 10 min 0 | 258 | 139 | 22 | 117 | 16% | -60.3 | -0.43 | -50.8 | +14.5 | -28.7 | 16 | 62.9R |
| contra pull 5.5 sl 10 min 0 | 258 | 164 | 28 | 136 | 17% | -63.4 | -0.39 | -56.2 | +8.9 | -40.3 | 27 | 66.0R |
| contra pull 5.5 sl 8 min 0 | 258 | 169 | 27 | 142 | 16% | -74.6 | -0.44 | -56.3 | +8.0 | -49.2 | 40 | 77.1R |

Mediana de R total entre las 36 variantes: -13.0. Con 36 variantes probadas, la mejor fila siempre luce bien por azar: lo que cuenta es si la mayoría está por encima de cero.

## Detalle fijo · solo resueltas

254 días hábiles con mercado al corte (7:00 AM ET). Zona de 3 puntos; TP a 1R/2R/3R. R = resultado en múltiplos del riesgo, posición completa sin BE salvo donde se indica.

| Variante | Señales | Llenadas | Gana | Pierde | % acierto | R total | R/señal | R tercios | R BE10 | R BE tras TP1 | Peor racha | Drawdown máx |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| momentum pull 5.5 sl 10 min 0 | 254 | 224 | 75 | 149 | 33% | +44.7 | +0.20 | +23.4 | +27.9 | +23.0 | 20 | 28.5R |
| momentum pull 3 sl 10 min 0 | 254 | 243 | 80 | 163 | 33% | +42.0 | +0.17 | +16.2 | +34.6 | +32.0 | 11 | 23.8R |
| momentum pull 5.5 sl 10 min 10 | 200 | 177 | 60 | 117 | 34% | +38.1 | +0.21 | +20.3 | +23.6 | +12.0 | 14 | 19.5R |
| momentum pull 5.5 sl 8 min 0 | 254 | 226 | 75 | 151 | 33% | +37.1 | +0.16 | +18.1 | +26.2 | +21.5 | 21 | 29.8R |
| momentum pull 3 sl 10 min 10 | 200 | 191 | 62 | 129 | 32% | +29.8 | +0.16 | +9.6 | +21.7 | +11.9 | 9 | 17.4R |
| momentum pull 5.5 sl 8 min 10 | 200 | 178 | 59 | 119 | 33% | +29.1 | +0.16 | +13.7 | +20.6 | +14.0 | 14 | 19.1R |
| momentum pull 3 sl 8 min 0 | 254 | 243 | 78 | 165 | 32% | +28.6 | +0.12 | +11.7 | +31.7 | +23.7 | 11 | 27.9R |
| momentum pull 8 sl 8 min 10 | 200 | 165 | 55 | 110 | 33% | +27.7 | +0.17 | +16.4 | +25.1 | +29.2 | 19 | 23.9R |
| momentum pull 8 sl 6 min 10 | 200 | 165 | 56 | 109 | 34% | +24.9 | +0.15 | +13.7 | +17.8 | +12.6 | 10 | 19.8R |
| momentum pull 8 sl 6 min 0 | 254 | 209 | 69 | 140 | 33% | +24.7 | +0.12 | +14.4 | +17.5 | +2.1 | 13 | 25.4R |
| momentum pull 5.5 sl 6 min 0 | 254 | 227 | 74 | 153 | 33% | +23.9 | +0.11 | +6.5 | +20.0 | -9.0 | 16 | 23.3R |
| momentum pull 8 sl 8 min 0 | 254 | 208 | 66 | 142 | 32% | +23.0 | +0.11 | +13.1 | +26.1 | +25.6 | 24 | 31.9R |
| momentum pull 8 sl 10 min 10 | 200 | 162 | 51 | 111 | 31% | +20.5 | +0.13 | +18.3 | +22.1 | +25.3 | 19 | 23.8R |
| momentum pull 8 sl 10 min 0 | 254 | 205 | 63 | 142 | 31% | +20.2 | +0.10 | +13.7 | +24.3 | +29.0 | 24 | 31.8R |
| momentum pull 3 sl 8 min 10 | 200 | 191 | 59 | 132 | 31% | +14.4 | +0.08 | +4.1 | +21.2 | +7.8 | 9 | 21.3R |
| momentum pull 5.5 sl 6 min 10 | 200 | 179 | 57 | 122 | 32% | +14.3 | +0.08 | +0.4 | +15.4 | -6.9 | 11 | 16.0R |
| momentum pull 3 sl 6 min 0 | 254 | 244 | 74 | 170 | 30% | +5.3 | +0.02 | -11.2 | +27.3 | -11.4 | 11 | 25.2R |
| contra pull 8 sl 8 min 0 | 254 | 209 | 60 | 149 | 29% | +1.5 | +0.01 | +1.9 | +25.7 | +12.1 | 12 | 28.8R |
| momentum pull 3 sl 6 min 10 | 200 | 192 | 57 | 135 | 30% | -0.2 | -0.00 | -13.6 | +12.0 | -16.7 | 10 | 19.1R |
| contra pull 8 sl 6 min 0 | 254 | 209 | 61 | 148 | 29% | -2.1 | -0.01 | -1.1 | +16.8 | +19.0 | 22 | 30.1R |
| contra pull 5.5 sl 6 min 0 | 254 | 221 | 64 | 157 | 29% | -2.7 | -0.01 | -5.0 | +2.5 | +0.2 | 13 | 29.7R |
| contra pull 3 sl 8 min 0 | 254 | 239 | 65 | 174 | 27% | -12.3 | -0.05 | -2.8 | +13.8 | +7.3 | 23 | 34.1R |
| contra pull 8 sl 8 min 10 | 200 | 165 | 43 | 122 | 26% | -13.6 | -0.08 | -4.3 | +13.7 | +2.3 | 18 | 34.8R |
| contra pull 5.5 sl 6 min 10 | 200 | 175 | 47 | 128 | 27% | -14.6 | -0.08 | -14.2 | -0.0 | -10.1 | 17 | 37.0R |
| contra pull 8 sl 6 min 10 | 200 | 165 | 44 | 121 | 27% | -15.3 | -0.09 | -6.5 | +8.8 | +5.2 | 17 | 35.0R |
| contra pull 3 sl 10 min 0 | 254 | 238 | 62 | 176 | 26% | -17.0 | -0.07 | -8.8 | +13.3 | -14.0 | 22 | 43.8R |
| contra pull 5.5 sl 10 min 0 | 254 | 218 | 56 | 162 | 26% | -17.3 | -0.08 | -13.9 | +2.6 | -10.1 | 22 | 48.3R |
| contra pull 3 sl 6 min 0 | 254 | 240 | 64 | 176 | 27% | -24.0 | -0.10 | -9.5 | +8.7 | -7.3 | 19 | 43.6R |
| contra pull 5.5 sl 8 min 0 | 254 | 220 | 56 | 164 | 25% | -24.4 | -0.11 | -14.3 | +4.3 | -1.9 | 22 | 44.7R |
| contra pull 3 sl 10 min 10 | 200 | 188 | 45 | 143 | 24% | -27.5 | -0.15 | -17.0 | +10.2 | -18.0 | 28 | 40.8R |
| contra pull 8 sl 10 min 0 | 254 | 205 | 49 | 156 | 24% | -29.6 | -0.14 | -18.5 | +24.3 | -11.4 | 22 | 56.8R |
| contra pull 3 sl 6 min 10 | 200 | 189 | 47 | 142 | 25% | -30.2 | -0.16 | -15.5 | +5.6 | -18.4 | 18 | 40.3R |
| contra pull 3 sl 8 min 10 | 200 | 188 | 45 | 143 | 24% | -31.0 | -0.16 | -13.7 | +10.9 | -9.1 | 28 | 40.6R |
| contra pull 5.5 sl 10 min 10 | 200 | 172 | 39 | 133 | 23% | -32.2 | -0.19 | -23.1 | +1.5 | -22.3 | 27 | 50.8R |
| contra pull 5.5 sl 8 min 10 | 200 | 174 | 38 | 136 | 22% | -41.6 | -0.24 | -24.4 | +1.8 | -13.8 | 28 | 53.3R |
| contra pull 8 sl 10 min 10 | 200 | 162 | 32 | 130 | 20% | -47.1 | -0.29 | -23.0 | +11.7 | -20.7 | 28 | 61.5R |

Mediana de R total entre las 36 variantes: +1.5. Con 36 variantes probadas, la mejor fila siempre luce bien por azar: lo que cuenta es si la mayoría está por encima de cero.

## Detalle fijo · total · solo resueltas

751 días hábiles con mercado al corte (7:00 AM ET). Zona de 3 puntos; TP a 1R/2R/3R. R = resultado en múltiplos del riesgo, posición completa sin BE salvo donde se indica.

| Variante | Señales | Llenadas | Gana | Pierde | % acierto | R total | R/señal | R tercios | R BE10 | R BE tras TP1 | Peor racha | Drawdown máx |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| momentum pull 8 sl 8 min 10 | 436 | 293 | 93 | 200 | 32% | +32.5 | +0.11 | +10.1 | +35.4 | +45.6 | 19 | 26.0R |
| momentum pull 8 sl 6 min 10 | 436 | 298 | 97 | 201 | 33% | +30.4 | +0.10 | +11.7 | +23.3 | +27.5 | 10 | 19.8R |
| momentum pull 5.5 sl 10 min 10 | 436 | 307 | 94 | 213 | 31% | +29.1 | +0.09 | +1.9 | +31.9 | -4.2 | 18 | 33.6R |
| momentum pull 8 sl 10 min 10 | 436 | 268 | 83 | 185 | 31% | +28.9 | +0.11 | +12.9 | +32.5 | +34.8 | 19 | 27.5R |
| momentum pull 8 sl 8 min 0 | 751 | 442 | 133 | 309 | 30% | +28.8 | +0.07 | -4.4 | +47.4 | +47.2 | 24 | 31.9R |
| momentum pull 3 sl 10 min 10 | 436 | 342 | 104 | 238 | 30% | +28.3 | +0.08 | -10.5 | +36.6 | -7.0 | 13 | 29.6R |
| momentum pull 5.5 sl 6 min 0 | 751 | 534 | 166 | 368 | 31% | +26.5 | +0.05 | -16.6 | +50.4 | -19.4 | 16 | 39.6R |
| momentum pull 3 sl 6 min 10 | 436 | 382 | 121 | 261 | 32% | +24.8 | +0.06 | -3.4 | +42.0 | -8.0 | 12 | 30.3R |
| momentum pull 5.5 sl 6 min 10 | 436 | 340 | 107 | 233 | 31% | +21.5 | +0.06 | -1.7 | +34.0 | -11.0 | 11 | 26.2R |
| momentum pull 5.5 sl 8 min 10 | 436 | 319 | 97 | 222 | 30% | +20.5 | +0.06 | +0.4 | +26.6 | -7.7 | 18 | 39.0R |
| momentum pull 3 sl 6 min 0 | 751 | 612 | 188 | 424 | 31% | +20.2 | +0.03 | -28.5 | +63.0 | -18.0 | 12 | 38.8R |
| momentum pull 3 sl 8 min 10 | 436 | 362 | 109 | 253 | 30% | +17.1 | +0.05 | -3.8 | +47.9 | +18.8 | 14 | 40.0R |
| momentum pull 8 sl 6 min 0 | 751 | 458 | 140 | 318 | 31% | +15.4 | +0.03 | -4.4 | +22.1 | +11.3 | 15 | 30.3R |
| momentum pull 3 sl 8 min 0 | 751 | 569 | 168 | 401 | 30% | +15.4 | +0.03 | -30.8 | +64.3 | +10.8 | 17 | 40.9R |
| momentum pull 3 sl 10 min 0 | 751 | 524 | 149 | 375 | 28% | +6.5 | +0.01 | -47.4 | +51.7 | -22.0 | 17 | 54.1R |
| momentum pull 8 sl 10 min 0 | 751 | 402 | 113 | 289 | 28% | +6.4 | +0.02 | -21.8 | +46.7 | +20.0 | 24 | 43.3R |
| momentum pull 5.5 sl 8 min 0 | 751 | 491 | 142 | 349 | 29% | +5.6 | +0.01 | -26.2 | +41.6 | -23.4 | 21 | 64.0R |
| momentum pull 5.5 sl 10 min 0 | 751 | 461 | 130 | 331 | 28% | +3.7 | +0.01 | -33.0 | +40.9 | -19.0 | 20 | 65.4R |
| contra pull 8 sl 6 min 10 | 436 | 305 | 76 | 229 | 25% | -47.3 | -0.15 | -32.8 | +13.6 | -10.4 | 17 | 60.2R |
| contra pull 8 sl 8 min 10 | 436 | 291 | 66 | 225 | 23% | -59.1 | -0.20 | -41.1 | +23.2 | -19.8 | 19 | 63.5R |
| contra pull 5.5 sl 6 min 10 | 436 | 342 | 83 | 259 | 24% | -60.0 | -0.18 | -57.2 | +3.8 | -55.2 | 17 | 76.0R |
| contra pull 8 sl 6 min 0 | 751 | 470 | 117 | 353 | 25% | -72.6 | -0.15 | -63.9 | +32.6 | -17.2 | 22 | 91.9R |
| contra pull 5.5 sl 6 min 0 | 751 | 536 | 132 | 404 | 25% | -88.5 | -0.17 | -87.0 | +24.4 | -63.4 | 36 | 105.2R |
| contra pull 5.5 sl 10 min 10 | 436 | 312 | 62 | 250 | 20% | -89.3 | -0.29 | -75.7 | +6.9 | -68.1 | 27 | 92.3R |
| contra pull 8 sl 8 min 0 | 751 | 442 | 100 | 342 | 23% | -90.6 | -0.20 | -81.2 | +45.1 | -39.7 | 18 | 100.1R |
| contra pull 3 sl 6 min 10 | 436 | 383 | 86 | 297 | 22% | -92.2 | -0.24 | -69.7 | +6.6 | -62.8 | 25 | 94.9R |
| contra pull 3 sl 10 min 10 | 436 | 348 | 70 | 278 | 20% | -97.7 | -0.28 | -87.8 | +16.0 | -85.0 | 33 | 102.2R |
| contra pull 8 sl 10 min 10 | 436 | 279 | 50 | 229 | 18% | -99.7 | -0.36 | -68.1 | +21.1 | -49.2 | 28 | 99.7R |
| contra pull 3 sl 8 min 10 | 436 | 367 | 75 | 292 | 20% | -104.7 | -0.29 | -82.6 | +14.1 | -67.7 | 28 | 110.0R |
| contra pull 5.5 sl 8 min 10 | 436 | 319 | 60 | 259 | 19% | -109.4 | -0.34 | -77.4 | +6.4 | -65.2 | 28 | 120.7R |
| contra pull 3 sl 6 min 0 | 751 | 622 | 149 | 473 | 24% | -119.3 | -0.19 | -96.6 | +13.3 | -68.2 | 24 | 122.0R |
| contra pull 3 sl 8 min 0 | 751 | 585 | 133 | 452 | 23% | -121.1 | -0.21 | -113.0 | +19.4 | -58.7 | 24 | 127.3R |
| contra pull 5.5 sl 10 min 0 | 751 | 475 | 95 | 380 | 20% | -134.2 | -0.28 | -124.0 | +18.9 | -98.8 | 27 | 137.9R |
| contra pull 8 sl 10 min 0 | 751 | 417 | 79 | 338 | 19% | -134.4 | -0.32 | -114.3 | +43.4 | -78.8 | 25 | 135.5R |
| contra pull 5.5 sl 8 min 0 | 751 | 499 | 103 | 396 | 21% | -139.1 | -0.28 | -113.7 | +23.4 | -82.3 | 40 | 151.3R |
| contra pull 3 sl 10 min 0 | 751 | 539 | 112 | 427 | 21% | -139.2 | -0.26 | -136.3 | +17.7 | -113.1 | 33 | 144.4R |

Mediana de R total entre las 36 variantes: +3.7. Con 36 variantes probadas, la mejor fila siempre luce bien por azar: lo que cuenta es si la mayoría está por encima de cero.

## Detalle escalado · solo resueltas

239 días hábiles con mercado al corte (7:00 AM ET). Zona de 3 puntos; TP a 1R/2R/3R. R = resultado en múltiplos del riesgo, posición completa sin BE salvo donde se indica.

| Variante | Señales | Llenadas | Gana | Pierde | % acierto | R total | R/señal | R tercios | R BE10 | R BE tras TP1 | Peor racha | Drawdown máx |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| momentum pull 5.5 sl 6 min 10 | 185 | 166 | 46 | 120 | 28% | -10.5 | -0.06 | -18.2 | +0.5 | -27.0 | 11 | 33.4R |
| momentum pull 3 sl 8 min 10 | 185 | 177 | 46 | 131 | 26% | -16.1 | -0.09 | -21.4 | +3.7 | -31.8 | 13 | 30.5R |
| momentum pull 3 sl 10 min 10 | 185 | 177 | 45 | 132 | 25% | -16.1 | -0.09 | -17.3 | +5.8 | -21.5 | 15 | 31.8R |
| momentum pull 8 sl 8 min 10 | 185 | 151 | 37 | 114 | 25% | -19.8 | -0.13 | -12.0 | +5.9 | -6.0 | 13 | 26.6R |
| momentum pull 8 sl 6 min 10 | 185 | 152 | 38 | 114 | 25% | -21.0 | -0.14 | -13.3 | +6.6 | -11.2 | 13 | 32.5R |
| momentum pull 3 sl 6 min 10 | 185 | 177 | 46 | 131 | 26% | -21.4 | -0.12 | -30.2 | -6.0 | -34.1 | 11 | 31.3R |
| momentum pull 3 sl 8 min 0 | 239 | 227 | 58 | 169 | 26% | -23.9 | -0.11 | -32.0 | +9.5 | -39.9 | 13 | 39.6R |
| momentum pull 3 sl 10 min 0 | 239 | 227 | 56 | 171 | 25% | -26.6 | -0.12 | -29.1 | +12.8 | -29.6 | 13 | 40.2R |
| momentum pull 5.5 sl 6 min 0 | 239 | 212 | 54 | 158 | 25% | -29.0 | -0.14 | -33.2 | +1.1 | -38.6 | 13 | 50.3R |
| momentum pull 5.5 sl 8 min 10 | 185 | 166 | 39 | 127 | 23% | -29.6 | -0.18 | -19.3 | -3.6 | -21.8 | 13 | 40.0R |
| momentum pull 3 sl 6 min 0 | 239 | 227 | 57 | 170 | 25% | -33.9 | -0.15 | -44.0 | -0.4 | -48.4 | 14 | 45.7R |
| momentum pull 8 sl 8 min 0 | 239 | 194 | 45 | 149 | 23% | -34.8 | -0.18 | -26.4 | +1.0 | -18.4 | 11 | 41.6R |
| momentum pull 8 sl 10 min 10 | 185 | 150 | 31 | 119 | 21% | -37.8 | -0.25 | -27.3 | +10.8 | -15.5 | 13 | 41.3R |
| momentum pull 5.5 sl 10 min 10 | 185 | 163 | 35 | 128 | 21% | -37.9 | -0.23 | -23.4 | -3.6 | -29.2 | 13 | 42.2R |
| momentum pull 8 sl 6 min 0 | 239 | 195 | 45 | 150 | 23% | -40.2 | -0.21 | -27.2 | -0.3 | -23.6 | 12 | 43.8R |
| momentum pull 5.5 sl 8 min 0 | 239 | 212 | 46 | 166 | 22% | -50.8 | -0.24 | -36.8 | -0.7 | -36.9 | 13 | 65.5R |
| momentum pull 8 sl 10 min 0 | 239 | 192 | 39 | 153 | 20% | -51.2 | -0.27 | -36.8 | +9.9 | -28.1 | 13 | 56.8R |
| momentum pull 5.5 sl 10 min 0 | 239 | 209 | 42 | 167 | 20% | -58.6 | -0.28 | -40.3 | -2.2 | -44.1 | 16 | 67.6R |

Mediana de R total entre las 18 variantes: -29.0. Con 18 variantes probadas, la mejor fila siempre luce bien por azar: lo que cuenta es si la mayoría está por encima de cero.

## Detalle escalado · solo resueltas

258 días hábiles con mercado al corte (7:00 AM ET). Zona de 3 puntos; TP a 1R/2R/3R. R = resultado en múltiplos del riesgo, posición completa sin BE salvo donde se indica.

| Variante | Señales | Llenadas | Gana | Pierde | % acierto | R total | R/señal | R tercios | R BE10 | R BE tras TP1 | Peor racha | Drawdown máx |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| momentum pull 8 sl 10 min 10 | 201 | 159 | 46 | 113 | 29% | +6.1 | +0.04 | +4.3 | +11.5 | -3.6 | 13 | 16.6R |
| momentum pull 3 sl 10 min 0 | 258 | 242 | 68 | 174 | 28% | +0.8 | +0.00 | -14.3 | +22.8 | -17.2 | 16 | 22.0R |
| momentum pull 5.5 sl 6 min 10 | 201 | 178 | 53 | 125 | 30% | +0.7 | +0.00 | -5.4 | +4.6 | -11.1 | 16 | 20.4R |
| momentum pull 3 sl 8 min 10 | 201 | 192 | 55 | 137 | 29% | +0.1 | +0.00 | -5.7 | +8.4 | -30.3 | 13 | 15.0R |
| momentum pull 3 sl 10 min 10 | 201 | 190 | 53 | 137 | 28% | -0.7 | -0.00 | -8.1 | +14.5 | -14.0 | 18 | 18.2R |
| momentum pull 5.5 sl 10 min 10 | 201 | 175 | 48 | 127 | 27% | -3.9 | -0.02 | -2.3 | +24.3 | -14.0 | 10 | 19.3R |
| momentum pull 5.5 sl 10 min 0 | 258 | 222 | 60 | 162 | 27% | -8.1 | -0.04 | -9.8 | +29.0 | -14.8 | 13 | 23.8R |
| momentum pull 3 sl 8 min 0 | 258 | 246 | 68 | 178 | 28% | -8.5 | -0.03 | -17.8 | +15.9 | -36.8 | 9 | 19.3R |
| momentum pull 8 sl 10 min 0 | 258 | 200 | 53 | 147 | 26% | -9.9 | -0.05 | -7.9 | +12.1 | -8.1 | 12 | 33.0R |
| momentum pull 8 sl 6 min 10 | 201 | 162 | 44 | 118 | 27% | -12.6 | -0.08 | -11.5 | +16.9 | -10.3 | 13 | 29.4R |
| momentum pull 5.5 sl 8 min 10 | 201 | 177 | 47 | 130 | 27% | -13.3 | -0.08 | -9.4 | +18.2 | -18.0 | 18 | 24.1R |
| momentum pull 5.5 sl 6 min 0 | 258 | 226 | 63 | 163 | 28% | -13.3 | -0.06 | -15.9 | +6.4 | -20.5 | 13 | 25.5R |
| momentum pull 8 sl 8 min 10 | 201 | 159 | 41 | 118 | 26% | -14.2 | -0.09 | -7.6 | +7.3 | -1.3 | 11 | 19.3R |
| momentum pull 8 sl 6 min 0 | 258 | 205 | 55 | 150 | 27% | -18.4 | -0.09 | -11.5 | +16.0 | -15.3 | 13 | 43.8R |
| momentum pull 5.5 sl 8 min 0 | 258 | 224 | 59 | 165 | 26% | -18.4 | -0.08 | -14.5 | +21.8 | -18.0 | 16 | 27.6R |
| momentum pull 3 sl 6 min 10 | 201 | 193 | 49 | 144 | 25% | -27.5 | -0.14 | -18.6 | -9.3 | -26.3 | 14 | 34.4R |
| momentum pull 8 sl 8 min 0 | 258 | 201 | 49 | 152 | 24% | -28.2 | -0.14 | -16.4 | +6.8 | -7.8 | 11 | 34.9R |
| momentum pull 3 sl 6 min 0 | 258 | 248 | 60 | 188 | 24% | -45.3 | -0.18 | -31.6 | -4.3 | -32.1 | 17 | 52.8R |

Mediana de R total entre las 18 variantes: -9.9. Con 18 variantes probadas, la mejor fila siempre luce bien por azar: lo que cuenta es si la mayoría está por encima de cero.

## Detalle escalado · solo resueltas

254 días hábiles con mercado al corte (7:00 AM ET). Zona de 3 puntos; TP a 1R/2R/3R. R = resultado en múltiplos del riesgo, posición completa sin BE salvo donde se indica.

| Variante | Señales | Llenadas | Gana | Pierde | % acierto | R total | R/señal | R tercios | R BE10 | R BE tras TP1 | Peor racha | Drawdown máx |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| momentum pull 8 sl 10 min 10 | 196 | 156 | 55 | 101 | 35% | +40.5 | +0.26 | +25.1 | +39.3 | +37.1 | 17 | 18.8R |
| momentum pull 8 sl 8 min 10 | 196 | 158 | 56 | 102 | 35% | +37.9 | +0.24 | +21.8 | +35.5 | +28.4 | 17 | 19.1R |
| momentum pull 8 sl 10 min 0 | 254 | 198 | 66 | 132 | 33% | +37.8 | +0.19 | +19.5 | +38.9 | +36.6 | 20 | 24.8R |
| momentum pull 5.5 sl 6 min 0 | 254 | 223 | 75 | 148 | 34% | +30.4 | +0.14 | +10.5 | +25.0 | -3.3 | 15 | 16.9R |
| momentum pull 8 sl 8 min 0 | 254 | 201 | 66 | 135 | 33% | +29.9 | +0.15 | +14.7 | +34.4 | +24.9 | 20 | 26.7R |
| momentum pull 5.5 sl 6 min 10 | 196 | 174 | 59 | 115 | 34% | +25.6 | +0.15 | +10.2 | +20.5 | +0.2 | 12 | 13.6R |
| momentum pull 5.5 sl 8 min 10 | 196 | 172 | 56 | 116 | 33% | +24.3 | +0.14 | +10.3 | +23.0 | +7.5 | 16 | 16.9R |
| momentum pull 3 sl 10 min 0 | 254 | 236 | 73 | 163 | 31% | +24.2 | +0.10 | +12.0 | +28.5 | +21.6 | 11 | 22.1R |
| momentum pull 3 sl 8 min 0 | 254 | 241 | 76 | 165 | 32% | +23.9 | +0.10 | +8.2 | +22.8 | +16.2 | 11 | 19.1R |
| momentum pull 5.5 sl 8 min 0 | 254 | 220 | 69 | 151 | 31% | +21.5 | +0.10 | +6.4 | +25.9 | +10.2 | 20 | 23.9R |
| momentum pull 3 sl 10 min 10 | 196 | 182 | 57 | 125 | 31% | +21.0 | +0.12 | +11.2 | +16.6 | +9.5 | 9 | 17.7R |
| momentum pull 5.5 sl 10 min 10 | 196 | 170 | 52 | 118 | 31% | +16.0 | +0.09 | +9.4 | +27.1 | +12.7 | 16 | 20.0R |
| momentum pull 5.5 sl 10 min 0 | 254 | 217 | 65 | 152 | 30% | +15.3 | +0.07 | +6.4 | +30.2 | +12.7 | 20 | 27.0R |
| momentum pull 3 sl 8 min 10 | 196 | 187 | 57 | 130 | 30% | +11.5 | +0.06 | +1.4 | +12.4 | +1.0 | 9 | 14.6R |
| momentum pull 8 sl 6 min 10 | 196 | 159 | 50 | 109 | 31% | +10.6 | +0.07 | +8.7 | +24.3 | +3.0 | 16 | 16.3R |
| momentum pull 3 sl 6 min 0 | 254 | 243 | 75 | 168 | 31% | +9.7 | +0.04 | -7.1 | +22.0 | -1.5 | 11 | 23.3R |
| momentum pull 8 sl 6 min 0 | 254 | 203 | 61 | 142 | 30% | +3.9 | +0.02 | +4.9 | +23.1 | -8.9 | 19 | 25.8R |
| momentum pull 3 sl 6 min 10 | 196 | 187 | 56 | 131 | 30% | +1.5 | +0.01 | -11.1 | +13.2 | -10.3 | 10 | 20.3R |

Mediana de R total entre las 18 variantes: +23.9. Con 18 variantes probadas, la mejor fila siempre luce bien por azar: lo que cuenta es si la mayoría está por encima de cero.

## Detalle escalado · total · solo resueltas

751 días hábiles con mercado al corte (7:00 AM ET). Zona de 3 puntos; TP a 1R/2R/3R. R = resultado en múltiplos del riesgo, posición completa sin BE salvo donde se indica.

| Variante | Señales | Llenadas | Gana | Pierde | % acierto | R total | R/señal | R tercios | R BE10 | R BE tras TP1 | Peor racha | Drawdown máx |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| momentum pull 5.5 sl 6 min 10 | 582 | 518 | 158 | 360 | 31% | +15.9 | +0.03 | -13.4 | +25.6 | -37.8 | 16 | 33.4R |
| momentum pull 8 sl 10 min 10 | 582 | 465 | 132 | 333 | 28% | +8.8 | +0.02 | +2.1 | +61.6 | +18.0 | 17 | 53.8R |
| momentum pull 3 sl 10 min 10 | 582 | 549 | 155 | 394 | 28% | +4.1 | +0.01 | -14.2 | +36.9 | -25.9 | 18 | 39.5R |
| momentum pull 8 sl 8 min 10 | 582 | 468 | 134 | 334 | 29% | +3.9 | +0.01 | +2.2 | +48.8 | +21.1 | 17 | 55.0R |
| momentum pull 3 sl 10 min 0 | 751 | 705 | 197 | 508 | 28% | -1.5 | -0.00 | -31.3 | +64.1 | -25.3 | 16 | 51.5R |
| momentum pull 3 sl 8 min 10 | 582 | 556 | 158 | 398 | 28% | -4.5 | -0.01 | -25.8 | +24.5 | -61.1 | 13 | 38.7R |
| momentum pull 3 sl 8 min 0 | 751 | 714 | 202 | 512 | 28% | -8.5 | -0.01 | -41.7 | +48.3 | -60.6 | 13 | 57.8R |
| momentum pull 5.5 sl 6 min 0 | 751 | 661 | 192 | 469 | 29% | -11.9 | -0.02 | -38.5 | +32.5 | -62.4 | 15 | 60.5R |
| momentum pull 5.5 sl 8 min 10 | 582 | 515 | 142 | 373 | 28% | -18.6 | -0.04 | -18.3 | +37.6 | -32.2 | 18 | 66.3R |
| momentum pull 8 sl 6 min 10 | 582 | 473 | 132 | 341 | 28% | -23.0 | -0.05 | -16.1 | +47.7 | -18.5 | 16 | 49.1R |
| momentum pull 8 sl 10 min 0 | 751 | 590 | 158 | 432 | 27% | -23.3 | -0.04 | -25.1 | +60.9 | +0.4 | 20 | 84.8R |
| momentum pull 5.5 sl 10 min 10 | 582 | 508 | 135 | 373 | 27% | -25.8 | -0.05 | -16.3 | +47.8 | -30.5 | 16 | 62.0R |
| momentum pull 8 sl 8 min 0 | 751 | 596 | 160 | 436 | 27% | -33.1 | -0.06 | -28.1 | +42.2 | -1.3 | 20 | 90.1R |
| momentum pull 3 sl 6 min 10 | 582 | 557 | 151 | 406 | 27% | -47.4 | -0.09 | -59.9 | -2.0 | -70.7 | 14 | 76.4R |
| momentum pull 5.5 sl 8 min 0 | 751 | 656 | 174 | 482 | 27% | -47.7 | -0.07 | -44.9 | +47.0 | -44.7 | 20 | 97.4R |
| momentum pull 5.5 sl 10 min 0 | 751 | 648 | 167 | 481 | 26% | -51.5 | -0.08 | -43.7 | +57.1 | -46.3 | 20 | 95.4R |
| momentum pull 8 sl 6 min 0 | 751 | 603 | 161 | 442 | 27% | -54.7 | -0.09 | -33.7 | +38.8 | -47.8 | 19 | 78.7R |
| momentum pull 3 sl 6 min 0 | 751 | 718 | 192 | 526 | 27% | -69.4 | -0.10 | -82.7 | +17.3 | -82.0 | 17 | 107.0R |

Mediana de R total entre las 18 variantes: -18.6. Con 18 variantes probadas, la mejor fila siempre luce bien por azar: lo que cuenta es si la mayoría está por encima de cero.
