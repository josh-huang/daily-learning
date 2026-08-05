---
date: 2026-08-05
tags: [prompt-engineering, kv-cache, prefix-caching, ttft, agent, context-window]
category: ai
---

# 长上下文 Agent 的 Prompt 优化：降低 TTFT 与 API 成本

## TL;DR

> 利用推理引擎的 Prefix Caching (KV Cache) 机制：静态内容前置（System Prompt、Tool Schema）、动态内容后置（用户输入、实时上下文），保持结构稳定避免 Cache Miss，用 Summary Memory 压缩超长历史。核心原理：KV Cache 按前缀匹配，匹配部分零计算复用。

## 核心概念

- **TTFT (Time To First Token)**：从请求发出到第一个 token 生成的延迟。长 Prompt 下 TTFT = KV Cache 未命中部分的 prefill 时间。
- **Prefix Caching**：推理引擎对相同前缀的 token 序列复用已计算的 KV Cache，避免重复 prefill。跨请求生效。
- **KV Cache 命中条件**：两个请求的前缀 token 序列 **逐位完全一致**。任何插入/删除/修改都会导致断裂点之后全部 miss。

## 深入

### 三条优化原则

```
静态前置命中 Cache → 动态后置降低变数 → 结构定型节省算力
```

#### 1. 结构静态化与前置

将**绝对不会变的**放在 Prompt 最前面：

```
┌─────────────────────────────┐
│ System Prompt               │  ← 静态，跨请求不变
│ Tool Definitions (JSON)     │  ← 静态，跨请求不变
│ RAG Context / Documents     │  ← 半静态，可能变
│ Conversation History        │  ← 动态，逐轮追加
│ User Query                  │  ← 动态，放在最后
└─────────────────────────────┘
```

为什么 User Query 放最后？因为前面的全部可以命中 Cache，只需对新增的 user query tokens 做 prefill。

#### 2. 格式规范化

Tool Schema 的 JSON key 顺序必须**每次都一样**。`{"name": "search", "description": "..."}` 和 `{"description": "...", "name": "search"}` 是两个不同的 token 序列，Cache 直接 miss。

```python
# ❌ 错误：Python dict 3.7+ 保序但 key 插入顺序可能变化
tool_schema = {"description": "...", "name": "search"}

# ✅ 正确：固定 key 顺序
import json
TOOL_SCHEMA = json.dumps(
    {"name": "search", "description": "...", "parameters": {...}},
    sort_keys=True  # 强制 alphabetical order
)
```

#### 3. 分层上下文蒸馏 (Summary Memory)

超长对话历史不能全塞进 Context Window。用 LLM 做摘要，把 20 轮对话压成一段 dense 文本：

```
Window Size: 128K
├── Static Prefix:           ~2K  tokens (System + Tools)
├── RAG Context:             ~20K tokens (按需)
├── Summary Memory:          ~5K  tokens (历史摘要，不是原始对话)
├── Recent Messages:         ~10K tokens (最近 3-5 轮保留原文)
└── User Query:              ~1K  tokens
──────────────────────────────────
                            ~38K，留给模型生成的空间充足
```

### 成本量化

假设 Prompt 长度 40K tokens，其中 38K 命中 Prefix Cache：

- Prefill 计算只发生在未命中的 2K tokens → 首 Token 延迟降低约 95%
- API 计费方面：不同厂商策略不同。DeepSeek/Claude 对 cache hit tokens 有折扣

## 关联

- 后续可深入：KV Cache 的底层管理（PagedAttention / vLLM）、不同推理引擎的 Prefix Caching 实现差异

## 参考

- [Anthropic: Prompt Caching (Claude)](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)
- [DeepSeek: Context Caching](https://api-docs.deepseek.com/guides/kv_cache)

---

*Created: 2026-08-05 | Updated: `UPDATE INDEX.md`*
