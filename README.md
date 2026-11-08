# xauusd-signals

Verificador de señales de oro (XAUUSD) contra el mercado real. Toma las señales
de un canal (zona de entrada, stop, TP1/TP2/TP3, hora) y reproduce qué habría
pasado tick a tick con precios bid/ask de Dukascopy, bajo tres manejos
distintos del stop. Es investigación, no una recomendación de operar.

## Uso

```bash
python verify.py data/signals_tracker.csv
python -m unittest discover -s tests -v
```

Sin dependencias externas (Python 3.10+). Salidas en `reports/results.csv` y
`reports/report.md`. Los ticks descargados quedan en `data/ticks/` (un archivo
por hora, ~55 KB) y no se vuelven a pedir.

Opciones: `--rows 1,4,10` (solo esas filas), `--horizon-hours 24`,
`--fill-window-hours 4`, `--be-minutes 10`, `--out reports/otra-carpeta`.

## Qué hace con cada señal

1. Convierte la hora a UTC. `h:mm AM/PM` se asume hora del Este (así las
   registra Francisco; verificado con la señal del 13-jul); `hh:mm UTC` se usa
   tal cual; sin hora, usa `received_at_utc` o arranca a las 00:00 UTC con una
   regla de aproximación (el precio debe venir del lado favorable).
2. Llena la orden cuando el precio toca la zona por el lado correcto del spread
   (bid para SELL, ask para BUY). Si el precio ya pasó el stop, la señal queda
   invalidada.
3. Sigue los ticks hasta 24 h y evalúa tres manejos: sin break-even, break-even
   a los 10 minutos del llenado (lo que hace el canal) y break-even al tocar
   TP1. Para cada uno reporta R con posición completa y en tercios.
4. Contrasta con lo que el canal reportó (`status` del tracker).

## Datos

Dukascopy publica ticks históricos gratis por HTTP plano:
`http://datafeed.dukascopy.com/datafeed/XAUUSD/AAAA/MM/DD/HHh_ticks.bi5`,
con el mes 0-indexado (julio = `06`), comprimidos en LZMA. Devuelve 503 si se
le pide muy seguido; el cliente reintenta con espera creciente.

## Velas para Vibe-Trading

```bash
python export_candles.py --months 6
```

Baja los ticks de Dukascopy y escribe `data/candles/XAUUSD_1m.csv` con velas
de 1 minuto (bid, UTC): `date, open, high, low, close, volume`, donde volumen
es el número de ticks. Es reanudable y tarda alrededor de una hora por seis
meses por el límite de velocidad de Dukascopy.

Vibe-Trading lo lee por su Data Bridge (`~/.vibe-trading/data-bridge/config.yaml`,
ya apunta a ese archivo) pidiendo el símbolo `local:XAUUSD`. El cargador
re-muestrea a 5m, 15m, 1h, 4h o 1d según el backtest. Para extender el
historial, correr el mismo comando otro día: continúa desde donde quedó.

## Formato del tracker

Columnas usadas: `signal_date`, `signal_time`, `received_at_utc`, `direction`,
`entry_low`, `entry_high`, `stop_loss`, `tp1`, `tp2`, `tp3`, `status`. El
resto se conserva pero no influye. Filas sin dirección o sin stop/TP se
listan como omitidas.
