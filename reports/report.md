# Verificación de señales XAUUSD contra el mercado

Fuente de precios: ticks bid/ask de Dukascopy (XAUUSD spot). Tracker: `signals_tracker.csv`. Generado 2026-10-29 12:14Z.

## Resumen

- Señales en el tracker: 12. Verificables (dirección + zona + SL + TP): 10. Omitidas: 2.
- Llenadas en el mercado: 10 de 10. Con desenlace cerrado en todos los manejos: 10.
- Reportes del canal contrastados: 7 coinciden, 3 no coinciden, 0 sin verificar.
- Horas con base `eastern_assumed` o `date_only` tienen menos certeza sobre el momento exacto de la señal; `date_only` arranca a las 00:00 UTC del día y puede llenarse antes de que la señal existiera.

## Métricas (solo señales llenadas y cerradas)

| Manejo | n | Gana | Pierde | BE | R total | R prom | R mediana | Payoff | Máx. pérdidas seguidas |
|---|---|---|---|---|---|---|---|---|---|
| Sin break-even, posición completa | 10 | 2 | 8 | 0 | -0.53 | -0.053 | -1.000 | 3.73 | 5 |
| Sin break-even, en tercios | 10 | 2 | 8 | 0 | -2.09 | -0.209 | -1.000 | 2.76 | 5 |
| BE a los 10 min (manejo del canal), posición completa | 10 | 0 | 2 | 8 | -2.00 | -0.200 | +0.000 | n/a | 1 |
| BE a los 10 min (manejo del canal), en tercios | 10 | 1 | 2 | 7 | -0.65 | -0.065 | +0.000 | 1.35 | 1 |
| BE al tocar TP1, posición completa | 10 | 0 | 6 | 4 | -6.00 | -0.600 | -1.000 | n/a | 5 |
| BE al tocar TP1, en tercios | 10 | 4 | 6 | 0 | -3.77 | -0.377 | -1.000 | 0.56 | 5 |

Lectura: R = resultado dividido entre el riesgo (entrada a stop). 'En tercios' cierra un tercio en cada TP y el resto al stop vigente. BE a los 10 min replica lo que hace el canal.

## Señal por señal

| # | Fecha | Dir | Zona | SL | TPs | Inicio (UTC) | Base hora | Llenado | Riesgo | 1er evento | TP1 | TP2 | TP3 | SL | MFE R | MAE R | Sin BE | BE 10m | BE tras TP1 | Canal dijo | Contraste |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 2026-07-13 | SELL | 4063-4065 | 4072 | 4056/4050/4046 | 07-13 11:11 | eastern_assumed | 11:11 @4063.36 | 8.6 | TP1 | 11:54 | 13:50 | 13:51 |  | 2.025 | -0.683 | TP3 +2.01R | BE +0.00R | BE +0.00R | closed_ambiguous_management | coincide |
| 2 | 2026-07-14 | SELL | 4028-4031 | 4037 | 4020/4012/4005 | 07-14 07:26 | eastern_assumed | 07:26 @4028.01 | 9.0 | TP1 | 08:02 |  |  | 12:30 | 1.551 | -3.855 | SL -1.00R | BE +0.00R | BE +0.00R | tp1_reported | coincide |
| 3 | 2026-07-14 | SELL | 4085-4089 | 4096.5 | 4075/4060/4035 | 07-14 13:23 | eastern_assumed | 13:23 @4085.20 | 11.3 | TP1 | 13:52 |  |  | 15:07 | 1.274 | -1.002 | SL -1.00R | BE +0.00R | BE +0.00R | closed_be_with_no_be_tp1_comparison | coincide |
| 4 | 2026-07-15 | SELL | 4028-4030 | 4037 | 4020/4013/4000 | 07-15 10:57 | received_at | 10:57 @4028.05 | 8.9 | SL |  |  |  | 11:41 | 0.08 | -1.001 | SL -1.00R | BE +0.00R | SL -1.00R | closed_sl | coincide |
| 7 | 2026-07-17 | SELL | 4000-4002 | 4010 | 3993/3982/3962 | 07-17 03:25 | explicit_utc | 03:25 @4002.57 | 7.4 | TP1 | 03:55 | 04:38 | 13:01 |  | 5.467 | -0.672 | TP3 +5.46R | BE +0.00R | BE +0.00R | tp1_reported_open | coincide |
| 8 | 2026-07-17 | BUY | 3974-3976 | 3965 | 3984/3995/4005 | 07-17 12:42 | explicit_utc | 12:42 @3975.89 | 10.9 | SL |  |  |  | 12:50 | 0.003 | -1.033 | SL -1.00R | SL -1.00R | SL -1.00R | closed_sl | coincide |
| 9 | 2026-07-22 | SELL | 4129-4133 | 4137 | 4123/4113/4101 | 07-22 00:00 | date_only | 02:32 @4129.19 | 7.8 | SL |  |  |  | 03:06 | 0.55 | -1.015 | SL -1.00R | BE +0.00R | SL -1.00R | closed_sl | coincide |
| 10 | 2026-07-23 | SELL | 4122-4124 | 4131.5 | 4115/4105/4098 | 07-23 00:00 | date_only | 02:44 @4122.01 | 9.5 | SL |  |  |  | 03:19 | 0.02 | -1.008 | SL -1.00R | BE +0.00R | SL -1.00R | closed_tp3 | NO coincide (mercado: SL) |
| 11 | 2026-07-23 | SELL | 4054-4056 | 4060 | 4049/4040/4029 | 07-23 00:00 | date_only | 13:23 @4054.24 | 5.8 | SL |  |  |  | 13:30 | 0.401 | -1.008 | SL -1.00R | SL -1.00R | SL -1.00R | closed_be | NO coincide (mercado con BE: SL) |
| 12 | 2026-07-27 | SELL | 4096-4098 | 4106 | 4089/4082/4075 | 07-27 00:00 | date_only | 06:12 @4096.19 | 9.8 | SL |  |  |  | 07:25 | 0.463 | -1.003 | SL -1.00R | BE +0.00R | SL -1.00R | closed_tp3 | NO coincide (mercado: SL) |

## Omitidas

- Fila 5 (2026-07-15): faltan entry/SL/TP
- Fila 6 (2026-07-15): sin dirección (actualización huérfana)

## Lo que esto no es

- No es una recomendación de operar. Es la verificación de lo que el mercado hizo después de cada señal publicada.
- Los llenados asumen que la orden se ejecuta en cuanto el precio toca la zona, sin deslizamiento.
- La muestra sigue siendo chica; ninguna métrica aquí es estadísticamente concluyente.
