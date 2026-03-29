# Cursor chat history recovery

If old chats don’t appear in the Cursor UI after merging into `state.vscdb`, try these in order.

---

## 1. Use the full recovered DB as the main DB

Cursor may need the **entire** recovered DB as the active file (not a merge). With **Cursor fully quit** (Cmd+Q):

```bash
CURSOR_USER="/Users/macm1air/Library/Application Support/Cursor/User/globalStorage"
cd "$CURSOR_USER"

# Backup what you have now
cp -a state.vscdb state.vscdb.after-merge-backup

# Remove WAL/SHM so Cursor doesn’t use journal mode on the next file
rm -f state.vscdb-shm state.vscdb-wal

# Replace live DB with the clean recovered one (92k keys)
cp -a state.vscdb.clean state.vscdb

# Optional: verify
sqlite3 state.vscdb "SELECT COUNT(*) FROM cursorDiskKV;"
# Should be ~92029
```

Then start Cursor and check if the chat list reappears.

---

## 2. Recover content from agent transcripts (always works)

Chat **content** is also stored as JSONL files under:

- **This project:**  
  `~/.cursor/projects/Users-macm1air-Documents-Code-sicop-health/agent-transcripts/`
- **All projects:**  
  `~/.cursor/projects/*/agent-transcripts/`

You can export all of them to readable Markdown:

```bash
# From the repo root (sicop-health)
node scripts/export-cursor-transcripts.js
```

This creates `./cursor-chats-export/` with:

- `INDEX.md` – list of all exported chats
- `001-…md`, `002-…md`, … – one Markdown file per conversation

So even if the UI never shows old chats again, you still have the full text of each conversation in `cursor-chats-export/`.

---

## 3. Optional: inspect what’s in the recovered DB

To see which keys might be chat-related (e.g. to debug or restore a specific key):

```bash
cd "/Users/macm1air/Library/Application Support/Cursor/User/globalStorage"
sqlite3 state.vscdb.clean "SELECT key FROM cursorDiskKV WHERE key LIKE '%chat%' OR key LIKE '%conversation%' OR key LIKE '%composer%' LIMIT 50;"
```

---

## Summary

| Goal                         | Action |
|-----------------------------|--------|
| Chats back in Cursor UI     | Do step 1 (use `state.vscdb.clean` as `state.vscdb` with Cursor closed). |
| Read old chats as files     | Run `node scripts/export-cursor-transcripts.js` (step 2). |
| Keep a safe copy of recovery| Don’t delete `state.vscdb.clean`; keep it as a backup. |
