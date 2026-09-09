# Project execution rules

## Compute location

- Unless the task is extremely small (for example, a quick metadata check,
  lightweight file validation, or a short unit test), do **not** run it on the
  local host/workstation. Schedule it on the appropriate remote GPU server:
  H100 (`shuifeng@192.168.237.26`) or V100 (`shuifeng@192.168.236.161`).
- Use H100 for current high-throughput and modern GPU workloads; use V100 for
  the pinned legacy DrugCLIP and Uni-Mol-pocket environments. Record host,
  environment, input hashes, and output paths in the run evidence.
- Local work is limited to lightweight orchestration, code editing, manifest
  checks, hashing, and result aggregation. Do not start CPU-intensive cohort
  materialization, detector runs, model inference, docking, or large-scale
  parsing on the local host.

## Background work

- Every detached, scheduler, long-running, or remote task must be registered
  in `~/.codex/monitor/tasks.json`; confirm a fresh monitor snapshot before
  reporting it as running. Use `tail -f ~/.codex/monitor/status.md` to monitor
  progress.
