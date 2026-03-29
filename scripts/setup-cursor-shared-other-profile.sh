#!/usr/bin/env bash
# Share Cursor config from macm1air with the current user (e.g. arthub).
# Run this once when logged in as the other profile. See CURSOR_SHARED_SETUP.md.

set -e
SOURCE_USER="macm1air"
SOURCE_HOME="/Users/$SOURCE_USER"
SOURCE_CURSOR="$SOURCE_HOME/.cursor"
SOURCE_CURSOR_USER="$SOURCE_HOME/Library/Application Support/Cursor/User"
CURSOR_USER="$HOME/Library/Application Support/Cursor/User"

if [ ! -d "$SOURCE_CURSOR" ]; then
  echo "Error: $SOURCE_CURSOR not found. Run prerequisites from macm1air's profile first."
  exit 1
fi

echo "=== Backing up / replacing .cursor ==="
if [ -d "$HOME/.cursor" ] && [ ! -L "$HOME/.cursor" ]; then
  BACKUP="$HOME/.cursor.backup.$(date +%Y%m%d)"
  mv "$HOME/.cursor" "$BACKUP"
  echo "Backed up existing .cursor to $BACKUP"
fi
[ -L "$HOME/.cursor" ] && rm "$HOME/.cursor"
ln -s "$SOURCE_CURSOR" "$HOME/.cursor"
echo "Symlinked $HOME/.cursor -> $SOURCE_CURSOR"

echo ""
echo "=== Backing up / replacing Cursor User folder ==="
if [ ! -d "$SOURCE_CURSOR_USER" ]; then
  echo "Warning: $SOURCE_CURSOR_USER not found. Cursor may not have been run on macm1air yet."
fi
mkdir -p "$HOME/Library/Application Support/Cursor"
if [ -d "$CURSOR_USER" ] && [ ! -L "$CURSOR_USER" ]; then
  BACKUP="${CURSOR_USER}.backup.$(date +%Y%m%d)"
  mv "$CURSOR_USER" "$BACKUP"
  echo "Backed up existing Cursor User to $BACKUP"
fi
[ -L "$CURSOR_USER" ] && rm "$CURSOR_USER"
ln -s "$SOURCE_CURSOR_USER" "$CURSOR_USER"
echo "Symlinked Cursor User -> $SOURCE_CURSOR_USER"

echo ""
echo "=== Confirm ==="
ls -la "$HOME/.cursor"
ls -la "$CURSOR_USER"
echo ""
echo "Done. Quit Cursor (Cmd+Q) and reopen if it was running."
