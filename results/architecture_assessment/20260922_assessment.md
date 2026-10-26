# Supervisor 与 Skill 模块化架构评估

评估日期：2026-09-22。范围：当前仓库、已安装 scientific-research-project 副本的文件一致性，以及入口、worker、调度器与协议的静态检查。未修改实现，未启动科研任务，未做性能或科学质量对照实验。

## 结论

优化方向合理。当前存在入口职责过宽、跨层规则重复和后台 worker 上下文过宽的问题；推荐先形成按需加载的多 Skill，再引入少量、职责清晰的 Agent 角色。保留已有确定性执行内核，不以 Agent 数量作为优化目标。

Skill 是可复用的方法和操作流程，可以覆盖一个连贯工作流，不必小到一个动作。Agent 是执行角色，具有任务、上下文、工具权限和交付责任，可以使用多个 Skill。确定性程序负责调度、校验、状态持久化等可精确执行的机制。三者不应一一对应。

## 用户目的与现有基础

根据 README.zh-CN.md，框架的目标是：从研究目的出发，完成澄清、调研、设计、执行、质控、解释与报告；每项计划任务都有唯一、可追溯的成果目录；已授权工作持续推进；冻结的科学设计不会被技术修复静默改变。

这些目标适合分工，但同时依赖统一状态和证据契约。多 Agent 不能各自维护一份总计划、任务注册表或正式结果。

现有基础值得保留：

- 五个根文档与 Q/task/run 标识、唯一结果路径。
- 12 个 references 文件，已经按澄清、调研、深度设计、恢复、解释、执行等主题组织。
- 调度器、systemd 驱动、执行策略、恢复策略、结构化输出、项目事件和报告工作流已有代码分离。
- 技术产物可用与科学结果正式完成已经区分。
- 重启核对作业、未知远端状态不重复提交、分任务恢复额度、证据哈希和事件发布边界。
- 原始蓝图 SCIENTIFIC_RESEARCH_AGENT_BLUEPRINT_v0.2.md 第 212 行已经提出多智能体角色分工。

## 直接证据与问题

| 位置 | 观察 | 架构含义 |
|---|---|---|
| skills/scientific-research-project/SKILL.md | 61 行，但约 13.95 KB、1,804 个空白分隔词；长段落包含澄清、调研、设计、执行、恢复预算、DAG 展开和报告验收 | 行数低不代表负担低；各阶段仍会加载不相关的入口规则 |
| adapters/claude/scientific-supervisor.md | 58 行、约 7.69 KB；重复了多项 Skill 工作流、质量要求、恢复和执行细节 | 同一规则存在多个维护点，增加未来漂移风险；不据此声称当前全都互相冲突 |
| scripts/progress_worker.py:25–100 | 同一个提示词使用总 Skill，同时处理契约准备与故障修复，并涉及研究深度、报告、解释和依赖展开 | 后台执行角色没有按目的提供精简的技能组合 |
| scripts/progress_worker.py:33 | 要求读取五个根文档 | 单个技术节点也负担全局阅读义务；可改为受版本约束的任务上下文包，并允许按需追溯 |
| scripts/supervisor_daemon.py:279 | 一个 progress_worker 配置和一个 worker 状态槽处理规划/修复 | 已有执行作业并发，不等于已有多个专业推理角色；增加角色文件还需要实际路由与调用适配 |
| scripts/supervisor_daemon.py:448 | worker 请求包含选中节点和全部节点状态 | 大项目可进一步收敛为相关依赖、故障、资源和产物摘要，同时保留全局快照引用 |
| scripts/supervisor_agent.py | intake/inspect/plan/review/reflect 主要提供库存、规则和结构检查 | 文件名中的 agent 不代表独立 LLM 科研角色，不能把它直接算作科研推理智能体 |

已比较仓库 Skill 包与 ~/.codex/skills/scientific-research-project 中对应文件，排除 __pycache__ 后未发现对应文件内容差异。本次未证明各项规则已经导致实际失败、成本增加或科学质量下降；上述是静态架构风险。

## 建议的 Skill 边界

保留 scientific-research-project 作为简洁入口和阶段路由；根据请求加载具体能力，不在总入口复制全文。

| 建议能力 | 主要责任与输出 | 当前可迁移材料 |
|---|---|---|
| research-intake | 澄清目的、范围和未决问题，形成方向摘要 | intake_protocol.md |
| research-evidence | 检索、原始证据提取、冲突证据和方法可行性综合 | deep_research_gate.md、research_skill_bridge.md、core_evidence.md 的证据提取部分 |
| research-design | 假设、对照、统计、详细任务卡和设计修订草案 | research_depth.md、设计冻结流程说明 |
| research-execution | 将已批准任务转为可执行契约，准备领域脚本和输入环境验证 | continuous_execution.md、execution_first_architecture.md 的 worker 部分 |
| research-recovery | 根据故障证据诊断、修复、最小验证并请求恢复失败阶段 | failure_recovery.md |
| research-interpretation | 预期与观察、文献对照、竞争解释、后续分支意义 | reflection_protocol.md |
| research-reporting | 从实际分析和解释产物生成一致的 Markdown/Word/表图 | project_schema.md 的交付规范、workflow_contract.md 的报告部分 |
| research-review | 独立检查设计或结果的实质问题，返回证据和具体整改要求 | research_depth.md 的审阅部分、现有 QC 和证据边界 |

这是候选职责地图，不是要求一次创建八套常驻流程。短小、不能独立复用的内容继续作为 references；专业分析优先使用已安装且适用的领域 Skill。数据与环境准备先作为 research-execution 的模式，出现独立复用需求后再拆分。

共享身份、路径、状态和证据 schema 应有一个权威定义。共享规范随安装包可靠分发；避免跨 Skill 引用不存在的路径，也不要在每个 Skill 内各自复制一套 schema。

## 建议的 Agent 角色

采用一个协调者加少量按需 worker：

| 角色 | 使用能力 | 权限和交付边界 |
|---|---|---|
| Supervisor | 入口路由、用户沟通、阶段交接 | 持有全局目标，协调决定和验收；不重复实现每项领域操作 |
| Researcher | evidence、design、interpretation | 交付来源证据、设计草案或解释；不同阶段可使用不同上下文 |
| Executor | execution、recovery、领域分析 Skill | 交付脚本、执行/修复提案和验证证据；实际长作业由 runtime 提交 |
| Reviewer | review、所需领域 Skill | 根据原始材料审阅，输出通过/修订/需要用户决定及理由；不自行改写被审阅结果 |
| Reporter（按需） | reporting、文档和绘图能力 | 根据已核验材料整理正式报告；草稿可提前生成，正式发布走统一验收 |

先落实 Supervisor、Researcher、Executor、Reviewer 四种角色；报告量大时再将 Reporter 固定为独立角色。角色可复用同一模型，不要求所有角色常驻，也不要求同时执行。独立 Reviewer 调用有助于上下文隔离，但不等于统计独立或不同模型之间的验证。

## 必须先明确的交接协议

每次调用应明确：角色和任务目的、task_id/node_id、批准的设计版本及哈希、相关任务卡、输入/证据引用、允许写入的任务目录、输出 schema、期限和资源/调用限制、验收条件。

业务提案、审阅意见、技术验证和调度状态应分开表示。Agent 返回产物与提案；调度器提交经过校验的执行契约并维护运行状态；事件机制更新受管理文档区块；真实用户决定由外层会话记录并通过已有设计流程落地。

避免多个 Agent 同时修改 registry、state 和五个根文件。代码和权限约束要与文字规则配套。上下文包必须可追溯到当前批准版本，缺少关键科学信息时明确报告缺口，不能为了减少 token 而丢失范围、对照、完整比较对象和失败规则。

## 实施顺序与验收

1. 列出现有规则的唯一归属和各调用入口，消除重复维护；保留兼容入口。
2. 提取独立 Skill 与按需引用，缩短总入口和平台适配文件；暂时沿用现有执行机制。
3. 将 progress_worker 的规划和修复按角色/模式路由，使用版本绑定的任务上下文包与结构化输出。
4. 接入 Researcher 与 Reviewer 的实际调用，先顺序验证交接，再在互不依赖的任务上启用并行。
5. 最后再评估 daemon 内部代码模块化；它的 877 行和约 51 KB 是维护信号，不能单独证明必须拆成多个智能体。

迁移保持 task/run/job 标识、冻结设计、已有结果、失败证据和预算语义。更新 Skill 不自动迁移活跃项目；如需变更运行契约，先核对已运行作业和旧版本兼容。

以真实典型场景检验收益：新项目澄清、单节点技术修复、结果解释、报告失败但独立计算继续、未知 SSH 状态恢复、设计变更请求。比较上下文量、重复读取、调用次数、耗时、任务成功率和具体质量缺陷。还需验证格式正确但科学依据不足的输出会被审阅指出，不能只运行 schema 测试。

预期收益是职责更清晰、上下文更聚焦、可复用性和故障定位更好；代价是交接、路由、版本和并发管理复杂度上升。没有对照验证前，不承诺更便宜、更快或科学上更可靠。

## 本轮边界

本次仅做静态评估并保存报告；未修改 Skill、Agent、运行代码、安装副本或后台服务。现有 tracked pycache 修改保持原样。会话记录：logs/sessions/20260922_204558_architecture_assessment_session.md。
