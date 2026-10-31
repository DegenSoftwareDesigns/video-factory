@echo off
@rem The workshop's pinned HyperFrames CLI (package-lock.json), run in the current folder.
setlocal
call "%~dp0_vf-env.cmd"
call "%VF_ROOT%\node_modules\.bin\hyperframes.cmd" %*
