#!/bin/sh
# Instala el agente (Vibe-Trading + CLI de Claude) en el servidor, junto a la regla mecánica.
# Correr como root desde la carpeta donde se descomprimió el paquete. Todo queda dentro de
# /opt/xauusd-signals y a nombre del usuario xauusd. No toca Docker, Caddy, /opt/subwave, el
# crontab de root ni los servicios de la regla (xauusd-signal, xauusd-warm) ni verifier/.
# Es idempotente. NO activa el timer del agente: eso lo hace deploy/claude-token.sh cuando
# el inicio de sesión de Claude ya funciona.
set -eu

APP=/opt/xauusd-signals
VT=$APP/vibe-trading
CLI=$APP/claude-cli
CLAUDE_VERSION=2.1.302  # la misma del CLI de la laptop con la que se midió el agente

id xauusd >/dev/null 2>&1 || { echo "falta el usuario xauusd: instalar primero la regla con install.sh"; exit 1; }

# Las descargas e instalaciones pesadas corren con los mismos límites que el servicio.
limited() {
    systemd-run --quiet --wait --pipe --collect --uid=xauusd --gid=xauusd \
        -p CPUQuota=50% -p MemoryMax=1500M -p Nice=15 -p IOSchedulingClass=idle \
        --setenv=HOME=$APP --working-directory="$1" /bin/sh -c "$2"
}

mkdir -p "$VT" "$CLI" "$APP/.vibe-trading/data-bridge" "$APP/.claude" "$APP/data/candles" "$APP/deploy"

# Código de la señal: solo lo que el agente necesita además de lo ya instalado.
cp daily_signal.py export_candles.py "$APP/"
cp deploy/claude-token.sh "$APP/deploy/claude-token.sh"
chmod 755 "$APP/deploy/claude-token.sh"
# Velas y registro del agente: se siembran una vez; después manda lo del servidor.
[ -f "$APP/data/candles/XAUUSD_1m.csv" ] || cp data/candles/XAUUSD_1m.csv "$APP/data/candles/XAUUSD_1m.csv"
[ -f "$APP/data/agent_signals.csv" ] || cp data/agent_signals.csv "$APP/data/agent_signals.csv"

# Vibe-Trading: código, ajustes del agente (sin llaves) y fuente local de velas.
rm -rf "$VT/agent"
cp -r vibe-trading/agent "$VT/agent"
cp vibe-trading/pyproject.toml vibe-trading/README.md vibe-trading/LICENSE vibe-trading/MANIFEST.in \
   vibe-trading/requirements-lock.txt "$VT/"
cat > "$VT/agent/.env" <<'EOF'
LANGCHAIN_PROVIDER=claude-cli
LANGCHAIN_MODEL_NAME=claude-sonnet-5
LANGCHAIN_REASONING_EFFORT=medium
CLAUDE_CLI_DENY_TOOL_PREFIXES=trading_,etoro_
CLAUDE_CLI_BASH_POLICY=python-only
TIMEOUT_SECONDS=600
VIBE_TRADING_DATA_CACHE=true
EOF
cat > "$APP/.vibe-trading/data-bridge/config.yaml" <<'EOF'
# Data Bridge de Vibe-Trading: fuentes locales.
# Se piden con el prefijo local:, por ejemplo local:XAUUSD.
sources:
  - symbol: "XAUUSD"
    type: csv
    path: "/opt/xauusd-signals/data/candles/XAUUSD_1m.csv"
    columns:
      date: "date"
      open: "open"
      high: "high"
      low: "low"
      close: "close"
      volume: "volume"
EOF

chown -R xauusd:xauusd "$APP"
chmod 750 "$APP"
chmod 700 "$APP/config"
[ -f "$APP/config/telegram.env" ] && chmod 600 "$APP/config/telegram.env"
[ -f "$APP/config/claude.env" ] && chmod 600 "$APP/config/claude.env"

# Entorno de Python del agente: versiones fijadas y verificadas por hash.
[ -x "$VT/.venv/bin/python" ] || limited "$VT" "/usr/bin/python3 -m venv .venv"
limited "$VT" ".venv/bin/pip install --quiet --no-cache-dir --disable-pip-version-check --require-hashes -r requirements-lock.txt"
limited "$VT" ".venv/bin/pip install --quiet --no-cache-dir --disable-pip-version-check --no-deps -e ."

# CLI de Claude, solo para este usuario (no se instala nada global).
limited "$CLI" "npm install --no-fund --no-audit --loglevel=error --cache $CLI/.npm-cache --prefix $CLI @anthropic-ai/claude-code@$CLAUDE_VERSION && rm -rf $CLI/.npm-cache"

cp deploy/xauusd-agent.service deploy/xauusd-agent.timer /etc/systemd/system/
systemctl daemon-reload

echo "Agente instalado:"
"$VT/.venv/bin/vibe-trading" --version 2>/dev/null || true
"$CLI/node_modules/.bin/claude" --version
du -sh "$VT" "$CLI"
[ -f "$APP/config/claude.env" ] || echo "FALTA: el token de Claude. Lo pone Francisco con: $APP/deploy/claude-token.sh"
