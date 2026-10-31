@echo off
@rem Run any command with the open project's provider keys from its .env (scripts/run.py); --list shows key names only.
setlocal
call "%~dp0_vf-env.cmd"
"%VF_PYTHON%" "%VF_ROOT%\scripts\run.py" %*
