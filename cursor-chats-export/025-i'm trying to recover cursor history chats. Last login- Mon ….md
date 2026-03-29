# i'm trying to recover cursor history chats. Last login: Mon …

Source: `../../../.cursor/projects/Users-macm1air-Documents-Code-sicop-health/agent-transcripts/d2b3f462-f936-498f-b34e-45c6bd771cb5/d2b3f462-f936-498f-b34e-45c6bd771cb5.jsonl`

---

**User**

<user_query>
i'm trying to recover cursor history chats.

Last login: Mon Mar  9 21:28:04 on ttys002
macm1air@Ocreamer-3 ~ % CURSOR_USER="/Users/macm1air/Library/Application Support/Cursor/User/globalStorage"
cd "$CURSOR_USER"
macm1air@Ocreamer-3 globalStorage % cp -a state.vscdb state.vscdb.before-recovery

macm1air@Ocreamer-3 globalStorage % rm -f state.vscdb-shm state.vscdb-wal

macm1air@Ocreamer-3 globalStorage % cp -a "state.vscdb.corrupted.1773112088515" state.vscdb<2028>

macm1air@Ocreamer-3 globalStorage % cp -a state.vscdb.backup state.vscdb

macm1air@Ocreamer-3 globalStorage % cd "/Users/macm1air/Library/Application Support/Cursor/User/globalStorage"

macm1air@Ocreamer-3 globalStorage % rm -f state.vscdb-shm state.vscdb-wal

macm1air@Ocreamer-3 globalStorage % cp -a "state.vscdb.corrupted.1773112088515" state.vscdb

macm1air@Ocreamer-3 globalStorage % ls -lh state.vscdb

-rw-r--r--@ 1 macm1air  staff   722M Mar  9 21:45 state.vscdb
macm1air@Ocreamer-3 globalStorage % sqlite3 state.vscdb "SELECT COUNT(*) FROM cursorDiskKV;"

92046
macm1air@Ocreamer-3 globalStorage % sqlite3 state.vscdb ".recover" > recovered.sql

macm1air@Ocreamer-3 globalStorage % wc -l recovered.sql
   93385 recovered.sql
macm1air@Ocreamer-3 globalStorage % sqlite3 state.vscdb.recovered < recovered.sql

          defensive off
macm1air@Ocreamer-3 globalStorage % sqlite3 state.vscdb.recovered2 << 'EOF'
.read recovered.sql
EOF
          defensive off
macm1air@Ocreamer-3 globalStorage % grep -v "PRAGMA" recovered.sql | grep -v "defensive" | sqlite3 state.vscdb.clean

macm1air@Ocreamer-3 globalStorage % sqlite3 state.vscdb.clean "SELECT COUNT(*) FROM cursorDiskKV;"
sqlite3 state.vscdb.clean "SELECT COUNT(*) FROM ItemTable;"
ls -lh state.vscdb.clean
92029
1322
-rw-r--r--  1 macm1air  staff   724M Mar  9 21:47 state.vscdb.clean
macm1air@Ocreamer-3 globalStorage % rm -f state.vscdb state.vscdb-shm state.vscdb-wal

macm1air@Ocreamer-3 globalStorage % cp state.vscdb.clean state.vscdb

macm1air@Ocreamer-3 globalStorage % ls -lh state.vscdb

-rw-r--r--  1 macm1air  staff   724M Mar  9 21:48 state.vscdb
macm1air@Ocreamer-3 globalStorage % 
  [Restored Mar 9, 2026 at 9:51:17 PM]
Last login: Mon Mar  9 21:51:17 on ttys000
Restored session: Mon Mar  9 21:50:21 CST 2026
macm1air@Ocreamer-3 globalStorage % 
  [Restored Mar 9, 2026 at 10:24:03 PM]
Last login: Mon Mar  9 22:24:03 on ttys001
Restored session: Mon Mar  9 22:15:48 CST 2026
macm1air@Ocreamer-3 globalStorage % cd "/Users/macm1air/Library/Application Support/Cursor/User/globalStorage/"

macm1air@Ocreamer-3 globalStorage % ls -lh state.vscdb*
-rw-r--r--@ 1 macm1air  staff   4.0K Mar  9 22:25 state.vscdb
-rw-r--r--@ 1 macm1air  staff   721M Mar  9 21:07 state.vscdb 
-rw-r--r--@ 1 macm1air  staff    32K Mar  9 22:26 state.vscdb-shm
-rw-r--r--@ 1 macm1air  staff   1.0M Mar  9 22:26 state.vscdb-wal
-rw-r--r--@ 1 macm1air  staff   724M Mar  9 22:24 state.vscdb.724mb-backup
-rw-r--r--@ 1 macm1air  staff   724M Mar  9 22:25 state.vscdb.backup
-rw-r--r--@ 1 macm1air  staff   4.0K Mar  9 21:26 state.vscdb.bak
-rw-r--r--@ 1 macm1air  staff   722M Mar  9 21:40 state.vscdb.before-recovery
-rw-r--r--  1 macm1air  staff   724M Mar  9 21:47 state.vscdb.clean
-rw-r--r--@ 1 macm1air  staff   721M Mar  9 21:07 state.vscdb.corrupted.1773112088515
-rw-r--r--@ 1 arthub    staff   721M Mar  9 21:07 state.vscdb.corrupted.1773112109288
-rw-r--r--@ 1 macm1air  staff   4.0K Mar  9 21:08 state.vscdb.corrupted.1773112397558
-rw-r--r--@ 1 macm1air  staff   4.0K Mar  9 21:13 state.vscdb.corrupted.1773113157061
-rw-r--r--@ 1 macm1air  staff   4.0K Mar  9 21:25 state.vscdb.corrupted.1773113161182
-rw-r--r--@ 1 macm1air  staff   4.0K Mar  9 21:26 state.vscdb.corrupted.1773113202865
-rw-r--r--@ 1 macm1air  staff   4.0K Mar  9 21:27 state.vscdb.corrupted.1773113229452
-rw-r--r--@ 1 macm1air  staff   4.0K Mar  9 21:27 state.vscdb.corrupted.1773113232052
-rw-r--r--@ 1 macm1air  staff    21B Mar  9 22:26 state.vscdb.options.json
-rw-r--r--  1 macm1air  staff   724M Mar  9 21:46 state.vscdb.recovered
-rw-r--r--  1 macm1air  staff   724M Mar  9 21:47 state.vscdb.recovered2
macm1air@Ocreamer-3 globalStorage % ls -lhi state.vscdb*

255382854 -rw-r--r--@ 1 macm1air  staff   564K Mar  9 22:27 state.vscdb
255291895 -rw-r--r--@ 1 macm1air  staff   721M Mar  9 21:07 state.vscdb 
255302435 -rw-r--r--@ 1 macm1air  staff   724M Mar  9 22:24 state.vscdb.724mb-backup
255189118 -rw-r--r--@ 1 macm1air  staff   564K Mar  9 22:27 state.vscdb.backup
255162458 -rw-r--r--@ 1 macm1air  staff   4.0K Mar  9 21:26 state.vscdb.bak
255291745 -rw-r--r--@ 1 macm1air  staff   722M Mar  9 21:40 state.vscdb.before-recovery
255300910 -rw-r--r--  1 macm1air  staff   724M Mar  9 21:47 state.vscdb.clean
168975281 -rw-r--r--@ 1 macm1air  staff   721M Mar  9 21:07 state.vscdb.corrupted.1773112088515
255142594 -rw-r--r--@ 1 arthub    staff   721M Mar  9 21:07 state.vscdb.corrupted.1773112109288
255148384 -rw-r--r--@ 1 macm1air  staff   4.0K Mar  9 21:08 state.vscdb.corrupted.1773112397558
255150069 -rw-r--r--@ 1 macm1air  staff   4.0K Mar  9 21:13 state.vscdb.corrupted.1773113157061
255162268 -rw-r--r--@ 1 macm1air  staff   4.0K Mar  9 21:25 state.vscdb.corrupted.1773113161182
255162317 -rw-r--r--@ 1 macm1air  staff   4.0K Mar  9 21:26 state.vscdb.corrupted.1773113202865
255162614 -rw-r--r--@ 1 macm1air  staff   4.0K Mar  9 21:27 state.vscdb.corrupted.1773113229452
255162618 -rw-r--r--@ 1 macm1air  staff   4.0K Mar  9 21:27 state.vscdb.corrupted.1773113232052
228822440 -rw-r--r--@ 1 macm1air  staff    21B Mar  9 22:26 state.vscdb.options.json
255300230 -rw-r--r--  1 macm1air  staff   724M Mar  9 21:46 state.vscdb.recovered
255300372 -rw-r--r--  1 macm1air  staff   724M Mar  9 21:47 state.vscdb.recovered2
macm1air@Ocreamer-3 globalStorage % find . -maxdepth 1 -name "state.vscdb" -ls
255382854     1152 -rw-r--r--    1 macm1air         staff              577536 Mar  9 22:27 ./state.vscdb
macm1air@Ocreamer-3 globalStorage % # Cursor debe estar cerrado (Cmd+Q)

sqlite3 state.vscdb << 'EOF'
ATTACH 'state.vscdb.clean' AS src;

INSERT OR IGNORE INTO cursorDiskKV
  SELECT key, value FROM src.cursorDiskKV
  WHERE key NOT LIKE 'checkpointId:%'
  AND key NOT LIKE 'agentKv:blob:%';

INSERT OR IGNORE INTO ItemTable
  SELECT key, value FROM src.ItemTable;
DETACH src;
EOF

sqlite3 state.vscdb "SELECT COUNT(*) FROM cursorDiskKV;"
ls -lh state.vscdb
zsh: unknown file attribute: C
55906
-rw-r--r--@ 1 macm1air  staff   428M Mar  9 22:29 state.vscdb
macm1air@Ocreamer-3 globalStorage % 

</user_query>

---

**Assistant**

Checking where Cursor stores chat history and how it maps to your recovery so we can give precise next steps.
[Tool: Grep]
[Tool: LS]

---

**Assistant**

[Tool: Glob]

---

**Assistant**

Here’s what your steps did and what to do next.

---

## What you did

1. You built a **recovered DB**: `state.vscdb.clean` (724 MB) with 92,029 `cursorDiskKV` rows and 1,322 `ItemTable` rows.
2. You **merged** that into the **live** `state.vscdb` with:
   - `INSERT OR IGNORE` from `state.vscdb.clean` into `state.vscdb`
   - Skipping keys `checkpointId:%` and `agentKv:blob:%`
3. Result: live `state.vscdb` grew to **428 MB** and has **55,906** `cursorDiskKV` rows. So a lot of recovered data is now in the active DB.

So recovery into the live DB is done; the question is whether Cursor’s UI shows the old chats again.

---

## What to do next

1. **Fully quit Cursor** (Cmd+Q, not just closing the window).
2. **Reopen Cursor** and check the chat/composer history in the UI.

Cursor loads `state.vscdb` at startup. If chat state is stored in `cursorDiskKV`/`ItemTable` under keys you didn’t exclude, it should reappear after this merge and restart.

---

## If chats still don’t show

- **Project chats are also on disk.** For this project, conversation logs are under:
  - `~/.cursor/projects/Users-macm1air-Documents-Code-sicop-health/agent-transcripts/`
  - You have 48 transcript files there (`.jsonl` and `.txt`). So the raw conversation data for this project is not lost even if the UI doesn’t list old chats.
- **Keep a backup of the recovered DB:**
  - Keep `state.vscdb.clean` (or a copy) somewhere safe. Don’t overwrite it. You can try replacing `state.vscdb` with it later (with Cursor closed) if you want to “go back” to the recovered snapshot.

---

## About the shell error

`zsh: unknown file attribute: C` usually comes from the shell parsing the heredoc or a pasted line (e.g. a character from “Cmd+Q” or a smart quote). The `INSERT` clearly ran (55,906 rows, 428 MB), so the recovery step itself succeeded.

---

**Summary:** Merged recovered data into the live `state.vscdb`. Quit Cursor completely, reopen, and check chat history. If it’s still missing, you still have the project’s chats in `agent-transcripts` and the full recovered DB in `state.vscdb.clean`.

---

**User**

<user_query>
old chats are not appearing. is there a way to recover?
</user_query>

---

**Assistant**

Checking how agent transcripts are stored so we can recover chats from disk if the UI doesn't show them.
[Tool: Read]
[Tool: LS]

---
