# 安装与验证（中文）

唯一源代码：`~/git/scientific_agent_design`。

## Codex 用户级安装

```bash
SOURCE="$HOME/git/scientific_agent_design/skills/scientific-research-project"
TARGET="$HOME/.codex/skills/scientific-research-project"
mkdir -p "$TARGET"
cp -a "$SOURCE/." "$TARGET/"
python3 "$HOME/.codex/skills/.system/skill-creator/scripts/quick_validate.py" "$TARGET"
```

安装后重启 Codex。项目执行位置由项目配置声明；当前内置 driver 支持本地或 SSH 远程服务器的 CPU/GPU 与 systemd 用户任务。

## Supervisor

```bash
python3 "$TARGET/scripts/supervisor_agent.py" intake --root /path/to/project
python3 "$TARGET/scripts/supervisor_agent.py" inspect --root /path/to/project
python3 "$TARGET/scripts/supervisor_agent.py" plan --root /path/to/project
```

持续执行使用 `supervisor_daemon.py`，监控使用 `tail -f ~/.codex/monitor/status.md`。

## Claude Code

```bash
mkdir -p .claude/skills
ln -s ~/git/scientific_agent_design/skills/scientific-research-project .claude/skills/scientific-research-project
```

详细协议见 `skills/scientific-research-project/references/`。
