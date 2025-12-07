#!/usr/bin/env bash
set -euo pipefail

# Simple macOS build helper for Maroon Type using PyInstaller.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON:-python3}"

if ! "$PYTHON_BIN" -c "import PyInstaller" >/dev/null 2>&1; then
  echo "PyInstaller not found, installing..."
  "$PYTHON_BIN" -m pip install --upgrade pip pyinstaller
fi

echo "Running PyInstaller..."
"$PYTHON_BIN" -m PyInstaller --clean --noconfirm app.spec

echo "Done. Output: dist/MaroonType.app"
