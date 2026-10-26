#!/bin/sh
# Run the universes in the foreground (the LaunchAgent does this 24/7).
cd "$(dirname "$0")"
exec /usr/local/bin/python3 sim/server.py
