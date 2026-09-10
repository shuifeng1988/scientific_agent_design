# 已安装科研 Skill 的设计比较与借鉴记录

核对日期：2026-09-10 UTC。对象为本机安装快照，不声称已经比较全部科研 Skill、验证远端最新版或完成性能评测。本文件记录来源，不能代替科学研究的文献证据。

## 中文

| 来源 | 已检查内容与版本 | 采用的设计原则 | 不直接移植的部分 |
|---|---|---|---|
| [Cheng-I Wu / academic-research-skills](https://github.com/Imbad0202/academic-research-skills) | Codex academic-research-suite 0.1.15；manifest 上游 commit `17c518b286e48bbcd19fa7d05ec4f7d2aeb01641`；deep-research 工作流、方法设计/综合/反证角色及文献/证据模板 | 研究问题决定方法；来源核验与综合分开；跨研究比较；提交前提出有证据的反驳 | 整套多智能体/Passport/目录体系；按论文数量投票；必须找错、限制连续接受反驳；固定页数或模式带来的无关输出 |
| [K-Dense Inc. / scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) | 本地 literature-review 1.2；安装锁定源 `skills/literature-review/SKILL.md`，folder hash `d301ba750b5956a25d6a99f8ad09340b027b1813`（不是 Git commit） | 分阶段检索、去重、筛选、全文取证、主题式综合、引用核验 | 固定工具/付费服务依赖、强制生成 AI 图、按作者名气/期刊/引用阈值筛掉证据；命令示例未经本项目实测不直接当可运行接口 |
| OpenAI 主机提供的 deep-research-work | 插件缓存 0.1.15 的 deep-research/SKILL.md | 选项式澄清；深入追查初始结果之外的来源；证据充分后形成自包含报告 | 固定输出页数、平台专用工具及不适合科研审计的省略方法记录习惯 |

采用方式：自行编写本项目规范，增加研究意义论证、逐任务证据设计和四个可见审阅阶段，入口为 `references/research_skill_bridge.md`，具体要求见 `research_depth.md` 与 `deep_research_gate.md`。外部 Skill 仅作为可选方法提供者，不取得本项目目录、审批或调度的控制权。没有复制第三方原文、代码或模板，也没有新增外部 API 或自动多智能体运行。

许可处理：ARS 本地 LICENSE 标明 Copyright (c) 2026 Cheng-I Wu、CC BY-NC 4.0，本次不直接纳入其文件；literature-review 的本地头信息标明 MIT，未额外核验/打包完整许可，因此也不复制；主机插件的已检查文件夹未见明确再分发许可。没有给本项目添加非商业许可或代替用户选择项目许可证。来源署名不是所有复制行为的许可替代品。

评价边界：方法规则的优点是人工比较所得，不代表执行效果已被实验验证。期刊声望、来源数量和检索返回数量不能替代测量质量、偏倚、独立性和对当前问题的适用性。真实研究仍须实际检索、核读原文、记录证据并接受审阅。

## English

Reviewed on 2026-09-10 UTC against installed snapshots, not every available research skill or verified latest upstream releases. This records design provenance, not scientific literature evidence or a performance benchmark.

ARS (Cheng-I Wu; Codex adapter 0.1.15, upstream commit above) informed the separation of question/method alignment, source checking, synthesis and critical review. K-Dense literature-review 1.2 informed staged retrieval, screening, full-text evidence extraction and thematic synthesis. The host-provided deep-research-work 0.1.15 informed choice-assisted scoping, following evidence beyond initial results and self-contained reporting.

The integration is independently written in research_skill_bridge.md, research_depth.md and deep_research_gate.md. Providers are optional methods, not alternative project owners. No upstream code, prompt or template is copied; no new API or automatic multi-agent runtime is enabled. We deliberately do not adopt paper vote-counting, prestige-based inclusion, mandatory defect quotas, mandatory AI figures, universal page counts or unverified CLI examples.

Observed licensing: ARS specifies CC BY-NC 4.0 and Copyright (c) 2026 Cheng-I Wu; K-Dense local metadata declares MIT but complete redistribution notices were not independently bundled; no explicit redistribution license was found in the inspected host-plugin folder. No third-party files are vendored and no noncommercial restriction or new project license is introduced. Any later copying requires a scoped license review and retained attribution/notices. This is a conservative integration decision, not legal advice or a claim of provider endorsement.

## Inspected file fingerprints / 已读文件指纹

Hashes identify the local files actually inspected; they do not prove equivalence to the current upstream repository.

| Local package-relative file | SHA-256 |
|---|---|
| ARS `ars/deep-research/WORKFLOW.md` | `3a6d1fa662857068376a1b507143618401febea272321a2d5a70daefafd2893c` |
| ARS `ars/deep-research/agents/research_architect_agent.md` | `b2b869f2312cec860f6023f23921e36602898993c8eba530ec0654a60166c3c6` |
| ARS `ars/deep-research/agents/devils_advocate_agent.md` | `f1affcd163b081ed10b6ba0c31e2029f0f821b43b8201ac0b25622aba211e682` |
| K-Dense `literature-review/SKILL.md` | `bd2db633e1565f4a25af55ff78cff668b791685b93f1558166320701ff564980` |
| Host `deep-research-work/0.1.15/skills/deep-research/SKILL.md` | `fe92f226b47314a3963738a7b98d5afc5d51973c7b589c72277e3cc9e59d44eb` |
