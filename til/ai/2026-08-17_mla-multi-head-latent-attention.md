---
date: 2026-08-17
tags: [mla, deepseek, kv-cache, attention, low-rank, llm-inference]
category: ai
---

# MLA（Multi-Head Latent Attention）：低秩联合压缩的 KV Cache

## TL;DR

> MLA 把历史 token 的 Key/Value **联合低秩压缩**到一个潜向量 $\mathbf{c}_t^{KV} \in \mathbb{R}^{d_c}$（$d_c \ll H \cdot d_h$），再把 RoPE 位置信息解耦成极小的专属向量 $\mathbf{k}_t^R$ 单独缓存。推理时只缓存这两个小向量，上投影矩阵 $W^{UK}, W^{UV}$ 被吸收进 Query 矩阵，显存不存完整 KV。相比 MHA，KV Cache 显存降低 **93.3%**（比 GQA 更极限），同时保留 Full Attention 容量。

## 核心概念

- **低秩联合压缩（Low-Rank Joint Compression）**：Key 和 Value 不再分别独立缓存，而是联合投影到低维潜空间 $\mathbf{c}_t^{KV}$，推理时再通过上投影矩阵恢复多头 K/V。
- **解耦 RoPE**：RoPE 对相对位置敏感、无法直接乘进低秩压缩矩阵，MLA 将位置信息解耦为极小的专属向量 $\mathbf{k}_t^R$ 单独缓存。
- **矩阵吸收（Matrix Absorption）**：把潜变量恢复到多头 K/V 的上投影矩阵 $W^{UK}, W^{UV}$ 提前吸收进 Query 与投影矩阵（如 $Q W^{UK}$），避免推理时显式解压完整 KV 张量。

## 展开

### 传统 MHA/GQA 的痛点

长上下文推理时 KV Cache 显存随上下文长度**线性增长**，成为制约并发与最大 Context 的硬伤。MHA 每 token 缓存 $2D$ 个元素（$H$ 个头各存 K、V），GQA/MQA 靠共享 KV 头降低头数，但仍线性增长。

### MLA 的压缩流程

1. **下投影（压缩）**：$\mathbf{c}_t^{KV} = X W^{DKV}$，$W^{DKV} \in \mathbb{R}^{D \times d_c}$，$d_c$ 通常取 $D/4 \sim D/8$。
2. **上投影（恢复）**：需要时 $\mathbf{K}^C = \mathbf{c}_t^{KV} W^{UK}$、$\mathbf{V}^C = \mathbf{c}_t^{KV} W^{UV}$，但通过矩阵吸收在推理时不显式解压。
3. **缓存内容**：仅 $\mathbf{c}_t^{KV}$（潜变量）+ $\mathbf{k}_t^R$（位置向量）。

### 显存收益

| 方案 | 每 token KV Cache |
|------|------------------|
| MHA | $2D$ |
| MQA | $2d_h$（$1/H$） |
| GQA | $2G d_h$（$G/H$） |
| **MLA** | $d_c$（+ 极小的 $\mathbf{k}_t^R$） |

DeepSeek-V2 报告：相比 DeepSeek 67B（dense-MHA 基线），KV Cache 降低 **93.3%**，最大生成吞吐提升 **5.76×**，训练成本节省 **42.5%**。代价是额外的下/上投影矩阵乘法，在长上下文（100k+）等**内存带宽受限**场景收益最大。

## 关联

- [[2026-08-09_deepseek-r1-grpo-vs-ppo]] — MLA 是 DeepSeek-V2 的架构创新，GRPO 是 DeepSeek-R1 的对齐算法，同属 DeepSeek 技术栈
- [[2026-08-07_rope-rotary-position-embedding]] — MLA 的"解耦 RoPE"正是 RoPE 无法进低秩压缩的直接后果，需配合理解
- [[2026-08-17_tensor-pipeline-parallelism]] — 同属大模型推理的显存/算力优化，正交维度

## 参考

- [DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model](https://arxiv.org/abs/2405.04434)

---

*Created: 2026-08-17 | Updated: `UPDATE INDEX.md`*
