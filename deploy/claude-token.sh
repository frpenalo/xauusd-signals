#!/bin/sh
# Inicio de sesión de Claude para el agente, en el servidor. Lo corre Francisco como root:
#     /opt/xauusd-signals/deploy/claude-token.sh
# Genera un token de larga duración con su suscripción (claude setup-token), lo guarda en
# config/claude.env (solo lo lee el usuario xauusd), comprueba que el agente puede usarlo y
# recién entonces activa el timer de las 7:00. El token nunca se muestra ni sale del servidor.
set -eu

APP=/opt/xauusd-signals
CLAUDE=$APP/claude-cli/node_modules/.bin/claude
ENVFILE=$APP/config/claude.env
export HOME=$APP CLAUDE_CONFIG_DIR=$APP/.claude

[ -x "$CLAUDE" ] || { echo "No está instalado el CLI de Claude ($CLAUDE)."; exit 1; }

echo "Paso 1 de 2. Se abrirá un enlace: ábrelo en tu navegador, autoriza con tu cuenta de Claude"
echo "y pega aquí el código que te da. Al final Claude te muestra un token largo: cópialo."
echo
runuser -u xauusd -- env HOME=$HOME CLAUDE_CONFIG_DIR=$CLAUDE_CONFIG_DIR "$CLAUDE" setup-token

echo
echo "Paso 2 de 2. Pega el token y presiona Enter (no se verá en pantalla):"
stty -echo 2>/dev/null || true
read -r TOKEN
stty echo 2>/dev/null || true
echo
TOKEN=$(printf '%s' "$TOKEN" | tr -d '[:space:]')
[ -n "$TOKEN" ] || { echo "No se recibió ningún token. No se cambió nada."; exit 1; }

umask 077
printf 'CLAUDE_CODE_OAUTH_TOKEN=%s\n' "$TOKEN" > "$ENVFILE"
unset TOKEN
chown xauusd:xauusd "$ENVFILE"
chmod 600 "$ENVFILE"

echo "Comprobando que el agente puede usar la sesión..."
if runuser -u xauusd -- /bin/sh -c "set -a; . $ENVFILE; set +a; HOME=$HOME CLAUDE_CONFIG_DIR=$CLAUDE_CONFIG_DIR exec $CLAUDE auth status" | grep -q '"loggedIn": *true'; then
    systemctl enable --now xauusd-agent.timer
    echo "Listo: sesión válida y timer del agente activado."
    systemctl list-timers "xauusd-*" --no-pager
else
    echo "La sesión NO quedó válida. El timer del agente sigue apagado. Vuelve a correr este script."
    exit 1
fi
