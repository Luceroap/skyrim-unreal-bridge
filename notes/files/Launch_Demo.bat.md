## Purpose
Launches the demo.py script using Python 3.12 to initiate the Skyrim-Unreal bridge demo interface. Serves as the primary user-facing entry point for the demo application.

## How it is run
Executed directly via Windows (e.g., double-clicking the batch file or using desktop shortcut "Skyrim Unreal Demo"). Referenced in `HANDOFF_FOR_CURSOR.md` as the one-click launcher for `demo.py`.

## Inputs
None; the batch file contains no command-line arguments or user input requirements.

## Outputs
Console output from `demo.py` until the `pause` command halts execution. No files or shared memory are written by this batch file itself.

## Key functions
Launches Python 3.12 with demo.py  
Uses absolute Python path  
Keeps console window open via pause

## Depends on
`demo.py` (in project root)  
Python 3.12 at `C:\Users\Aidan\AppData\Local\Programs\Python\Python312\`

## Gotchas
Hard-coded user-specific Python path may fail on other machines  
Requires Python 3.12 installed at the specified location  
No error handling for missing dependencies  
Console window requires manual close after execution  
Path references `Aidan` directory, not portable

Source: read, not executed.
