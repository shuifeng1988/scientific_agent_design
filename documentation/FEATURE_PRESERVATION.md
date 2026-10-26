# 重构特性保留清单

基线：重构前的核心 SKILL.md、12 个 references、Claude supervisor 指令、progress_worker 提示词、project_template、运行实现和回归测试。用户列举的特点不是特性范围上限。下表区分程序可验证事项与必须通过真实行为/科学审阅判断的事项；不把格式测试当成科学质量保证。

v0.7.0 拆分阶段原则：只改变归属、入口和模块交接；发现表述冲突时不暗中改变行为。当时 runtime、冻结、报告、事件、驱动和模板不变。v0.8.0 的明确治理变更见文末增补。原 SKILL.md 编号 1–15 的要求原文分别保存在 project_contract.md、design_contract.md、execution_contract.md；保留旧编号用于追溯。

| 特性 | 重构后的权威归属 | 验证/边界 |
|---|---|---|
| 五个根文件共同指导科研 | project_contract + 原模板/项目 schema | 模板与 ROOT_DOCS 未改；现有项目各角色仍读五文件 |
| 新方向先理解、分轮澄清、真实等待 | intake_protocol + intake Skill | 协议保留；对话质量需真实行为验证 |
| 1–3 问、简短选项、自由输入、不确定选项 | intake_protocol | 界面能力与用户回答不能由 schema 保证 |
| 方向确认与正式方案批准分开 | intake + design + workflow_contract | 不把草案、默认项或含糊“继续”当作批准 |
| 批准项目续跑不重复索要既有决定 | core + supervisor/worker | 保留 intake 回归与范围判断 |
| 不把安装、说明、框架维护当新研究接洽 | 入口 + intake_protocol | 保留原适用边界 |
| 深度调研有实际多途径检索、日期与窗口 | evidence + deep_research_gate | 原 appraisal 校验继续；两途径不是深度保证 |
| 关键原文、方法/图表定位、访问深度、撤稿更正检查 | evidence + deep_research_gate | 科学审阅；不能用 DOI 匹配冒充全文取证 |
| 支持、零结果、矛盾与独立验证证据 | evidence + core_evidence + reflection | 原来源/反证要求不减 |
| 最相近工作、精确空白、重要性与零结果价值 | design_contract + research_depth | 需要实质论证，不按字数或论文数验收 |
| 传统/当前可复现/前沿方法与数据可行性比较 | evidence + deep_research_gate | 原 appraisal 字段校验 + 内容审阅 |
| 核心主张—原始证据—任务—结果映射 | core_evidence + design/review | 保留计划/外部发现/项目观察/推断区分 |
| 每一步有详细任务卡、子步骤、输入方法统计和输出 | research_depth + 原 01_PLAN 模板 | 模板不变；关键选择缺失需真实讨论 |
| 科学预期不等于承诺正面结果 | research_depth + reflection | 不事后改假设，不把零结果当失败 |
| 五正式文件和方案/调研/决定哈希绑定 | 原 research_workflow.py + design | 原冻结、过期批准与设计漂移测试 |
| 不能静默改 cohort/split/endpoint/纳入排除 | project_contract + 原设计检查 | 原 gate/事件检查；外部 provider 无豁免 |
| Q/task/run 标识、每任务唯一 results 路径 | project_contract + project_schema + registry | 原路径/任务测试；交接限定在任务子目录 |
| 多模型/种子/重试留在原任务路径 | project_schema + execution_first_architecture | 不产生平行正式成果目录 |
| 批准的模型/数据全部覆盖，pilot 不冒充正式 | project_contract + expansion policy | 原完整矩阵/依赖/排除测试 |
| 原始数据/软件/checkpoint 版本、环境、命令和资源 | project_schema + execution | 原 gate 与报告 manifest；真实 provenance 需实测 |
| 下载可靠性、本地中转后远端再次核验 | project_contract + 当前用户规则 | 未启动下载；远端核验不能以本地哈希替代 |
| 方法、结果、结论、解释、表、图、Markdown/Word | project_schema + reporting | 原双语报告、图表来源、Word 内容测试 |
| 表图随已验证批次更新；草稿与正式收据分开 | project_contract + workflow_contract | 原防静默覆盖和同源渲染不变 |
| 失败、缺失、排除保留分母，不编造性能值 | core + worker_contract + reflection | 科学/统计审阅，保留实际失败证据 |
| 预期/观察、不确定性、竞争解释、局限及下一步 | interpretation + reflection_protocol | 真实检索推理；关键词不等于解释有效 |
| 科学异常只暂停受影响分支，独立任务继续 | 原 daemon + reflection | 原科学 hold/独立分支测试 |
| 低风险范围内补证据任务具有依赖与来源 | reflection + execution | 原补充/post hoc 标记、scope/expansion 门槛 |
| 真实 worker 才能分析/解释；daemon 不会科研推理 | core + continuous_execution | 不以命名或文件存在冒充能力 |
| 技术产物可用与正式科学完成分离 | project_contract + execution policy | 原 artifact release/全报告验收测试 |
| 报告/文档故障不拖停独立合格计算 | 原 daemon/outbox | 原 artifact 与发布确认测试 |
| 已授权就绪任务持续推进、资源预留和依赖检查 | execution_contract + 原 daemon/driver | 原资源、依赖、循环和完整面板测试 |
| 固定 job ID、重启核对、未知 SSH 不重复提交 | failure_recovery + 原 daemon | 原 restart/unknown/uncertain submit 测试 |
| 保证故障证据→诊断→修复→最小验证→失败阶段续跑 | recovery Skill + failure_recovery | 原 repair/QC/保留前阶段哈希测试 |
| 每任务/阶段独立 3 修复调用与 3 验证重试 | execution_contract + 原 execution/recovery policy | 原额度/incident 稳定身份测试 |
| 初次执行和正常规划不扣故障额度，保留累计成本 | 原 execution policy | 原预算和规划测试 |
| 两次无进展规划可见 stalled，不无限空转 | execution_contract + 原 daemon | 原 no-progress 测试 |
| 只有明确用户干预能重置指定 incident | failure_recovery + 原 intervene | 原重置范围、未知作业/科学 hold 测试 |
| 监控注册、服务活跃、fresh snapshot、实际子作业 | core/execution + 原监控接口 + 用户规则 | 本轮未操作实际服务；mock 不证明线上运行 |
| 服务健康与项目推进分开、完成需产物验证 | execution_contract + 原 progression | 原状态测试；不凭心跳声称科研进展 |
| durable 事件、幂等重放、发布 hook 确认 | 原 project_events + daemon | 原事件、重复 key、发布确认测试 |
| 会话日志隔离，项目隔离，不读别的会话日志 | core + roles + worker_contract | 当前会话专属日志；未读取旧会话日志 |
| Codex/Claude 共用科研约定，遵守真实平台能力 | core + roles + 平台薄适配 | 离线路由测试；不声称 Claude 常驻链路已在线验证 |
| Linux local/SSH systemd、local lightweight、NVIDIA 探测边界 | execution_contract + 原 driver | 未新增或宣称其他后端/GPU 兼容 |
| 外部 Skill 是方法来源，不是科学证据 | core_evidence + research_skill_bridge | 保留归属、来源、许可和适用范围检查 |
| 外部方法可选，自含规范可独立使用 | modules catalog + provider resolver | 核心独立安装可用；明确指定但缺失时不偷偷替换 |
| 独立审阅不能由同一上下文自称多 Agent 完成 | reviewer role + research_skill_bridge | 记录实际调用方式；离线测试不等于独立科学审查 |
| 旧项目迁移保留冻结记录、编号和成果，不为升级重跑 | core + workflow_contract | 未改 migration 行为；源码更新与项目迁移分开 |
| 已授权修订需实际替换草稿和差异，不能只列建议 | research_depth 第 5 节 + design | 原要求保留；没有自动覆盖冻结文件 |
| 原始输出留存，结构化提案拒绝歧义/截断/重复键 | 原 structured_output + worker | 原输出 decoder 测试继续 |

新增扩展边界：按能力配置 provider、版本/host 显式声明、原始产物与标准产物交接、过期设计/provider 拒绝、跨任务目录拒绝、证据篡改拒绝、缺少调研记录拒绝、provider 不可自行完成/发布。见 test_module_provider.py。

仍需真实任务验证：首轮澄清是否自然、文献是否足够深入、设计是否具有信息价值、图表解释是否准确、独立审阅能否发现科学缺陷、真实 Codex/Claude/第三方工具能否按契约交接。本轮不宣称这些已由单元测试证明。

## v0.8.0 增补与兼容

上表记录 v0.7.0 拆分时保留的特性。v0.8.0 不改变五根文件、真实澄清/批准、计划任务与正式成果映射、方法/表图/结论/Word、检索反证、任务监控及有界恢复。新增审阅收据约束新方案/结果；旧冻结基线不自动升级。批准后的方案修订通过独立事务保存历史版本，不替换已完成证据。补充分析仍在所属任务结果目录下；技术 artifact 不增加 Word 要求。

新的 `reviewing` 状态等待科学工作，不作为技术故障重试；必要补证据阻止正式交付，可选探索仅需登记。第三方方法保留输入、入口和原始输出证据，不获得修改共享状态或批准科学方案的权限。Codex/Claude 保留共同协议，但具体宿主调用与权限仍分别验证。详见[科研治理协议](../skills/scientific-research-project/references/scientific_governance.md)。
