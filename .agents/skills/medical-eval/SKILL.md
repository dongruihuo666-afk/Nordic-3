---
name: medical-eval
description: Run or analyze the Nordic AI Cup medical-appointment local evaluation when asked to score a model change, compare runs, or investigate wrong answers and evidence spans. Do not use for platform submissions.
---

# 医疗预约题本地评测

本 skill 只复用仓库已有的 `medical-appointment/local_evaluator.py`。先读项目根目录的 `AGENTS.md`、`WORKLOG.md`，以及 `medical-appointment/RUN_LOCAL.md`；题目接口和评分细节以 `medical-appointment/README.md` 为准。

## 运行

1. 确认 `medical-appointment/data/` 中有 `question_train.csv` 和 `audio/`，本机 Python 环境已按 `RUN_LOCAL.md` 准备，`ASR_MODEL_DIR` 与 `NLI_MODEL_DIR` 指向本地模型。缺少数据或模型时，说明具体缺项和准备方法，不编造分数。
2. 在 `medical-appointment/` 启动 `python api.py`；另开终端在同一目录运行 `python local_evaluator.py`。排查单题时才加 `--verbose`。评测完成后关闭本次启动的服务。
3. 记录题数、答题准确率、平均证据 tIoU、总分、未返回证据的正例数、失败请求、超时和最慢请求时间。与 `WORKLOG.md` 中最近一次同一公开训练集结果比较，并说明改动可能影响了哪一项。遇到失败或超时，要如实报告，不能只报总分。

## 交接

- 公开训练集结果只代表本地开发，不能写成隐藏验证集、比赛平台或最终排名成绩。需要独立验证时明确标记数据来源。
- 有实质模型改动或新的有效评测结论时，按 `WORKLOG.md` 的格式追加一条简短记录；只记改动、验证和下一步，不贴完整终端输出。
- 不提交音频、模型权重、虚拟环境、密钥或机器专属路径。调用本 skill 本身不授权平台提交、GitHub 推送或云端 AI 推理。
