---
date: 2026-08-07
tags: [rag, retrieval, agent, context-window, rerank, hybrid-search]
category: ai
---

# RAG/Agent 系统中的检索漂移与上下文污染：三层拦截架构

## TL;DR

> 检索漂移（Retrieval Drift）和上下文污染（Context Contamination）的解法是三层拦截：**多路召回拓广度 + 重排门控控精度 + 历史摘要省 Token**。Hybrid Search 防语义漂移，Cross-Encoder Reranker 做二次过滤，Incremental Summary 避免无关历史噪声污染 Prompt。

## 核心概念

- **检索漂移 (Retrieval Drift)**：纯 Dense Vector 检索在专有名词、实体词上精度不足，召回与 query 语义相关但实际无关的 chunk，导致 LLM 基于错误上下文生成。
- **上下文污染 (Context Contamination)**：多轮对话中，将全量历史直接追加到 Prompt，无关的历史噪声稀释 LLM 注意力、挤占 Context Window 的 tokens。
- **混合检索 (Hybrid Search)**：Dense Vector + Sparse/BM25 并行召回，前者捕获语义关联，后者精准匹配实体词，互补防止专有名词幻觉。
- **Cross-Encoder Reranker**：对召回结果做 Pairwise 二次打分（query-chunk 联合编码），不同于 Bi-Encoder 的独立编码，精度更高但计算开销更大。
- **增量式摘要 (Incremental Summary)**：对历史对话做逐步摘要而非全文追加，压缩噪声同时保留关键信息。

## 展开

### 三层拦截架构

```
Layer 1: Hybrid Search (Recall)
├── Dense Vector (语义泛化)    → Top-K candidates
├── Sparse / BM25 (实体匹配)   → Top-K candidates
└── 合并去重                   → Candidates pool

Layer 2: Rerank & Thresholding (Precision)
├── Cross-Encoder Reranker    → 对每对 (query, chunk) 打分
├── Similarity Threshold      → 过滤低置信度 chunk
└── 输出 Top-N                 → Refined context

Layer 3: Context Summarization (Compression)
├── Incremental Summary       → 历史压缩为 dense 摘要
├── Sliding Window            → 仅保留最近 N 轮原文
└── Final Prompt Assembly     → Static + Summary + Recent + Query
```

### 为什么 Dense Vector 不够？

```
Query: "Apple 的 M4 芯片性能"
Dense: 可能召回 "apple pie recipe" (语义上 cooking + ingredient 相近)
BM25:  精确匹配 "Apple", "M4", "芯片" — 无歧义
→ Hybrid: 取两者交集或加权合并
```

### Bi-Encoder vs Cross-Encoder

| | Bi-Encoder | Cross-Encoder |
|---|---|---|
| 编码方式 | Query 和 Doc 独立编码 | Query-Doc 联合编码 |
| 速度 | 快（可预计算 doc embedding） | 慢（每对实时计算） |
| 精度 | 中等 | 高 |
| 用法 | Recall 阶段 | Rerank 阶段 |

## 关联

- [[2026-08-05_prompt-optimization-long-context-agent]] — Summary Memory 的实现延伸
- [[2026-08-07_rope-rotary-position-embedding]] — 同日记的 RoPE 笔记

## 参考

- [Pinecone: Hybrid Search](https://www.pinecone.io/learn/hybrid-search/)

---

*Created: 2026-08-07 | Updated: `UPDATE INDEX.md`*
