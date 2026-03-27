# I want to share cursor memory, skills, and everything around…

Source: `../../../.cursor/projects/Users-macm1air-Documents-Code-sicop-health/agent-transcripts/6ce94c4a-bc0f-43dc-b314-b0b9ef791727/6ce94c4a-bc0f-43dc-b314-b0b9ef791727.jsonl`

---

**User**

<user_query>
I want to share cursor memory, skills, and everything around ai across profiles. How can i achieve it?
</user_query>

---

**Assistant**

Searching for where Cursor stores memory, skills, and AI config and how profiles work.
[Tool: WebSearch]
[Tool: Glob]

---

**Assistant**

[Tool: mcp_web_fetch]
[Tool: LS_DIR]
[Tool: Grep]

---

**Assistant**

[Tool: Shell]
[Tool: WebSearch]
[Tool: Shell]

---

**Assistant**

[Tool: Shell]
[Tool: mcp_web_fetch]

---

**Assistant**

[Tool: Read]
[Tool: Shell]

---

**Assistant**

Here’s a concise map of where things live and how to share them across profiles.

---

## Where Cursor stores things

| What | Location |
|------|----------|
| **Skills** | `~/.cursor/skills/`, `~/.cursor/skills-cursor/`, and optionally `~/.codex/skills/`, `~/.claude/...` |
| **MCP config** | `~/.cursor/mcp.json` |
| **Global commands** | `~/.cursor/commands/` (if you use them) |
| **User rules / memories** | `~/Library/Application Support/Cursor/User/globalStorage/state.vscdb` (SQLite, key `aicontext.personalContext`). In recent Cursor versions some of this may also be stored in the cloud. |
| **Settings / keybindings** | `~/Library/Application Support/Cursor/User/settings.json`, `keybindings.json` |
| **Profile-specific data** | `~/Library/Application Support/Cursor/CachedProfilesData/<profile_name>/` (per profile when using **Profiles: Switch Profile**) |

So:

- **Skills, MCP, commands** → under `~/.cursor` (and related dotfolders). Same for every Cursor window on this machine.
- **Rules/memory and editor settings** → under `Application Support/Cursor/User/` (and possibly per-profile under `CachedProfilesData`). These are what differ between profiles.

---

## What “profiles” means here

1. **Cursor profiles** (Cmd+Shift+P → “Profiles: Switch Profile”)  
   Each profile can have its own settings, keybindings, and possibly its own copy of state (including rules/memory). They still use the same `~/.cursor` (so skills are shared).

2. **Separate data dirs** (`cursor --user-data-dir=~/.cursor-python`, etc.)  
   This is a second, fully separate “Cursor install”: its own `User/`, `globalStorage`, settings, etc. Skills might still be read from `~/.cursor` (same as above), but all Application Support–style data is isolated per dir.

So “sharing across profiles” mainly means aligning **rules/memory** and **settings** that live under Application Support (and per-profile dirs).

---

## How to share memory, skills, and AI-related config across profiles

### 1. **Skills and MCP (already shared on this machine)**

- Skills and MCP live in `~/.cursor` (and `.codex` / `.claude` if you use them). All Cursor profiles and `--user-data-dir` instances on this machine typically use the same `$HOME`, so they already share these.
- To share **across machines**: put `~/.cursor` (and optionally `.codex` / `.claude`) under version control or a sync folder (e.g. Git repo, Dropbox), and clone or sync that on each machine.

### 2. **User rules / memories (and settings) across Cursor profiles**

- Rules/memories are in `User/globalStorage/state.vscdb`. If each profile has its own `User` or its own `state.vscdb`, they won’t share rules unless you force it.

**Option A – Prefer a single profile**  
Use one Cursor profile for “shared AI + editor” and switch to it when you want that setup. No copying; everything stays in one place.

**Option B – Symlink so all profiles use the same User data**  
- Pick one profile (e.g. default) as the “source.”
- For every other profile, replace its `User` (or at least `User/globalStorage`) with a symlink to the source profile’s `User` (or `User/globalStorage`).  
- Then all profiles use the same `settings.json`, `keybindings.json`, and `state.vscdb` (same rules/memory).  
- Caveat: Cursor may expect one writer at a time; symlinking the whole `User` or just `globalStorage` can work but avoid opening the same “profile” from two Cursor instances at once.

**Option C – Script to copy rules (and optionally settings) into each profile**  
- Export the rules from the “master” `state.vscdb` (e.g. the SQLite query from the forum: `SELECT value FROM ItemTable WHERE key = 'aicontext.personalContext';`).
- Either:
  - Update the same key in each profile’s `state.vscdb`, or  
  - If Cursor supports it, use an import path or UI to load that blob into each profile.  
- You can do the same for `settings.json` / `keybindings.json` by copying those files into each profile’s `User` folder.

### 3. **If you use multiple `--user-data-dir` instances**

- Each `--user-data-dir=~/.cursor-xyz` has its own “Application Support” tree (its own `User/`, `globalStorage`, etc.).
- To share memory/settings across those:
  - Symlink each instance’s `User` (or `User/globalStorage`) to one “master” instance’s, or  
  - Run the same sync/copy script (rules + settings) into each instance’s `User/globalStorage` and `User/` as above.
- Skills/MCP in `~/.cursor` are still shared as long as Cursor reads from `$HOME`.

### 4. **Sharing across machines**

- **Skills / MCP / commands**: Sync `~/.cursor` (and related dotfolders) via Git, cloud storage, or dotfiles script.
- **Rules / memories**:  
  - If Cursor has “signed in” sync for rules, that may already sync them.  
  - If not: export the `aicontext.personalContext` value (and any other keys you care about) from `state.vscdb`, store that in your dotfiles or a private repo, and on each machine either restore into `state.vscdb` or use a small script to do it after installing Cursor.

---

## Summary

- **Skills and MCP** live in `~/.cursor` (and siblings); they’re already shared across profiles on one machine. Sync that folder to share across machines.
- **Memory and rules** live in `Application Support/Cursor/User/globalStorage/state.vscdb` and may be per-profile. To share across profiles: use one profile, or symlink one profile’s `User`/`globalStorage` to the others, or copy/sync that DB (or the rules key) into each profile’s `User` data.
- **Settings/keybindings** are in `User/`; same options (single profile, symlink, or copy) apply.

If you tell me whether you use “Profiles: Switch Profile” or multiple `--user-data-dir` (and one machine vs several), I can give a minimal step-by-step (exact paths and commands) for your case.

---

**User**

<user_query>
does this applies for my macbook users? i want to share averything with my other user profile
</user_query>

---

**Assistant**

No. What we talked about was **one macOS user** (one login). Across **different Mac user accounts** (e.g. “Work” vs “Personal” on the same MacBook), nothing is shared by default.

---

## How it works per macOS user

Each macOS user has:

- Their own home: `/Users/yourname` (so `~` is different per user).
- Their own `~/.cursor` → e.g. `/Users/UserA/.cursor` vs `/Users/UserB/.cursor`.
- Their own `~/Library/Application Support/Cursor` (settings, rules, state).

So **skills, MCP, rules, memory, and settings are per macOS user**. Your other Mac user profile does **not** see your current user’s Cursor data unless you explicitly share it.

---

## Ways to share “everything” with your other user profile

You have to put the data in a place both users can use, then point each user’s Cursor at it.

### 1. **Shared folder + symlinks (good for “same config for both users”)**

Use a single copy of the config in a shared location, and make both users use it:

- **Pick a shared location** both users can read (and optionally write), e.g.:
  - `/Users/Shared/CursorShared/`, or  
  - a folder in one user’s home that you explicitly open up for the other user (more fiddly with permissions).
- **Under that shared folder**, mirror what Cursor expects:
  - e.g. `CursorShared/.cursor/` (skills, `mcp.json`, `commands/`, etc.),
  - and either the whole `User` tree or at least the bits you care about (e.g. `User/globalStorage`, `User/settings.json`, `User/keybindings.json`) — you can copy these from your current user’s `~/Library/Application Support/Cursor/User/` once.
- **From each macOS user**, replace their local Cursor data with symlinks to that shared folder:
  - User A:  
    - Back up then replace `~/.cursor` with a symlink to `CursorShared/.cursor`.
    - Optionally do the same for `~/Library/Application Support/Cursor/User` (or only `User/globalStorage` + `User/settings.json` + `User/keybindings.json`) → link to the shared `User` (or those files).
  - User B (your “other user profile”):  
    - Same: symlink `~/.cursor` and (if you want) `User` (or the same subset) to the same shared paths.

Then **both Mac user profiles** use the same skills, MCP, and (if you linked `User`) the same rules/memory and settings. Just make sure the shared directory has permissions so both users can read it (and write if you want both to be able to change rules/settings).

### 2. **One-way copy (simpler, but not live sync)**

- From your main user, copy (or rsync):
  - `~/.cursor` → e.g. `/Users/Shared/CursorShared/.cursor`
  - and optionally `~/Library/Application Support/Cursor/User` (or just `globalStorage` + `settings.json` + `keybindings.json`) into a shared `User` folder.
- In the **other user profile**, either:
  - Replace their `~/.cursor` and `User` with symlinks to that shared copy (same idea as above), or  
  - Periodically overwrite their `~/.cursor` and `~/Library/Application Support/Cursor/User` with a copy from the shared folder (script or manual). Then it’s “shared” but not live—changes in one profile don’t appear in the other until you copy again.

### 3. **Sync via cloud (Dropbox, iCloud, Git)**

- Put `~/.cursor` (and optionally a copy of `User` or just the important files) in a synced folder (e.g. Dropbox) or a Git repo.
- In **each** macOS user:
  - Either symlink `~/.cursor` (and the User data you care about) to that synced location inside their home, or  
  - Run a script on login that copies from the synced folder into `~/.cursor` and `~/Library/Application Support/Cursor/User`.

Then both users get the same “everything” as long as the sync runs and they’re using the same sync folder/repo.

---

## Summary

- **Yes, this applies to your MacBook users:** each macOS user has their own Cursor data; nothing is shared automatically.
- To share **everything** (skills, MCP, rules, memory, settings) with your other user profile, you have to:
  - Put that data in a **shared location** (e.g. `/Users/Shared/CursorShared/`) or a **synced** location, and  
  - In **each** Mac user account, point Cursor at it (symlinks or copy script).

The symlink approach to a shared folder is the one that actually gives both Mac user profiles the same Cursor setup in real time. If you tell me which path you prefer (e.g. `/Users/Shared/CursorShared`), I can outline exact symlink commands for both users step by step (without running them, since you’re in Ask mode).

---

**User**

<user_query>
how can i search files in directly from cursro
</user_query>

---

**Assistant**

Here’s how to search from Cursor:

---

## Search by **file name** (open a file quickly)

- **Mac:** `Cmd + P`  
- **Windows/Linux:** `Ctrl + P`

Type part of the path or name; results are fuzzy-matched. Enter opens the file.

---

## Search **inside files** (text in the whole project)

- **Mac:** `Cmd + Shift + F`  
- **Windows/Linux:** `Ctrl + Shift + F`

Opens the Search panel. Enter your text, optionally restrict to a folder or use regex. Use the gear icon for options (case sensitivity, whole word, exclude folders, etc.).

---

## Search **in the current file only**

- **Mac:** `Cmd + F`  
- **Windows/Linux:** `Ctrl + F`

Find/replace in the active editor.

---

## Command Palette (run any command, including search)

- **Mac:** `Cmd + Shift + P`  
- **Windows/Linux:** `Ctrl + Shift + P`

Type e.g. “Search” or “Go to File” to open the corresponding feature.

---

**Summary:** `Cmd + P` = files by name, `Cmd + Shift + F` = text in all files.

---

**User**

<user_query>
there's a way you can look for file stored in local machine, like diving through all files
</user_query>

---

**Assistant**

Cursor only searches **the folder(s) you have open** (your workspace). To search your whole machine, you have to open a folder that contains everything you care about.

---

## Search “all files” on your machine

**1. Open a top-level folder**

- **File → Open Folder…** (or **Cmd + O** on Mac)
- Choose:
  - **Your user folder** – e.g. `/Users/macm1air` to search everything in your home directory, or  
  - **Root** – `/` to search the whole disk (can be slow and include system files).

**2. Use the usual search**

- **Cmd + P** – find files by name in that folder tree  
- **Cmd + Shift + F** – search text inside all files in that folder

So “diving through all files” = open a big folder (e.g. your home), then use Cmd+P and Cmd+Shift+F.

---

## Keep your project and still search elsewhere

If you want to keep your current project open but also search another place (e.g. home or another drive):

- **File → Add Folder to Workspace…**
- Add e.g. `/Users/macm1air` or any other folder

You’ll have multiple roots in the sidebar. **Cmd + P** and **Cmd + Shift + F** will include all of them.

---

## Optional: narrow search

In the Search panel (**Cmd + Shift + F**), use **“files to include”** or **“files to exclude”** so you don’t search huge dirs (e.g. `node_modules`, `.git`, `Library/Caches`). The gear icon next to the search box opens those fields.

**Summary:** Open the folder you want (e.g. your home) with **File → Open Folder** or **Add Folder to Workspace**, then use **Cmd + P** (by name) and **Cmd + Shift + F** (by content) to search “all files” in that tree.

---

**User**

<user_query>
help me find ~/.cursor
</user_query>

---

**Assistant**

On your Mac, **~/.cursor** is:

**`/Users/macm1air/.cursor`**

(The `~` means your home directory, so it’s the `.cursor` folder inside that.)

---

### How to open it

**In Cursor**

- **File → Open Folder…** (or **Cmd + O**)
- In the path field, press **Cmd + Shift + G** (Go to Folder)
- Type: `~/.cursor` or `/Users/macm1air/.cursor`
- Press Enter, then Open

**In Finder**

- **Go → Go to Folder…** (or **Cmd + Shift + G**)
- Type: `~/.cursor` or `/Users/macm1air/.cursor`
- Press Enter

**In Terminal**

- `cd ~/.cursor` — go into the folder  
- `open ~/.cursor` — open it in Finder  

Because the name starts with a dot (`.`), it’s hidden in Finder unless you use “Go to Folder” or turn on “Show hidden files.”

---

**User**

<user_query>
those files are hidden but i remember i could access them through cursor
</user_query>

---

**Assistant**

In Cursor, **hidden files and folders** (names starting with `.`) are shown in the file explorer when you open a folder that contains them. You don’t need to enable anything special.

---

### Open `~/.cursor` in Cursor

1. **File → Open Folder…** (or **Cmd + O**).
2. In the dialog, press **Cmd + Shift + G** to open “Go to folder”.
3. Type: **`~/.cursor`** or **`/Users/macm1air/.cursor`**
4. Press **Enter**, then click **Open**.

You’ll see the contents of `.cursor` (e.g. `skills`, `projects`, `mcp.json`) in the sidebar. Cursor does not hide them because they start with `.`.

---

### If you open your home folder instead

1. **File → Open Folder…** → **Cmd + Shift + G** → type **`/Users/macm1air`** (or **`~`**).
2. In the sidebar, **`.cursor`** will appear among the other files and folders (including other dotfiles like `.zshrc`).

So you access them “through Cursor” by opening the folder that contains them (e.g. home or `~/.cursor`); the editor then shows those “hidden” items in the tree.

---

**User**

<user_query>
i want to be able to share /Users/macm1air/.cursor across all my macos profiles
</user_query>

---

**Assistant**

You can share one `.cursor` folder for all macOS user accounts by putting it in a shared location and symlinking each account’s `~/.cursor` to it.

---

## 1. Use a shared folder

Use a directory under `/Users/Shared/` so every macOS user can access it:

```bash
# Create shared Cursor config folder
sudo mkdir -p /Users/Shared/CursorConfig
```

---

## 2. Move your current `.cursor` into it (as macm1air)

In Terminal (logged in as **macm1air**):

```bash
# Copy your existing .cursor into the shared folder (keeps your data)
cp -R /Users/macm1air/.cursor/* /Users/Shared/CursorConfig/

# Optional: remove the old .cursor so you can replace it with a symlink
# (Only do this after confirming the copy looks good)
# rm -rf /Users/macm1air/.cursor
```

Then point your account at the shared folder:

```bash
# Back up and remove old .cursor, then symlink to shared
mv /Users/macm1air/.cursor /Users/macm1air/.cursor.backup
ln -s /Users/Shared/CursorConfig /Users/macm1air/.cursor
```

---

## 3. Set permissions so other users can use it

```bash
# Allow all users to read and write (so every profile can use/update it)
sudo chown -R macm1air:staff /Users/Shared/CursorConfig
sudo chmod -R u+rwX,g+rwX,o+rwX /Users/Shared/CursorConfig
```

If you have other admin users who should own files they create there, you can use a shared group later; the above is enough to get sharing working.

---

## 4. Do the same in each other macOS profile

Log in as each other user and run (replace `otherusername` with that account’s short name):

```bash
# If that user already has a .cursor, back it up first
mv /Users/otherusername/.cursor /Users/otherusername/.cursor.backup 2>/dev/null || true

# Symlink to the shared config
ln -s /Users/Shared/CursorConfig /Users/otherusername/.cursor
```

Repeat for every macOS user that should use this shared Cursor config.

---

## Summary

| Step | Action |
|------|--------|
| 1 | `sudo mkdir -p /Users/Shared/CursorConfig` |
| 2 | Copy or move `/Users/macm1air/.cursor/*` into `/Users/Shared/CursorConfig/` |
| 3 | Replace `~/.cursor` with a symlink: `ln -s /Users/Shared/CursorConfig /Users/macm1air/.cursor` |
| 4 | Fix permissions on `/Users/Shared/CursorConfig` so all users can read/write |
| 5 | In each other user account, create the same symlink for their `~/.cursor` |

After this, every macOS profile will use the same Cursor data (skills, MCP, projects, etc.) from `/Users/Shared/CursorConfig`. If two users run Cursor at the same time, they’ll be editing the same files (e.g. same rules/settings); that’s usually fine for a shared “personal” setup across your own profiles.

---
