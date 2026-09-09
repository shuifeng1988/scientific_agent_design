# Installation and validation (English)

Canonical source: `~/git/scientific_agent_design`.

## Codex user installation

```bash
SOURCE="$HOME/git/scientific_agent_design/skills/scientific-research-project"
TARGET="$HOME/.codex/skills/scientific-research-project"
mkdir -p "$TARGET"
cp -a "$SOURCE/." "$TARGET/"
python3 "$HOME/.codex/skills/.system/skill-creator/scripts/quick_validate.py" "$TARGET"
```

Restart Codex after installation. Execution location is project-configured; the bundled driver supports CPU/GPU jobs locally or through SSH on remote servers, managed by user-level systemd.

## Supervisor commands

```bash
python3 "$TARGET/scripts/supervisor_agent.py" intake --root /path/to/project
python3 "$TARGET/scripts/supervisor_agent.py" inspect --root /path/to/project
python3 "$TARGET/scripts/supervisor_agent.py" plan --root /path/to/project
```

Use `supervisor_daemon.py` for continuous execution and `tail -f ~/.codex/monitor/status.md` for monitoring.

## Claude Code

```bash
mkdir -p .claude/skills
ln -s ~/git/scientific_agent_design/skills/scientific-research-project .claude/skills/scientific-research-project
```

Detailed protocols are in `skills/scientific-research-project/references/`.
