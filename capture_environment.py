import platform
import subprocess

import torch


def safe_git_commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "UNKNOWN"


print("OS:", platform.platform())
print("Python:", platform.python_version())
print("Torch:", torch.__version__)
print("Torch CUDA:", torch.version.cuda)
print("CUDA available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))
    print("GPU capability:", torch.cuda.get_device_capability(0))
else:
    print("GPU: NONE")
    print("GPU capability: NONE")
print("Git commit:", safe_git_commit())
