#!/bin/sh
set -eu
cd "$(dirname "$0")"
if [ "$(uname -s)" != "Linux" ]; then
  echo "ProcScope requires Linux with /proc. On macOS, use an Ubuntu Linux machine or VM." >&2
  exit 2
fi
if [ ! -r /proc/sys/kernel/random/boot_id ]; then
  echo "Cannot read /proc boot ID. Ensure Linux procfs is mounted and readable." >&2
  exit 2
fi
exec python3 server.py
