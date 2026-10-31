@rem Shared setup for the vf .cmd commands: workshop root, its Python and the default client project.
set "PYTHONUTF8=1"
for %%I in ("%~dp0..") do set "VF_ROOT=%%~fI"
set "VF_PYTHON=%VF_ROOT%\.venv\Scripts\python.exe"
if not defined VIDEO_FACTORY_PROJECT if /I not "%CD%"=="%VF_ROOT%" set "VIDEO_FACTORY_PROJECT=%CD%"
