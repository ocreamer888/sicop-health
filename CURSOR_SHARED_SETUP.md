# Share Cursor config across macOS profiles

This guide is for **the other macOS profile** (e.g. arthub) so Cursor uses the same `.cursor` folder as macm1air, with **Read & Write** so you can change rules and settings.

---

## Prerequisites (do once from macm1air’s profile — already done)

1. Open **Finder** and go to `/Users/macm1air/` (Cmd+Shift+G → type that path).
2. Show hidden files (Cmd+Shift+.) and find the **`.cursor`** folder.
3. Right‑click **`.cursor`** → **Get Info** → **Sharing & Permissions**.
4. Unlock (click the lock and enter the admin password if needed).
5. For the **other user** (e.g. arthub): set **Read & Write**.
6. For **everyone** (optional): set **Read & Write** if you want any profile to use and edit it.
7. Click the gear → **Apply to enclosed items** so all files inside get the same access.
8. Lock again if you want.

**Note:** ACLs are set so user **arthub** can traverse `/Users/macm1air`, and has full **read/write** on `/Users/macm1air/.cursor` and on `/Users/macm1air/Library/Application Support/Cursor/User` (chat history, settings). The other profile can go straight to **"On the other profile"** below.

---

## On the other profile (e.g. arthub)

Do this **once** when logged in as the other user.

### 1. Back up existing Cursor config (if any)

In **Terminal**:

```bash
# Replace 'arthub' with your short username if different
if [ -d "$HOME/.cursor" ] && [ ! -L "$HOME/.cursor" ]; then
  mv "$HOME/.cursor" "$HOME/.cursor.backup.$(date +%Y%m%d)"
  echo "Backed up existing .cursor to .cursor.backup.*"
fi
```

If you already have a symlink and want to replace it:

```bash
rm "$HOME/.cursor"   # removes the symlink, not the real folder
```


### 2. Symlink .cursor (skills, MCP, rules, projects)

```bash
ln -s /Users/macm1air/.cursor "$HOME/.cursor"
```

### 3. Symlink Cursor User folder (chat history, settings, keybindings)

```bash
CURSOR_USER="$HOME/Library/Application Support/Cursor/User"
MACM1AIR_USER="/Users/macm1air/Library/Application Support/Cursor/User"
mkdir -p "$HOME/Library/Application Support/Cursor"
if [ -d "$CURSOR_USER" ] && [ ! -L "$CURSOR_USER" ]; then
  mv "$CURSOR_USER" "${CURSOR_USER}.backup.$(date +%Y%m%d)"
fi
[ -L "$CURSOR_USER" ] && rm "$CURSOR_USER"
ln -s "$MACM1AIR_USER" "$CURSOR_USER"
```

### 4. Confirm

```bash
ls -la "$HOME/.cursor"
ls -la "$HOME/Library/Application Support/Cursor/User"
```

You should see both symlinks pointing to macm1air's paths.

---

## Result

- **Shared:** skills, MCP, rules, projects (via `~/.cursor`).
- **Shared:** chat history, settings, keybindings (via Cursor `User` folder).
- **Writable from arthub:** ACLs give arthub full read/write on both `.cursor` and Cursor `User`, so you can change rules, settings, and chats from the other profile.

---

## Troubleshooting

| Issue | What to do |
|-------|------------|
| “Permission denied” when opening Cursor | On macm1air’s profile, give your user **Read & Write** on `.cursor` and apply to enclosed items. |
| Cursor still uses old config | Quit Cursor fully (Cmd+Q), then open it again. |
| You want to stop sharing | Remove both symlinks: `rm "$HOME/.cursor"` and `rm "$HOME/Library/Application Support/Cursor/User"`. Restore from backups if you made them. |

This can happen if the storage file is corrupted, moved, or there are permission issues.

Storage path: /Users/arthub/Library/Application Support/Cursor/User/workspaceStorage/397b7dffca7241d9cb9d318e55d70bda/state.vscdb