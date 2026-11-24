## Purpose
Applies reviewed docstring suggestions from staging/docstrings/*.txt to source files, ensuring valid function matches and syntax. Operates in dry-run mode by default, showing changes without modifications.

## How it is run
Command: `python tools/apply_docstrings.py` (dry run) or `python tools/apply_docstrings.py --apply` (applies changes). Called directly via command line as documented in `staging/README.md` (line 9).

## Inputs
- Source files listed in `staging/docstrings/*.txt` (e.g., `src/file.py__function.txt` format)
- Actual source files (e.g., `src/file.py`) to modify

## Outputs
- Dry run: Prints insertions without changes
- With `--apply`: Modifies source files and creates `.bak` backups in `staging/docstring_backups/`

## Key functions
Process docstring files
Validate insertion points via AST
Insert docstrings at line positions
Apply changes with backup
Syntax-check new file contents

## Depends on
- `ast` (syntax validation)
- `glob`, `os`, `re`, `shutil`, `sys` (file handling)
- `staging/docstrings/*.txt` (input data)

## Gotchas
- Skips non-existent source files (checks `os.path.exists(rel)`)
- Rejects docstrings >120 chars or containing quotes/backslashes
- Requires no existing docstring (skips if `ast.get_docstring(fn)`)
- Uses `ast.parse` to validate syntax before applying
- Backups stored in `staging/docstring_backups/` with `.bak` extension

Source: read, not executed.
