# Nordic AI Cup 2026｜团队项目

这是我们参加 [Nordic AI Cup 2026](https://github.com/amboltio/Nordic-AI-Cup-2026) 的协作仓库。比赛有三道应用 AI 题目；我们**先做医疗预约题**（`medical-appointment/`），其他题目尚未在这个仓库实现。

## 医疗预约题要做什么

系统收到一段英语医患对话录音和 10 个问题，需要对每题回答“是/否”，并给出录音中支持答案的时间段。评测同时看**答题是否正确**和**证据时间段是否准确**：总分 = 40% 答题准确率 + 60% 证据 tIoU。具体接口、数据格式和比赛限制以[官方题目说明](medical-appointment/README.md)为准。

目前的方案先在本地把录音转成文字，再用文本模型判断问题并寻找证据片段。推理通过 `/predict` 接口提供；评测请求期间不调用云端 AI 服务。

## 现在做到哪一步

- 已有一版能在 Linux CPU 上运行的模型和本地评测脚本。
- 在**公开训练集**的 39 段录音、390 道题上，答题准确率为 **0.841**、证据 tIoU 为 **0.311**、总分为 **0.523**；39 段均成功处理，无失败或超时。
- 这是本地训练集结果，**不是比赛平台成绩**，也不能用来判断最终排名。证据时间段定位仍有改进空间，尤其是 34 道正例没有返回证据片段。

## 仓库怎么读

| 文件 | 用途 |
| --- | --- |
| [AGENTS.md](AGENTS.md) | 团队和 AI 助手的协作规则。 |
| [WORKLOG.md](WORKLOG.md) | 简短的进度与操作记录；接手前先读这里。 |
| [.codex/hooks.json](.codex/hooks.json) | Codex 的自动提醒配置；只做检查，不代替规则或日志。 |
| [.agents/skills/medical-eval/SKILL.md](.agents/skills/medical-eval/SKILL.md) | 医疗题本地评测的团队操作说明；在 Codex 中可指定 `$medical-eval`。 |
| [medical-appointment/README.md](medical-appointment/README.md) | 官方医疗题说明，包含接口和评分细节。 |
| [medical-appointment/RUN_LOCAL.md](medical-appointment/RUN_LOCAL.md) | Linux 本地安装、启动和评测步骤。 |

## 新队友如何开始

1. 克隆本仓库，先读 `AGENTS.md` 和 `WORKLOG.md`。
2. 按官方题目说明准备训练数据：`medical-appointment/data/` 下需要 `question_train.csv` 和 `audio/`。数据**没有**上传到本仓库；可以把该目录链接到自己电脑上存放数据的位置。
3. 按 [Linux 本地运行说明](medical-appointment/RUN_LOCAL.md)创建环境、下载模型、启动接口，再运行本地评测。
4. 完成实质修改后，做相应验证，并在 `WORKLOG.md` 追加一条“日期｜改动｜验证｜下一步”。

请勿提交音频、模型权重、虚拟环境、密钥或个人电脑专属路径。当前数据目录在一位队友的电脑上指向其他磁盘，克隆仓库后不会自动出现。

## 接下来

优先改进证据时间定位，再用独立数据检查效果，并确认部署机器的速度和稳定性。比赛规则或提交方式有疑问时，以[官方仓库](https://github.com/amboltio/Nordic-AI-Cup-2026)和医疗题说明为准。
