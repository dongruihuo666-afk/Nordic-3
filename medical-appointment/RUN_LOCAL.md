# Linux 本地试跑（医疗题）

在 `medical-appointment/` 目录操作。需要 Python 3（含 `venv`）、网络（仅首次下载模型）和约 1 GB 模型空间。若 Ubuntu 提示缺少 `ensurepip`，先安装 `python3-venv`。数据目录需包含官方 `question_train.csv` 和 `audio/`；不要把音频、模型或密钥加入 Git。

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python setup_models.py /path/on/non-C-drive/models
export ASR_MODEL_DIR=/path/on/non-C-drive/models/whisper-base-en
export NLI_MODEL_DIR=/path/on/non-C-drive/models/nli-minilm
python api.py
```

另开一个终端，在同一目录激活环境并运行 `python local_evaluator.py`。这是本地训练集评测，不会提交到比赛平台。当前实现默认用 CPU；有可用的 NVIDIA GPU 时，可在兼容的 CUDA/cuDNN 环境中设置 `ASR_DEVICE=cuda`、`ASR_COMPUTE_TYPE=float16` 后重新测速度。

2026-09-18 在 Linux CPU 上的本地训练集结果：390 题，准确率 0.841，平均证据 tIoU 0.197，总分 0.455，最慢请求约 14 秒。该分数来自公开训练集，不能代表比赛的隐藏验证或最终评测分数。
