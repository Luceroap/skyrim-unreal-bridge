# Agent instructions (Codex / ChatGPT)

Read these first, in this order: `AGENT_BRIEFING.md` (rules, layout, commands), the last 30 lines of `notes/AGENT_LOG.md` (what the other agents just did; append one line when you finish something), `HANDOFF_FOR_CHATGPT.md` (your task and hard rules), `README.md`, `COORDINATION.md` (who owns which files; other agents may be editing), then `HANDOFF_FOR_CURSOR.md`.

- Write replies, file names, folder names, code comments, commit messages and chat titles in plain English using only ASCII letters, digits, `_` and `-`. Never use Chinese or other non-English characters in file names.
- Git is local only (no remote, never push). Commit only files you changed, with a clear message. Never `git add -A`, reset, checkout, stash or clean.
- Do not install or download software, create accounts, enter passwords, or change Windows security settings.
- Only one `UnrealEditor.exe` may run at a time; do not minimize Skyrim.
- Free local models (this PC and the homelab server) are described in `LOCAL_MODELS.md`: endpoints, which jobs to send to each, the task-queue launchers, and where results go. Read it before starting grunt work.
