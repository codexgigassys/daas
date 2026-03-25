#!/usr/bin/env bash
set -euo pipefail

# Cursor afterFileEdit: JSON on stdin includes file_path (absolute path on host).

if ! command -v jq >/dev/null 2>&1; then
  echo "formatter.sh: jq is not installed on the host (PATH)." >&2
  exit 1
fi
if ! command -v autopep8 >/dev/null 2>&1; then
  echo "formatter.sh: autopep8 is not installed on the host (PATH)." >&2
  exit 1
fi

json=$(cat)
file_path=$(printf '%s' "$json" | jq -r '.file_path // empty')

case "$file_path" in
  "") exit 0 ;;
  *.py) ;;
  *) exit 0 ;;
esac

root="${CURSOR_PROJECT_DIR:-$(pwd)}"
root="${root%/}"
# Cursor sends absolute paths; relative paths (e.g. from find ./...) must be resolved under root.
if [[ "$file_path" != /* ]]; then
  file_path="${root}/${file_path#./}"
fi

case "$file_path" in
  "$root"/*) ;;
  *) exit 0 ;;
esac

if [ ! -f "$file_path" ]; then
  echo "formatter.sh: file not found, skipping: $file_path" >&2
  exit 0
fi

exec autopep8 --in-place --ignore="E402,E501" "$file_path"
