#!/bin/sh
# Inicio de sesión de Claude para el agente, en el servidor. Lo corre Francisco como root:
#     xauusd-claude-token
# (install-agent.sh lo instala en /usr/local/sbin, a nombre de root: un script que corre root
# no debe vivir en una carpeta donde el usuario xauusd puede escribir.)
# Genera un token de larga duración con su suscripción (claude setup-token), lo guarda en
# config/claude.env (solo lo lee el usuario xauusd), hace una llamada real a Claude para
# comprobarlo y recién entonces activa el timer de las 7:00. El token nunca se muestra.
set -eu

APP=/opt/xauusd-signals
CLAUDE=$APP/claude-cli/node_modules/.bin/claude
ENVFILE=$APP/config/claude.env
PREFIX=sk-ant-oat01-
export HOME=$APP CLAUDE_CONFIG_DIR=$APP/.claude

[ -x "$CLAUDE" ] || { echo "No está instalado el CLI de Claude ($CLAUDE)."; exit 1; }

echo "PASO 1 de 2. Va a salir un enlace. Ábrelo en tu navegador y autoriza con tu cuenta de Claude."
echo "El navegador te da un CÓDIGO: pégalo aquí abajo cuando Claude lo pida."
echo "Después Claude muestra el TOKEN: un texto largo que empieza con $PREFIX"
echo "Ese token (no el código) es lo que vas a copiar para el paso 2."
echo
runuser -u xauusd -- env HOME=$HOME CLAUDE_CONFIG_DIR=$CLAUDE_CONFIG_DIR "$CLAUDE" setup-token

ok=0
for intento in 1 2 3; do
    echo
    echo "PASO 2 de 2. Pega el TOKEN (empieza con $PREFIX) y presiona Enter DOS veces."
    echo "No se verá en pantalla mientras lo pegas."
    stty -echo 2>/dev/null || true
    TOKEN=
    while IFS= read -r linea; do
        [ -n "$linea" ] || break
        TOKEN=$TOKEN$linea
    done
    stty echo 2>/dev/null || true
    echo
    TOKEN=$(printf '%s' "$TOKEN" | tr -d '[:space:]')
    case $TOKEN in
        "$PREFIX"*) ;;
        *) echo "Eso no es el token: debe empezar con $PREFIX (puede que hayas pegado el código del navegador)."
           continue ;;
    esac
    umask 077
    printf 'CLAUDE_CODE_OAUTH_TOKEN=%s\n' "$TOKEN" > "$ENVFILE"
    unset TOKEN
    chown xauusd:xauusd "$ENVFILE"
    chmod 600 "$ENVFILE"
    echo "Comprobando con una llamada real a Claude (unos segundos)..."
    if runuser -u xauusd -- /bin/sh -c "set -a; . $ENVFILE; set +a; cd $APP/.claude && HOME=$HOME CLAUDE_CONFIG_DIR=$CLAUDE_CONFIG_DIR exec $CLAUDE -p 'responde solo: ok'" >/dev/null 2>&1; then
        ok=1
        break
    fi
    echo "Claude rechazó ese token (puede que se haya copiado incompleto)."
done

if [ "$ok" = 1 ]; then
    systemctl enable --now xauusd-agent.timer
    echo "Listo: sesión válida y timer del agente activado."
    systemctl list-timers "xauusd-*" --no-pager
else
    rm -f "$ENVFILE"
    systemctl disable --now xauusd-agent.timer 2>/dev/null || true
    echo "No quedó una sesión válida. El timer del agente queda apagado. Vuelve a correr: xauusd-claude-token"
    exit 1
fi
