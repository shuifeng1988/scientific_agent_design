# Scientific Research Agent Design

> **Auditable · Explainable · Reproducible · Continuously Executable**  
> **可审计 · 可解释 · 可复现 · 持续执行**

本项目是一个面向真实科研工作的通用 Skill + Supervisor Agent 框架。它不是单纯的聊天机器人，也不是只会提交作业的调度器，而是把“提出问题—深度调研—制定方案—配置环境与数据—执行—质控—解释—反思—推进下一步”固化为可追踪的科研工作流。

This project provides a general-purpose Skill and Supervisor Agent for real scientific workflows. It is not merely a chatbot or a job scheduler: it turns the complete research loop—question, literature appraisal, protocol design, software/data preparation, execution, QC, interpretation, reflection, and next-step planning—into a traceable, restartable system.

## 项目做什么 / What it does

- 用五个根文档明确项目目标、计划、软件、数据和状态。
- 在冻结新方案前强制进行基础与最新研究的深度文献调研。
- 将模型×数据×阶段展开为带依赖、资源和证据要求的 DAG。
- 按项目声明的执行后端运行任务，可为本地 CPU/GPU、远程服务器或集群、容器环境、云端作业或在线 API；不得把特定显卡写成通用要求。
- 失败时保留证据，诊断原因，定向修复，最小验证后只重跑失败阶段。
- 每个结果都生成方法、数据来源、软件版本、哈希、QC、表、图和人类可读结论。
- 比较观察结果与预期，并评估是否需要补充证据或改变后续任务。

- The five root documents make project intent, plan, software, data, and status explicit.
- A mandatory deep-research gate surveys foundational and recent work before plan freeze.
- The complete model × dataset × stage matrix becomes a dependency/resource/evidence-aware DAG.
- Execution is dispatched to the backend declared by each project: local CPU/GPU, remote server or cluster, container/VM, cloud job, or online API. Local execution is allowed when declared and appropriate.
- Failures follow preserve evidence → diagnose → targeted repair → minimal verification → phase resume.
- Each result package contains methods, data provenance, software versions, hashes, QC, tables, figures, and readable conclusions.
- Observations are compared with preregistered expectations, with downstream scientific impact assessed.

## 架构 / Architecture

```mermaid
flowchart TD
  A[User proposes research question] --> B[Supervisor intake + discussion]
  B --> C[Draft 00_PROJECT / 01_PLAN]
  C --> D[Deep Research Gate]
  D --> E[User discussion and plan freeze]
  E --> F[Generate final 00_PROJECT / 01_PLAN / 02_SOFTWARE / 03_DATA / 04_STATUS]
  F --> G[Dependency and resource DAG]
  D --> E[Resident Supervisor]
  E --> F[Declared backend: local GPU/CPU, remote cluster, container, cloud, or API]
  F --> G[Hash/QC/evidence validation]
  G --> H[Literature-grounded interpretation]
  H --> I{Expected? Scientifically useful?}
  I -->|yes / add evidence| D
  I -->|strong anomaly| J[Hold affected branch + user discussion]
```

核心组件 / Components:

1. `scientific-research-project` Skill：定义科研契约、深度研究门槛、证据和反思规则。
2. Supervisor Agent：执行 intake、inspect、plan、review、reflect。
3. Resident Supervisor Daemon：持续监控、资源感知调度、依赖释放和有限重试。
4. Project template：提供 `00_PROJECT.md`–`04_STATUS.md`、registry、provenance、results 结构。

## 核心 Skill 工作流 / Core Skill workflow

1. **Intake / 需求理解**：识别研究目的、科学决策、假设、对象、数据、模型、终点、约束和预期；记录高影响待决问题。
2. **Draft / 初步方案**：与用户讨论后，仅生成初步 `00_PROJECT.md` 和 `01_PLAN.md`，明确问题边界与候选分析。
3. **Deep research gate / 深度研究门槛**：检索基础及最新文献，建立证据图谱，比较常规、当前和前沿方法，评估意义、创新性、可行性、资源和信息增益。
4. **User decision / 用户决策**：向用户呈现研究价值、方法选项、风险和 go/no-go 或分阶段建议；记录确认、异议和修改。
5. **Freeze / 正式冻结**：确认后才生成最终五个根文件、registry、数据/软件版本、split、统计、排除和资源契约。
6. **Execute / 执行**：将完整 eligible 模型×数据×阶段展开为 DAG，在项目声明的本地、远程、容器、云端或 API 后端运行。
7. **Recover / 故障恢复**：保留日志和哈希，诊断原因，定向修复，最小验证，只恢复失败阶段，并限制任务级重试额度。
8. **QC and release / 质控发布**：核对输入输出哈希、行数、环境、失败表、表图和报告；artifact readiness 与 scientific release 分离。
9. **Interpret and reflect / 解读反思**：比较预期与观察，检索支持和冲突证据，解释异常和限制，判断后续任务价值，必要时提出补充证据或用户讨论。
10. **Continue / 持续推进**：依赖和资源满足即调度下一节点；所有状态、事件和结果路径持久化，支持中断后恢复。

## 主要优点 / Key advantages

- **可审计 / Auditable**：每次下载、运行、失败、修复和结论都有事件与哈希证据。
- **不漏模型 / Complete coverage**：正式 benchmark 不得静默缩小 eligible 模型面板。
- **可解释 / Explainable**：结果必须说明数据、方法、预期、异常、文献支持和限制。
- **可迁移 / Portable**：服务器、环境、checkpoint、资源和命令均登记，可迁移到其他项目。
- **可恢复 / Recoverable**：任务级失败预算、幂等重试、断点续跑，不盲目重算。
- **持续推进 / Continuous**：依赖满足且资源可用时自动启动后续任务，并区分 daemon 健康和科研进展。

## 目录 / Repository layout

```text
README.md                         # 中英双语总览 / bilingual overview
INSTALL.md                        # Codex / Claude 安装与验证
skills/scientific-research-project/
  SKILL.md                        # Skill 入口
  references/                     # 深度研究、失败恢复、执行协议
  scripts/                        # Supervisor 与验证脚本
adapters/claude/                  # Claude 适配
project_template/                 # 五个根文档模板
 documentation/                   # 架构说明、图、DOCX、PDF
archive/                          # 只读历史版本
```

## 版本 / Version

当前版本 / Current release: **0.5.1**。安装方法见 [`INSTALL.md`](INSTALL.md)。深度研究门槛见 [`deep_research_gate.md`](skills/scientific-research-project/references/deep_research_gate.md)。
