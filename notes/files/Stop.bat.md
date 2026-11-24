## Purpose
Stop.bat initiates the shutdown process of the Skyrim-Unreal bridge by triggering the play.py script with a `--stop` command. It serves as a user-friendly interface to gracefully terminate the bridge connection without manual process termination.

## How it is run
The file is executed via command line as `Stop.bat`. It is listed as a launcher in `tools/make_local_queue.py` alongside other entry points like `Play.bat`, but it is not called by other scripts—it is directly invoked by the user or from the launcher menu.

## Inputs
No user inputs; the `--stop` argument is hardcoded in the batch file.

## Outputs
Triggers the `play.py` script to stop the bridge. The main effect is termination of the bridge process (e.g., closing sockets, releasing shared memory), but no direct file output is generated.

## Key functions
- Trigger shutdown via play.py --stop

## Depends on
- `play.py` (must exist in project path)
- Python 3.12 installed at `C:\Users\Aidan\AppData\Local\Programs\Python\Python312\python.exe`

## Gotchas
- Hardcoded Python path; will fail if Python installation path changes.
- Requires `play.py` to handle `--stop` command correctly.
- No error handling for missing `play.py` or Python.
- Path uses Windows-specific backslashes; not cross-platform.
- Requires user to have write access to `play.py`'s working directory.

Source: read, not executed.
