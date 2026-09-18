"""Download the two public models before running the local API."""

import sys
from pathlib import Path

from huggingface_hub import hf_hub_download, snapshot_download


if len(sys.argv) != 2:
    raise SystemExit("Usage: python setup_models.py /path/to/model-storage")
root = Path(sys.argv[1]).expanduser().resolve()
asr = root / "whisper-base-en"
nli = root / "nli-minilm"

snapshot_download(
    repo_id="Systran/faster-whisper-base.en",
    local_dir=asr,
    allow_patterns=["config.json", "model.bin", "tokenizer.json", "vocabulary.txt"],
)
for name in ("config.json", "tokenizer.json", "tokenizer_config.json", "onnx/model_quint8_avx2.onnx"):
    hf_hub_download(repo_id="cross-encoder/nli-MiniLM2-L6-H768", filename=name, local_dir=nli)

print(f"ASR_MODEL_DIR={asr}")
print(f"NLI_MODEL_DIR={nli}")
