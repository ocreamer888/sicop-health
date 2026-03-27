# Agent memory

## Learned User Preferences

- When sharing Cursor config across macOS profiles, the other profile must have Read & Write (not read-only) so they can change rules and settings.
- Do not symlink the Cursor User folder (or state.vscdb) across macOS user accounts—both profiles writing to the same DB causes lock/corruption and chat history loss.
- Do not guess, imagine, or suppose; think rationally and objectively.
- Do not over-engineer; prefer the smallest change that solves the problem.

## Learned Workspace Facts

- For Licitacion and dashboard types, `apps/web/lib/types.ts` is the source of truth (DB schema names); `apps/web/src/lib/types.ts` is legacy and may be inconsistent.
- Dashboard amounts: `monto_colones` may hold CRC or USD; use `raw_data.currency_type` to separate when aggregating.
