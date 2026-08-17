---
date: 2026-08-17
tags: [tensor-parallelism, pipeline-parallelism, megatron, distributed-inference, llm-serving]
category: ai
---

# 张量并行（TP）vs 流水线并行（PP）：Megatron-LM MLP 切分与通信

## TL;DR

> TP 把**单个算子/层内的权重矩阵**切到多卡（Layer 内切分，走 NVLink 高带宽），PP 把**不同 Layer** 切到不同设备（跨 Layer 切分，走跨节点）。Megatron-LM 的 MLP 用「列并行 GEMM → GeLU（卡内局部算）→ 行并行 GEMM」把激活函数卡在中间，整个 MLP 块仅需 **1 次 All-Reduce**，最小化通信。

## 核心概念

- **张量并行（TP）**：将单层内的权重矩阵（如 GEMM）切分到多 GPU 并行计算，属 Layer 内部切分，适合节点内高带宽互联（NVLink）。
- **流水线并行（PP）**：将模型不同 Layer（如 1–16 层在 GPU0，17–32 层在 GPU1）切分到不同设备，属跨 Layer 切分，适合跨节点通信。
- **列并行 / 行并行 GEMM**：Megatron-LM MLP 的两段切分方式，把 GeLU 夹在中间做卡内局部计算，从而只需一次 All-Reduce。

## 展开

### TP vs PP 一句话区分

| 维度 | TP | PP |
|------|----|----|
| 切分粒度 | 层内（单算子的权重矩阵） | 跨层（不同 Layer） |
| 通信位置 | 每层计算中的 All-Reduce | 层间边界的前向/反向传递 |
| 适合互联 | 节点内 NVLink（高带宽） | 跨节点 |
| 典型问题 | 通信频繁、对带宽敏感 | Pipeline Bubble（设备空等） |

### Megatron-LM 的 MLP 层 TP 切分

设 MLP 权重 $W_1 \in \mathbb{R}^{h \times 4h}$（上投影）、$W_2 \in \mathbb{R}^{4h \times h}$（下投影）：

1. **列并行 GEMM**：$W_1$ 按列切为 $[W_{1,1}, W_{1,2}]$，输入 $X$ 广播到两卡，分别算 $Y_1 = \text{GeLU}(X W_{1,1})$、$Y_2 = \text{GeLU}(X W_{1,2})$。**此阶段卡间零通信**。
2. **行并行 GEMM**：$W_2$ 按行切为 $\begin{bmatrix} W_{2,1} \\ W_{2,2} \end{bmatrix}$，每卡算局部乘积 $Z_1 = Y_1 W_{2,1}$、$Z_2 = Y_2 W_{2,2}$。
3. **All-Reduce 求和**：$Z = Z_1 + Z_2$，仅在 MLP 输出端做一次 All-Reduce。

**精髓**：列切分与行切分串联，把非线性激活 GeLU 放在卡内局部计算，整个 MLP 块只触发 1 次 All-Reduce，极大降低通信瓶颈。

## 关联

- [[2026-08-17_mla-multi-head-latent-attention]] — 两者同属大模型推理/训练的显存与算力优化，一个在 Attention 层做低秩压缩，一个在 MLP 层做张量切分
- [[2026-08-05_flashattention-io-aware-exact-attention]] — FlashAttention 优化单卡 Attention 的 I/O，TP/PP 优化多卡的通信与切分，正交但可叠加

## 参考

- [Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM](https://arxiv.org/abs/2104.04473)

---

*Created: 2026-08-17 | Updated: `UPDATE INDEX.md`*
