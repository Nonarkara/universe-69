#!/bin/sh
# Run the universes in the foreground (the LaunchAgent does this 24/7).
cd "$(dirname "$0")"
if [ -x /usr/bin/python3 ]; then
  PY=/usr/bin/python3
elif [ -x /usr/local/bin/python3 ]; then
  PY=/usr/local/bin/python3
elif command -v python3 >/dev/null 2>&1; then
  PY=python3
else
  echo "python3 not found" >&2
  exit 1
fi
exec "$PY" -u sim/server.py
