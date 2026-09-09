# 安装与验证说明 / Installation and validation

本文件说明如何在 Codex 和 Claude Code 中安装、更新和验证本 Skill 与 Supervisor。
This document explains how to install, update, and validate the Skill and Supervisor in Codex and Claude Code.

## 快速开始 / Quick start

唯一源代码目录 / Canonical source: `~/git/scientific_agent_design`. Codex 用户级安装 / Codex user-level installation:

```bash
SOURCE="$HOME/git/scientific_agent_design/skills/scientific-research-project"
TARGET="$HOME/.codex/skills/scientific-research-project"
mkdir -p "$TARGET"
cp -a "$SOURCE/." "$TARGET/"
python3 "$HOME/.codex/skills/.system/skill-creator/scripts/quick_validate.py" "$TARGET"
```

安装后请重启 Codex/Claude Code。After installation, restart Codex/Claude Code. Heavy computation belongs on declared H100/V100 servers.

## v0.5.1 常驻模式（当前入口）

唯一源代码目录为 `~/git/scientific_agent_design`；将其中 `skills/scientific-research-project/` 同步到 `~/.codex/skills/scientific-research-project/`。服务器驱动使用绝对路径，避免误用旧副本。

1. 在项目 `registry/supervisor.json` 填写依赖节点与 host 资源上限，执行契约格式见 [continuous_execution.md](skills/scientific-research-project/references/continuous_execution.md)。未写完的 contract 必须留空并显示阻断，不能以 true 命令伪装科学任务。
2. 用下面命令检查 DAG 并安装常驻服务（使用现有用户 SSH/CLI 登录；不修改账号凭据）：

```bash
python3 ~/git/scientific_agent_design/skills/scientific-research-project/scripts/supervisor_daemon.py check --root /absolute/project
python3 ~/git/scientific_agent_design/skills/scientific-research-project/scripts/install_supervisor_service.py --root /absolute/project --start
tail -f ~/.codex/monitor/status.md
```

安装器输出项目专属 `scientific-supervisor-<hash>.service`。它每 30 秒扫描，崩溃 30 秒后重启。更详细的逐节点依赖、phase、失败、等待原因见项目 `04_STATUS.md` 与 `provenance/supervisor/status.md`。`systemctl --user stop SERVICE` 停止调度器；已经提交到远程的作业仍由远程调度器管理。新提交暂停文件是项目 `provenance/supervisor/PAUSE`；恢复时移走该文件。

常驻服务登录后自启；注销后保持运行须 `loginctl show-user "$USER" -p Linger` 为 yes。不声称操作系统关机时本机守护进程仍能运行。

## 配置主动推进 worker

在 supervisor.json 增加以下配置，并定义 local host 的 systemd_driver 与轻量资源限额。开启表示授权已有研究范围内的后台 Codex 调用，使用当前账户额度。v2 默认每个任务/阶段每轮最多 3 次修复调用和 3 次重试；首次运行与正常规划不消耗失败额度。每次调用最多 30 分钟，连续 2 次无可执行进展显示 stalled。规划可补齐契约或在预授权 expansion_policy 内展开完整模型矩阵，不改变科学 scope。发生预算、网络、身份验证或科学决定阻断，状态表显示具体原因。

```json
{
  "execution_policy": "v2",
  "progress_worker": {
    "enabled": true,
    "argv": ["/usr/bin/python3", "/home/USER/git/scientific_agent_design/skills/scientific-research-project/scripts/progress_worker.py"],
    "batch_size": 1,
    "max_no_progress_visits": 2,
    "budget_scope": "per_node",
    "max_worker_calls_per_round": 3,
    "priority_nodes": ["Q01.02"],
    "cooldown_seconds": 600,
    "failure_backoff_seconds": 1800,
    "timeout_seconds": 1800
  }
}
```

内置推进 worker 使用本机已验证的 `codex exec --approve-for-me --output-last-message`，保持自动审批与沙箱策略；不使用 bypass。它调用当前配置的模型，不自动指定另一个模型。官方非交互入口：[Codex non-interactive mode](https://developers.openai.com/codex/noninteractive/)。Claude 使用相同阶段/driver JSON 协议，但需配置对应 CLI worker；不能把 Codex worker 当成已验证的 Claude 后台执行器。

测试：

```bash
python3 -B -m unittest discover -s ~/git/scientific_agent_design/skills/scientific-research-project/scripts -p 'test_*.py' -v
```

以下单次模式安装示例保留用于兼容；legacy execute 和仅凭 README 关键词自动发出 qc.passed 已禁用，正式运行请使用上面的 daemon。

v0.5.0 更新后重启项目常驻服务。当前使用每任务独立额度，项目总调用次数仅用于审计。
v2 的失败额度按稳定任务/阶段计数：3 次修复调用、3 次验证后重试，首次执行不计；legacy 配置仍保留旧 max_attempts 语义。详见执行优先架构文档。
人工明确要求修复/继续某任务时，执行一次下列维护流程（不要因查询进度而重置）：

```bash
systemctl --user stop scientific-supervisor-PROJECT_HASH.service
python3 -B ~/git/scientific_agent_design/skills/scientific-research-project/scripts/supervisor_daemon.py intervene \
  --root /absolute/project --node Q01.02.materialize_splits --reason '用户明确要求修复并继续此任务'
systemctl --user start scientific-supervisor-PROJECT_HASH.service
```

将服务名与 node 替换成项目实际值。命令需独占调度锁；目标作业须确认已终止，
未知状态、活跃目标 worker、冻结结果和科学异常不会因重置而放行。
重置记录保存在 `provenance/supervisor/interventions/`，状态表显示累计次数和本轮额度。
每次失败仍先诊断、针对性修复、最小验证，只重试失败 phase。
详见 [failure_recovery.md](skills/scientific-research-project/references/failure_recovery.md)。

本目录是唯一源代码目录。安装时请复制或链接本目录中的
`skills/scientific-research-project/`，不要在 Codex 或 Claude 的副本中单独修改实现。

## 1. Codex

### 用户级安装

```bash
SOURCE="$HOME/git/scientific_agent_design/skills/scientific-research-project"
TARGET="$HOME/.codex/skills/scientific-research-project"

mkdir -p "$TARGET"
cp -a "$SOURCE/." "$TARGET/"
```

验证：

```bash
python "$HOME/.codex/skills/scientific-research-project/scripts/supervisor_agent.py" \
  inspect --root /path/to/your/scientific-project
```

更新副本时，仍从唯一源代码目录执行同一组 `cp -a` 命令。更新后重新打开 Codex。

### Supervisor 模式

```bash
python "$HOME/.codex/skills/scientific-research-project/scripts/supervisor_agent.py" intake  --root PROJECT
python "$HOME/.codex/skills/scientific-research-project/scripts/supervisor_agent.py" inspect --root PROJECT
python "$HOME/.codex/skills/scientific-research-project/scripts/supervisor_agent.py" plan    --root PROJECT
python "$HOME/.codex/skills/scientific-research-project/scripts/supervisor_agent.py" review  --root PROJECT
python "$HOME/.codex/skills/scientific-research-project/scripts/supervisor_agent.py" reflect --root PROJECT --task-id Q01.01
```

旧 `execute` 已禁用；正式执行使用上面的常驻服务，并校验执行契约、目标服务器及现有授权范围。

## 2. Claude Code

### 项目级 Skill

在科研项目根目录执行：

```bash
mkdir -p .claude/skills
ln -s /path/to/Project_Benchmarking_molecular_representation/scientific_agent_design/skills/scientific-research-project \
  .claude/skills/scientific-research-project
```

也可以使用复制而不是链接：

```bash
cp -a /path/to/Project_Benchmarking_molecular_representation/scientific_agent_design/skills/scientific-research-project \
  .claude/skills/scientific-research-project
```

启动 Claude Code 后使用 `/skills` 检查，或直接输入：

```text
/scientific-research-project
```

### Claude Supervisor 子 Agent

在项目中创建 `.claude/agents/scientific-supervisor.md`，内容可使用：

```markdown
---
name: scientific-supervisor
description: Supervises auditable scientific projects and guards intake, planning, execution, QC, review, and reflection.
tools: Read, Glob, Grep, Bash
model: sonnet
permissionMode: default
skills:
  - scientific-research-project
---

你是项目级 Scientific Supervisor。工作前读取 00_PROJECT.md、01_PLAN.md、02_SOFTWARE.md、03_DATA.md 和 04_STATUS.md。

必须遵守：不静默改变冻结设计；所有任务对应 registry/tasks.tsv；结果必须包含 README、Word、表、图、QC、反思和 evidence hash；重计算只能提交到项目登记且获授权的执行后端；可为本地 CPU/GPU、远程服务器/集群、容器、云端作业或在线 API。用户已授权范围内的常规下载、提交及有限技术重试无需逐次询问；停止无关进程、破坏性覆盖及重大设计修改需要另行明确授权。

优先调用：

```bash
python scientific_agent_design/skills/scientific-research-project/scripts/supervisor_agent.py inspect --root .
```

根据用户请求使用 `intake`、`inspect`、`plan`、`review` 或 `reflect`；持续执行使用 `supervisor_daemon.py`，不要调用已禁用的旧 `execute`。
```

然后重启 Claude Code，并请求：

```text
Use the scientific-supervisor subagent to inspect the project and identify the next auditable task.
```

### 个人级安装

如果希望所有 Claude Code 项目都能使用 Skill：

```bash
mkdir -p "$HOME/.claude/skills"
ln -s /path/to/Project_Benchmarking_molecular_representation/scientific_agent_design/skills/scientific-research-project \
  "$HOME/.claude/skills/scientific-research-project"
```

个人级 Supervisor 放在：

```text
~/.claude/agents/scientific-supervisor.md
```

但 Supervisor 中依赖五个根文档和项目 `registry/`，因此更推荐项目级安装。

## 3. 安装后检查清单

```bash
test -f .claude/skills/scientific-research-project/SKILL.md
test -f scientific_agent_design/skills/scientific-research-project/scripts/supervisor_agent.py
for f in 00_PROJECT.md 01_PLAN.md 02_SOFTWARE.md 03_DATA.md 04_STATUS.md; do test -f "$f" || exit 1; done
python scientific_agent_design/skills/scientific-research-project/scripts/supervisor_agent.py inspect --root .
```

如果当前会话没有发现新建的 Skill 或 Agent，关闭并重新打开 Codex/Claude Code。

## 4. 版本同步原则

```text
scientific_agent_design/       唯一源代码
        ├──> ~/.codex/skills/  Codex 用户级副本
        └──> .claude/skills/   Claude 项目级副本
```

每次修改 Skill 或 Supervisor 后，重新执行同步命令，并运行安装后检查清单。副本只用于运行，不用于开发。
