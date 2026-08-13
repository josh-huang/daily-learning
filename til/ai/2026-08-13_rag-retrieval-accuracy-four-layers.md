---
date: 2026-08-13
tags: [rag, retrieval, query-rewriting, multi-query, hyde, chunking, hybrid-search, rrf, rerank]
category: ai
---

# RAG 检索正确率四层优化：Query → Index → Retrieval → Rerank

## TL;DR

> 提升 RAG 检索正确率按四层系统推进：**Query 层**用改写 / Multi-Query / HyDE 缩小「用户问法」与「文档写法」的鸿沟；**Index 层**用语义化 Chunk 与 Embedding 微调提升索引质量；**Retrieval 层**用 Hybrid Search + RRF 互补召回；**Rerank 层**用 Cross-Encoder 二次精排。前提是源数据质量过关——数据清洗常占一半以上工作量。

## 核心概念

- **Query Rewriting**：用 LLM 改写原始查询，使其贴近知识库文档的表述风格，缩小 query-doc 语义鸿沟。
- **Multi-Query**：让 LLM 从不同角度生成多个查询变体分别检索再合并，相当于「多角度捞取」，提升召回广度。
- **HyDE (Hypothetical Document Embeddings)**：先让 LLM 生成一份「假想答案文档」，再用它的 Embedding 去检索——把「问题→文档」变成「文档→文档」，向量空间匹配更准。
- **Chunk 策略**：按文档语义结构切分而非固定长度；工程上常用「小 Chunk 检索 + 大 Chunk（父级）喂模型」，细粒度保命中、父级保上下文完整。
- **Hybrid Search + RRF**：向量检索（语义）+ BM25（关键词精确）并行召回，用 RRF（Reciprocal Rank Fusion）做无监督排名融合。
- **Cross-Encoder Reranker**：对 Top-K 召回结果做 query-doc 逐 token 联合编码重排，相关性判断比 Bi-Encoder 精细得多。

## 展开

### 四层优化架构

```
Layer 1: Query 层 (缩小鸿沟)
├── Query Rewriting   → 贴近文档表述
├── Multi-Query       → 多角度变体分别检索再合并
└── HyDE              → 假想答案文档 Embedding 检索

Layer 2: Index 层 (索引与文档处理)
├── 语义化 Chunk      → 按结构切分，非固定长度
├── 小 Chunk 检索 / 大 Chunk 喂模型 → 命中精准 + 上下文完整
└── Embedding 微调    → 垂直领域效果明显

Layer 3: Retrieval 层 (检索策略)
├── Dense Vector      → 语义匹配
├── BM25              → 精确关键词匹配
└── RRF 融合          → 互补召回，统一排序

Layer 4: Rerank 层 (二次精排)
└── Cross-Encoder     → Top-K → 精选 Top-N，提升最终上下文质量
```

### 各层投入产出比

| 层 | 手段 | 投入产出比 | 备注 |
|----|------|-----------|------|
| Query | 改写 / Multi-Query / HyDE | 高 | 零索引改动，纯 prompt 层 |
| Index | Chunk 策略 / Embedding 微调 | 中高 | 需重建索引，微调需标注 |
| Retrieval | Hybrid + RRF | 最高 | 向量与 BM25 能力天然互补 |
| Rerank | Cross-Encoder | 高 | 每次查询额外算力，换精度 |

### 为什么 RRF 而不是加权求和

RRF 不依赖各路检索器返回的原始分数（不同检索器的分数尺度不可比），只基于排名融合：

$$\text{RRFscore}(d) = \sum_{r \in R} \frac{1}{k + r(d)}$$

其中 $r(d)$ 为文档 $d$ 在某路排名中的名次，$k$ 为平滑常数（经典取 60）。向量与 BM25 的分数不可比，直接加权无意义，RRF 规避了这个问题。

## 关联

- [[2026-08-07_rag-retrieval-drift-context-contamination]] — Hybrid Search + Rerank 的三层拦截（本篇是更系统的四层全景）
- [[2026-08-09_rag-high-concurrency-agent-fault-tolerance]] — 检索层在高并发架构中的落地

## 参考

- [HyDE: Precise Zero-Shot Dense Retrieval without Relevance Labels (arXiv:2212.10496)](https://arxiv.org/abs/2212.10496)
- [Cormack, Clarke & Buettcher (2009): Reciprocal Rank Fusion outperforms Condorcet and individual Rank Learning Methods (SIGIR '09)](https://dl.acm.org/doi/10.1145/1571941.1572114)

---

*Created: 2026-08-13 | Updated: `UPDATE INDEX.md`*
