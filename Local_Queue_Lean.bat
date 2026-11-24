@echo off
rem LEAN setup for the PC's 30B model: 12k context (instead of 32k) and smaller chunks per task, so it reserves ~2 GB less memory.
rem Use this while Windows' paging file is small (see AGENT_BRIEFING / chat notes). Raise the paging file to ~64 GB and Local_Queue.bat is fine again.
rem The runner pauses by itself if free commit memory gets under 1.2 GB (the idle model unloads after 2 minutes), and stops after 15 minutes of that.
title Local model queue (lean)
cd /d "C:\Users\Aidan\SkyrimUnrealBridge"
set OLLAMA_MODELS=D:\Aidan_Moved\ollama_data\models
set OLLAMA_KEEP_ALIVE=2m
set LOCAL_MODEL=qwen3:30b-a3b-12k
python tools\make_local_queue.py
python tools\run_local_queue.py --cap 22000 %*
pause
