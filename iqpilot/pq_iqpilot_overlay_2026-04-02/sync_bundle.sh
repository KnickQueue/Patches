#!/usr/bin/env bash
set -euo pipefail

PATCH_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$PATCH_DIR/../.." && pwd)"
FILES_MANIFEST="$PATCH_DIR/FILES.txt"
STAGE_DIR="$PATCH_DIR/files"

if [[ ! -f "$FILES_MANIFEST" ]]; then
  echo "Missing manifest: $FILES_MANIFEST" >&2
  exit 1
fi

rm -rf "$STAGE_DIR"
mkdir -p "$STAGE_DIR"

while IFS= read -r relpath || [[ -n "$relpath" ]]; do
  [[ -z "$relpath" ]] && continue
  src="$REPO_ROOT/$relpath"
  dst="$STAGE_DIR/$relpath"

  if [[ ! -f "$src" ]]; then
    echo "Missing source file: $src" >&2
    exit 1
  fi

  mkdir -p "$(dirname "$dst")"
  cp "$src" "$dst"
done < "$FILES_MANIFEST"

echo "Refreshed bundle in $STAGE_DIR"
