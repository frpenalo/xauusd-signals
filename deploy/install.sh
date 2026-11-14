#!/bin/sh
# Instala la señal mecánica de XAUUSD en el servidor. Correr como root desde la carpeta
# donde se descomprimió el paquete. No toca Docker, Caddy, /opt/subwave ni el crontab de root.
# Es idempotente: se puede volver a correr para actualizar el código sin perder datos.
set -eu

APP=/opt/xauusd-signals

id xauusd >/dev/null 2>&1 || useradd --system --home-dir "$APP" --no-create-home --shell /usr/sbin/nologin xauusd

mkdir -p "$APP/data" "$APP/logs" "$APP/config"
cp daily_signal.py backtest.py "$APP/"
rm -rf "$APP/verifier"
cp -r verifier "$APP/verifier"
cp data/events.csv "$APP/data/events.csv"
# El registro de señales solo se siembra la primera vez; después manda el del servidor.
[ -f "$APP/data/mech_signals.csv" ] || cp data/mech_signals.csv "$APP/data/mech_signals.csv"
cp config/telegram.env.example "$APP/config/telegram.env.example"

chown -R xauusd:xauusd "$APP"
chmod 750 "$APP"
chmod 700 "$APP/config"
[ -f "$APP/config/telegram.env" ] && chmod 600 "$APP/config/telegram.env"

cp deploy/xauusd-signal.service deploy/xauusd-signal.timer deploy/xauusd-warm.service deploy/xauusd-warm.timer /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now xauusd-signal.timer xauusd-warm.timer

echo "Instalado. Próxima corrida:"
systemctl list-timers "xauusd-*" --no-pager
[ -f "$APP/config/telegram.env" ] || echo "FALTA: $APP/config/telegram.env (lo pone Francisco; dueño xauusd, permisos 600)"
