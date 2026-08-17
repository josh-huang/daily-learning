---
date: 2026-08-17
tags: [structured-output, json-mode, constrained-decoding, grammar, pydantic, llm-engineering]
category: ai
---

# 结构化输出：Constrained Decoding + Pydantic + 自愈降级

## TL;DR

> 生产级 Agent 的 JSON/结构化输出靠三层保证确定性：**引擎层语法掩码**（把 JSON Schema 编译成 FSM/CFG，逐 token 把非法 token 的 logit 掩为 $-\infty$，语法 100% 合规）→ **应用层 Pydantic 校验**业务逻辑 → **渐进式降级**（json_repair/AST 本地修复 + Reflexion 单次重试）。口诀：底层文法掩码保合规，应用层 Pydantic 验逻辑，本地 AST 快速自愈。

## 核心概念

- **Constrained Decoding / 语法掩码**：在推理引擎（vLLM / Outlines / SGLang）把目标 JSON Schema 编译为有限状态机（FSM）或上下文无关文法（CFG），每一步把违反语法的 token 的 logit 置为 $-\infty$，从源头保证输出符合 Schema。
- **Pydantic 强校验**：模型输出合法 JSON 后，再校验业务逻辑约束（数值范围、枚举合法性、正则匹配），区分"语法合法"与"业务合法"。
- **自愈降级（Fallback & AST Repair）**：未开 BNF 约束导致 JSON 截断或微瑕（缺括号、单引号）时，先用 `json_repair`/AST 本地无损修复；仍失败则把错误堆栈喂给修正 Prompt 做单次 Reflexion 重试。

## 展开

### 三层防御各自解决什么问题

| 层 | 手段 | 解决的问题 |
|----|------|-----------|
| 引擎层 | BNF Grammar / FSM 掩码 | 语法 100% 合法（防 Schema 损坏） |
| 应用层 | Pydantic | 业务逻辑合法（枚举/范围/正则） |
| 降级层 | json_repair + Reflexion | 截断/微瑕时的自愈 |

单靠 Prompt 里写"请输出 JSON"不可靠：模型可能输出合法 JSON 但字段类型错，或直接输出非法 JSON。语法掩码保证**结构**，Pydantic 保证**语义**，降级层兜住**边缘**。

### 原理：FSM 掩码

```python
# 伪代码：把非法 token 的 logit 掩为 -inf
valid_tokens = fsm.allowed_next_tokens(current_state)   # 当前语法状态下合法的 token 集合
logits[~mask_for(valid_tokens)] = -float("inf")          # 非法 token 概率归零
```

每个生成步的合法 token 集合由 FSM 当前状态决定，Outlines 通过词汇表预索引把每步成本从遍历整个词表的 $O(N)$ 降到平均 $O(1)$，因此约束解码几乎不增加推理开销。

## 关联

- [[2026-08-07_langchain-agent-seven-steps]] — Structured Output 是"任务边界 → 工具契约"里工具参数 schema 的确定性来源，决定 Agent 能否可靠调用工具
- [[2026-08-07_rag-retrieval-drift-context-contamination]] — 同属"污染防御"的上下游：检索侧拦截脏上下文 vs 生成侧约束输出结构

## 参考

- [Efficient Guided Generation for Large Language Models (Outlines)](https://arxiv.org/abs/2307.09702)
- [vLLM: Structured Outputs](https://docs.vllm.ai/en/latest/features/structured_outputs.html)

---

*Created: 2026-08-17 | Updated: `UPDATE INDEX.md`*
