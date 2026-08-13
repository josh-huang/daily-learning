---
date: 2026-08-13
tags: [langgraph, langchain, agent, deep-research, multi-agent, reasoning, checkpointer]
category: ai
---

# Deep Agent vs Deep Research：LangGraph 架构范式与落地场景

## TL;DR

> Deep Agent 是「底层架构范式」，Deep Research 是用这套范式落地的「典型应用」。Deep Agent = 推理大模型 + LangGraph 状态机 + 多层级子图 + 持久化记忆；Deep Research = 基于 Deep Agent 架构 + 搜索 Tool + 报告合成 Prompt，针对开放性课题做「规划 → 并行搜索 → 反思 → 迭代 → 合成报告」的长流程自主研究。

## 核心概念

- **Deep Agent**：构建复杂 Agent 的深度工程架构理念，非单一 Python 类。用推理模型（CoT）+ 多层级子图 + Checkpointer 持久化支撑长流程任务。
- **Deep Research**：针对复杂/模糊的开放性主题，像分析师一样自主做长时网络探索、交叉验证，最终产出带完整引用的详尽报告。
- **Reasoning LLM**：具备思维链的推理大模型（DeepSeek-R1 / OpenAI o1、o3-mini），调用工具前先深度推理与自我纠错，降低长流程「迷路」与死循环概率。
- **Subgraph（子图）**：多层级图结构，主 Agent（Manager Node）拆解调度，Worker Subgraph 专职执行特定子任务（如代码生成与单测、文档解析）。
- **Checkpointer（检查点）**：LangGraph 的状态持久化机制，任务可运行数小时甚至数天，中断/审批后可完整恢复继续执行。

## 展开

### Deep Research 工作流（LangGraph 状态机驱动的循环）

```
[用户输入复杂课题]
        ↓
[1. Planning 规划/拆解] → 拆为若干子研究方向与提纲
        ↓
[2. Parallel Search 并行搜索] → 多子节点通过搜索 API 检索
        ↓
[3. Reflection 提取与反思] → 信息够不够？有没有盲区？
        ↓
  信息不足？─ YES ─→ 生成新 Query，进入下一轮迭代
        ↓ NO
[4. Synthesis 报告撰写] → 整合数据，生成带引用的长篇报告
```

### Deep Agent vs Deep Research 对比

| 维度 | Deep Agent | Deep Research |
|------|-----------|---------------|
| 定位 | 架构设计模式 / 技术范式 | 具体业务应用 / 落地产品 |
| 解决问题 | 如何构建稳定、可控、处理超复杂长流程的 Agent 系统 | 如何解决复杂信息检索、行业调研、报告撰写 |
| 技术组成 | 推理大模型 + LangGraph 状态机 + 多层级子图 + 持久化记忆 | Deep Agent 架构 + 搜索/爬虫 Tool + 报告合成 Prompt |
| 比喻 | 建高楼的工程标准与框架 | 建出来的图书馆 / 科研楼 |

### Deep Agent 三个维度

1. **结合深度推理模型**：大脑从普通 LLM（如 GPT-4o，倾向立即作答）换成推理模型（CoT），调用工具前先规划与自我反思。
2. **嵌套/多层级图结构**：主 Agent（Manager Node）全局拆解调度，深层 Worker Subgraphs 专职执行子任务，而非简单 ReAct 单循环。
3. **长执行链路与状态持久化**：Checkpointer 支撑 Long-running（数小时/数天），中断或人工审批后可完整恢复。

### LangChain 开源版 Deep Research 的优势

- **完全开源可控**：OpenAI Deep Research 是黑盒；开源版可自定义 LLM（DeepSeek-R1 / Claude）、搜索引擎（Tavily / Perplexity / 本地向量库）、报告模板。
- **Human-in-the-loop**：搜索大纲生成后可暂停等人工确认，再大规模搜索，省 Token。

## 关联

- [[2026-08-07_langchain-agent-seven-steps]] — Agent 从任务边界到生产监控的七步工程化
- [[2026-08-09_context-rot-mitigation]] — Checkpointer / 状态持久化与上下文治理的关系

## 参考

- [LangChain Open Deep Research (GitHub)](https://github.com/langchain-ai/open_deep_research)
- [OpenAI: Introducing deep research](https://openai.com/index/introducing-deep-research/)

---

*Created: 2026-08-13 | Updated: `UPDATE INDEX.md`*
