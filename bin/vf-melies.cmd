@echo off
@rem Melies Cinematic Techniques lookup used by the storyboard skill.
setlocal
call "%~dp0_vf-env.cmd"
"%VF_PYTHON%" "%VF_ROOT%\.claude\skills\storyboard\scripts\melies.py" %*
