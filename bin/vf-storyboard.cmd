@echo off
@rem The storyboard skill's board builder (init/build) for the open project.
setlocal
call "%~dp0_vf-env.cmd"
"%VF_PYTHON%" "%VF_ROOT%\.claude\skills\storyboard\scripts\storyboard.py" %*
