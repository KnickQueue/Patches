#!/usr/bin/env bash
set -euo pipefail

PATCH_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$PATCH_DIR/../.." && pwd)"
PATCHES_REPO="${PATCHES_REPO:-$HOME/Documents/Dev/Patches}"
PATCHES_BRANCH="${PATCHES_BRANCH:-codex/pq-iqpilot-overlay-2026-04-02}"
TARGET_DIR="$PATCHES_REPO/iqpilot/pq_iqpilot_overlay_2026-04-02"
COMMIT_MSG="${1:-Refresh PQ IQ Pilot overlay bundle}"

"$PATCH_DIR/sync_bundle.sh"

if [[ ! -d "$PATCHES_REPO/.git" ]]; then
  echo "Missing git checkout at $PATCHES_REPO" >&2
  echo "Clone it first:" >&2
  echo "  git clone --single-branch --branch $PATCHES_BRANCH https://github.com/KnickQueue/Patches.git \"$PATCHES_REPO\"" >&2
  exit 1
fi

current_branch="$(git -C "$PATCHES_REPO" rev-parse --abbrev-ref HEAD)"
if [[ "$current_branch" != "$PATCHES_BRANCH" ]]; then
  echo "Expected branch $PATCHES_BRANCH, found $current_branch" >&2
  exit 1
fi

mkdir -p "$TARGET_DIR"
rsync -a --delete "$PATCH_DIR/" "$TARGET_DIR/"

git -C "$PATCHES_REPO" add iqpilot/pq_iqpilot_overlay_2026-04-02

if git -C "$PATCHES_REPO" diff --cached --quiet; then
  echo "No patch bundle changes to publish."
  exit 0
fi

git -C "$PATCHES_REPO" commit -m "$COMMIT_MSG"
git -C "$PATCHES_REPO" push origin "$PATCHES_BRANCH"

echo "Published bundle to $PATCHES_BRANCH"
