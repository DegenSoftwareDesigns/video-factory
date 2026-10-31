# Shared setup for the vf commands: workshop root, its Python and the default client project.
# Paths are given in native form (pwd -W on Git Bash for Windows) so Python reads them unchanged.
native_pwd() { pwd -W 2>/dev/null || pwd -P; }
VF_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && native_pwd)"
if [ -x "$VF_ROOT/.venv/Scripts/python.exe" ]; then
  VF_PYTHON="$VF_ROOT/.venv/Scripts/python.exe"
else
  VF_PYTHON="$VF_ROOT/.venv/bin/python"
fi
export PYTHONUTF8=1
if [ -z "${VIDEO_FACTORY_PROJECT:-}" ] && [ "$(native_pwd)" != "$VF_ROOT" ]; then
  export VIDEO_FACTORY_PROJECT="$(native_pwd)"
fi
