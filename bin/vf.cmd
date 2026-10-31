@echo off
@rem video-factory production commands (scripts/videos.py) for PowerShell and cmd; the open folder is the client project.
setlocal
call "%~dp0_vf-env.cmd"
"%VF_PYTHON%" "%VF_ROOT%\scripts\videos.py" %*
