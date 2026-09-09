# Scientific Research Agent Design（中文说明）

这是一个面向真实科研项目的自动化科研 Skill + Supervisor Agent。它把科研目标、文献调研、方案设计、软件和数据版本、任务依赖、资源调度、执行、质控、结果解释和后续推进组织成可审计的项目闭环。

## 核心优势

- 深度研究门槛：先调研基础与最新工作，再与用户讨论并冻结方案。
- 项目契约：用 `00_PROJECT.md`、`01_PLAN.md`、`02_SOFTWARE.md`、`03_DATA.md`、`04_STATUS.md` 固化目标、计划、环境、数据和状态。
- 完整执行：模型×数据×阶段形成依赖 DAG，不静默遗漏 eligible 单元。
- 可审计结果：每次运行绑定命令、环境、版本、输入输出哈希、QC、表、图和结论。
- 可恢复：失败先保留证据、诊断原因、定向修复、最小验证，再恢复失败阶段。
- 可解释：比较预期与观察，记录不确定性、异常、文献证据和下一步影响。

## 工作流

用户提出问题 → Supervisor 需求访谈 → 初步 `00_PROJECT.md`/`01_PLAN.md` → Deep Research Gate → 用户讨论 → 生成并冻结五个最终根文件 → 注册任务依赖和资源 → 执行 → QC → 文献解读与反思 → 自动推进下一项。

## 执行范围

当前内置 driver 支持：

- 本地电脑 CPU/GPU；
- SSH 连接的远程服务器 CPU/GPU；
- 远程服务器上的 `systemd --user` 任务管理和资源探测。

本项目不声称已内置 Docker、Slurm、云端作业或在线 API 适配器。

## 目录

`skills/scientific-research-project/` 是 Skill；`adapters/claude/` 是 Claude 适配；`project_template/` 是项目模板；`INSTALL.zh-CN.md` 是中文安装说明；英文见 `README.en.md` 和 `INSTALL.en.md`。

当前版本：**0.5.1**。
