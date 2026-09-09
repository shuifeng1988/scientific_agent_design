# Robin 与 Co-Scientist 设计证据摘录

_用途：记录通用科研智能体蓝图使用的主要公开来源；不作为任何具体科研项目的实验结果。_

---

## 🔗 主要来源

| 来源 | 可复用机制 | 关键限制 |
|---|---|---|
| Co-Scientist Nature paper | Supervisor、异步 worker、Generation/Reflection/Ranking/Evolution/Proximity/Meta-review、持久上下文 | 完整代码未公开；自动评价不是客观真值；文献覆盖和幻觉风险 |
| Robin Nature paper | Crow/Falcon 文献代理、Finch 分析代理、实验反馈闭环、多条分析轨迹 | 人类仍参与候选审查、实验协议和部分数据处理；分析有随机性 |
| Robin GitHub | Python/LiteLLM、Docker、结构化输出目录、可执行 notebook | 部分能力依赖外部 Edison 服务 |
| Finch GitHub | Jupyter-native Python/R/Bash 分析、Docker 环境、逐步执行 | 需要独立结果 QC 与科学审查 |

## 📚 URLs

- https://www.nature.com/articles/s41586-026-10644-y
- https://www.nature.com/articles/s41586-026-10652-y
- https://research.google/blog/accelerating-scientific-breakthroughs-with-an-ai-co-scientist/
- https://arxiv.org/abs/2502.18864
- https://arxiv.org/abs/2505.13400
- https://github.com/Future-House/robin
- https://github.com/Future-House/finch

