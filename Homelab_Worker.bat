@echo off
rem Keeps a worker running on the HOMELAB server model for all the tiny tasks. If the server stops answering the worker stops itself
rem (10 failures in a row); this loop waits 10 minutes and starts it again, until you create the file notes\STOP_HOMELAB.
rem Tasks are claimed, so the PC's queue and this worker never do the same task.
title Homelab worker (qwen3:14b-gpu)
cd /d "C:\Users\Aidan\SkyrimUnrealBridge"
:loop
if exist notes\STOP_HOMELAB goto end
python tools\run_local_queue.py --base-url http://<homelab-tailscale-ip>:11434/v1 --model qwen3:14b-gpu --worker homelab --kinds H,K,M,X,N,T,Y,U,A,B,G --cap 4500 --timeout-min 4
if exist notes\STOP_HOMELAB goto end
echo Worker stopped (server busy or finished). Waiting 10 minutes before trying again. Create notes\STOP_HOMELAB to quit.
timeout /t 600 /nobreak >nul
goto loop
:end
echo Stopped.
pause
