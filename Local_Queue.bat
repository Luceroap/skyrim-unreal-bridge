@echo off
rem Runs the whole grunt-work queue on your LOCAL model (free). Close Skyrim and Unreal first. Resumable: run it again to continue.
rem Shows what is being worked on and the totals as it goes. Create the file notes\STOP to halt after the current task.
rem Args pass through, e.g.  Local_Queue.bat --limit 5   or   --status   or   --retry-failed
title Local model queue
cd /d "C:\Users\Aidan\SkyrimUnrealBridge"
python tools\make_local_queue.py
python tools\run_local_queue.py %*
pause
