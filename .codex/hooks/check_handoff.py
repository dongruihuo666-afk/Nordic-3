"""Warn Codex when the shared handoff files or Git index need attention."""

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def is_local_only(path: str) -> bool:
    parts = [part.lower() for part in path.replace("\\", "/").split("/")]
    name = parts[-1]
    return (
        any(part in {"data", "models", ".venv", "venv", "__pycache__"} for part in parts)
        or name.startswith(".env")
        or name.endswith((".mp3", ".wav", ".pt", ".pth", ".safetensors"))
    )


issues = []
for name in ("AGENTS.md", "WORKLOG.md"):
    if not (ROOT / name).is_file():
        issues.append(f"Missing {name}.")

result = subprocess.run(
    ["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=False
)
if result.returncode == 0:
    indexed = [part.decode("utf-8", "replace") for part in result.stdout.split(b"\0") if part]
    local_only = [path for path in indexed if is_local_only(path)]
    if local_only:
        issues.append("Local data or model files are in Git's index: " + ", ".join(local_only[:5]))
else:
    issues.append("Could not inspect Git's index.")

print(json.dumps({"systemMessage": " ".join(issues)} if issues else {}))
