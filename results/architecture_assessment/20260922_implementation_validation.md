# 模块化实现与验证记录

用户约束：保留全部现有科研特点，不局限于用户举例；优化模块兼容与替换能力。

## 已实现

- 保留 scientific-research-project 入口，增加八个阶段 Skill。
- 五种共享角色契约与五个 Claude 薄适配；通过实际宿主按需调用，不自动创建 Agent 团队。
- 可按能力配置外部 Skill/sub-agent；默认内置方法保持自包含。
- provider resolve/prepare/check-output：记录版本、宿主、根文档和任务映射，核验交接身份/路径/哈希；不授予科学完成或发布权限。
- Codex progress_worker 使用 execution/recovery 路由，保留旧提案格式和原始输出；调用中途相关 provider/契约变化时拒绝直接交付，无关 provider 变化不阻断当前交接。
- 完整归属清单：documentation/FEATURE_PRESERVATION.md；接入说明：documentation/MODULAR_ARCHITECTURE.md 和 references/provider_contract.md。

## 验证

- 重构前 SKILL.md 的编号要求 1–15：15/15 原文保存在共享/设计/执行契约中。
- 原有 12 个 references：11 个未改，research_skill_bridge.md 仅增加 2 行路由说明。
- project_template 未改。
- 9 个 Skill 结构校验通过；本地 Markdown 链接和 Claude Skill 依赖检查通过。
- 105 项 unittest 通过，包含 14 项 provider 交接/worker 测试；运行约 6.2 秒。
- git diff --check 通过。
- 下列核心运行实现与 HEAD 字节一致：

- research_workflow.py
- project_events.py
- supervisor_daemon.py
- supervisor_agent.py
- execution_policy.py
- recovery_policy.py
- budget_policy.py
- systemd_driver.py
- structured_output.py

## 边界

未更新已安装 Skill/Claude 副本、未重启服务、未迁移实际科研项目。现有 pycache 工作区修改保持原样。测试使用隔离临时项目和合成来源/批准/结果、模拟模型 CLI；没有运行真实文献检索、模型推理或在线 Claude/第三方 Agent。科学深度、对话质量和外部工具兼容不能由离线测试证明。

通用 provider 调用由宿主执行，本轮增加的是明确交接契约和检查，不是任意平台的自动执行器。配置版本/host 声明仍需对真实入口和工具进行核实。现有科研完成标准继续由原门槛及实质审阅决定。
