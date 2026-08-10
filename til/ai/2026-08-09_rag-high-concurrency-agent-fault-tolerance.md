---
date: 2026-08-09
tags: [rag, agent, system-design, tool-calling, fault-tolerance, self-correction, caching, hybrid-search]
category: ai
---

# 高并发 RAG 系统设计与 Agent 容错：从架构到面试

## TL;DR

> 高并发 RAG 系统 = **Semantic Cache（语义缓存兜底）+ Hybrid Search（混合检索防漂移）+ Cross-Encoder Rerank（重排提精度）+ SSE Streaming（流式提体验）**。Agent 容错 = **Schema 校验（本地拦截）+ Reflexion Loop（报错回抛促自修正 2-3 次）+ Fallback 降级（兜底保可用）**。

## 核心概念

- **Semantic Caching**：对 Query 做语义相似度匹配（如 Redis Vector / GPTCache），相似度 > 0.95 直接返回缓存，绕过检索+生成，延迟秒级→毫秒级，成本→0。
- **Reflexion Loop**：Tool 执行抛异常时，将 Error Traceback + 原始参数重新包装进 Prompt 喂回 LLM，触发自我纠错重试（上限 2-3 次）。
- **Graceful Degradation**：达到重试上限后切换备用 Tool / 返回缓存 / 向用户提示具体失效原因，避免整条 Agent 链路崩塌。
- **Sliding Window + Summarization**：保留最近 N 轮原文，早期对话用轻量模型做生成式摘要压缩，防 Context OOM。

## 展开

### RAG 高并发低延迟四层架构

```
Layer 1: 接入层 (Latency Control)
├── Semantic Caching: Redis Vector / GPTCache
├── 相似度 > 0.95 → 直接返回（毫秒级）
└── Miss → 进入检索层

Layer 2: 检索层 (Retrieval Optimization)
├── Hybrid Search: Dense Vector + BM25
├── HNSW 向量索引（毫秒级检索）
└── 兼顾语义泛化与实体精确匹配

Layer 3: 重排与压缩层 (Rerank & Compression)
├── Cross-Encoder (BGE-Rerank): Top-K(30) → Top-5
├── LLMLingua 上下文压缩：去噪减 Token
└── 提高 LLM 生成速度 + 降低成本

Layer 4: 生成层 (LLM Streaming & Concurrency)
├── SSE (Server-Sent Events) 流式响应 → 降低 TTFT 体感
├── 异步 I/O 并行拉取数据
└── 自建部署: vLLM / TensorRT-LLM (PagedAttention + Continuous Batching)
```

### Agent Tool Call 容错三层防护

```
┌──────────────────────────────────────────┐
│ Layer 1: Schema 校验 (本地)               │
│ Pydantic / JSON Schema 静态校验            │
│ 类型错误、必填缺失 → 本地拦截，不浪费 LLM 调用 │
├──────────────────────────────────────────┤
│ Layer 2: Reflexion Loop (2-3 次)          │
│ Tool 执行异常 → Error Traceback 喂回 LLM    │
│ → LLM 自我纠错重新生成参数                   │
├──────────────────────────────────────────┤
│ Layer 3: Fallback 降级                     │
│ 重试耗尽 → 备用 Tool / 缓存结果 / 提示用户    │
│ 避免整条 Agent 链路崩塌                      │
└──────────────────────────────────────────┘
```

### 超长上下文管理策略

| 策略 | 机制 | 效果 |
|------|------|------|
| Sliding Window | 保留最近 N 轮原文 | 保证近期对话精度 |
| Summarization | 早期对话用轻量模型压缩归档 | 防 Context OOM |
| Memory 分层 | 短期记忆（当前 Task）+ 长期记忆（Vector DB 用户偏好）| 按需检索加载 |

> 口诀：**本地校验省算力，报错回抛促自修正，降级兜底保可用。**

## 关联

- [[2026-08-07_rag-retrieval-drift-context-contamination]] — Hybrid Search + Rerank 的三层拦截架构
- [[2026-08-09_context-rot-mitigation]] — Reflexion Loop 与 State Mutation 的分工、上下文治理全景
- [[2026-08-05_prompt-optimization-long-context-agent]] — Summary Memory 与 Sliding Window 的实现细节
- [[2026-08-07_langchain-agent-seven-steps]] — Middleware 承接重试/摘要/权限横切逻辑

## 参考

- [GPTCache: Semantic Cache for LLM Queries](https://github.com/zilliztech/GPTCache)
- [BGE-Reranker (BAAI)](https://huggingface.co/BAAI/bge-reranker-v2-m3)

---

*Created: 2026-08-09 | Updated: `UPDATE INDEX.md`*
