## Purpose
Assembles local model notes into compact, deterministic files for strong agents (non-LLM systems). Generates `FILE_MAP.md` detailing file purposes and `REVIEW_LEADS.md` listing review findings ranked by confidence.

## How it is run
Command: `python tools/build_briefing.py`. Called by `tools/run_local_queue.py` (via `subprocess.run` as shown in `git grep` output).

## Inputs
- `notes/files/*.md` (purpose descriptions)
- `notes/review/*.md` (review findings)
- `notes/index/symbols.json` (optional, fallback to empty dict on error)

## Outputs
- `notes/FILE_MAP.md` (file map with purposes and function counts)
- `notes/REVIEW_LEADS.md` (review leads ranked by confidence and category)

## Key functions
- FILE_MAP generation
- REVIEW_LEADS generation

## Depends on
- `notes/files/*.md`
- `notes/review/*.md`
- `notes/index/symbols.json`
- Standard libraries: `glob`, `json`, `os`, `re`

## Gotchas
- REVIEW_LEADS entries are explicitly UNVERIFIED; must be confirmed in code before acting.
- FILE_MAP flags files containing 'unsure' (marked as `[contains 'unsure']`).
- Purpose descriptions in FILE_MAP are truncated to 300 characters.
- Review lead descriptions in REVIEW_LEADS are truncated to 420 characters.
- FILE_MAP includes exact function counts from `notes/index/symbols.json` (falls back to 0 if missing).

Source: read, not executed.
