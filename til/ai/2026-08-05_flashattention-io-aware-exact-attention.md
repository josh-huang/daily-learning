---
date: 2026-08-05
tags: [attention, transformer, flashattention, complexity, memory-optimization, gpu]
category: ai
---

# Transformer Attention 复杂度与 FlashAttention 原理

## TL;DR

> Standard Attention: 时间 $O(N^2 \cdot d)$，空间 $O(N^2)$（瓶颈在 $N \times N$ Attention Matrix）。FlashAttention 通过 Tiling（SRAM 分块计算）+ Online Softmax（在线规约）+ Recomputation（反向传播重算），将空间降至 $O(N)$，同时利用 SRAM 高带宽加速。

## 核心概念

- **HBM vs SRAM**：GPU 显存分两层 — HBM (High Bandwidth Memory) 大但慢（~1.5TB/s），SRAM (on-chip Shared Memory) 小但快（~19TB/s）。Standard Attention 反复在 HBM 和 SRAM 之间搬运 $N \times N$ 矩阵，I/O 是瓶颈。
- **Tiling**：把 $Q, K, V$ 切成小块加载到 SRAM 内部完成 softmax 计算，中间结果不写回 HBM。
- **Online Softmax**：分块 softmax 的数学技巧 — 用 `m(x)`（运行最大值）和 `l(x)`（运行归一化因子）实现分块无损合并。
- **Recomputation**：前向传播时不保存 $N \times N$ Attention Matrix，反向传播时在 SRAM 中重新算一遍。用计算换显存。

## 深入

### Standard Attention 复杂度推导

给定 $Q, K, V \in \mathbb{R}^{N \times d}$：

$$
S = QK^T \quad \text{— } N \times N \text{ 矩阵，计算量 } O(N^2 \cdot d)
$$

$$
P = \text{softmax}(S) \quad \text{— } N \times N \text{ 矩阵，存储量 } O(N^2)
$$

$$
O = PV \quad \text{— } N \times d \text{，计算量 } O(N^2 \cdot d)
$$

**总时间**: $O(N^2 \cdot d)$，**总空间**: $O(N^2)$（$S$ 和 $P$ 各需存储 $N^2$ 以用于反向传播求梯度）

当 $N=8192$（8K context）：Attention Matrix = $8192^2 \times 2$ bytes (fp16) ≈ 128MB。当 $N=128K$：≈ 32GB — 单张 H100 80GB 也吃不住。

### FlashAttention 三步优化

```
┌──────────────────────────────────────┐
│                 HBM                  │  Q, K, V, Output
│  ┌──────────────────────────────┐    │
│  │           SRAM               │    │
│  │  Q_block → local S → O_block │    │  Tiling: 不写 N×N 回 HBM
│  │  m(x), l(x) ← online update  │    │  Online Softmax: 分块合并
│  └──────────────────────────────┘    │
│  反向传播: recompute in SRAM         │  Recomputation: 不存 Attention Matrix
└──────────────────────────────────────┘
```

| 优化 | 解决什么问题 | 效果 |
|------|-------------|------|
| Tiling | HBM ↔ SRAM 的 $O(N^2)$ 数据搬运 | I/O 变为 $O(N^2 \cdot d^2 / M)$（$M$=SRAM 大小） |
| Online Softmax | 分块后各块的 softmax 分母不同，无法直接拼接 | 数学等价，分块无损合并 |
| Recomputation | 反向传播需要 $S$ 和 $P$ 求梯度 | 空间 $O(N^2) \to O(N)$，前向稍快（不写大矩阵） |

### 一句话为什么是 IO-Aware

Standard Attention 的瓶颈不是计算 $O(N^2 \cdot d)$，而是**往 HBM 读写 $N \times N$ 矩阵的 I/O**。FlashAttention 在 SRAM 里算完，只把最终结果 `O` 和 `l(x)` 写回 HBM — 省了 $N \times N$ 的读写。

## 面试要点

> **Q**: FlashAttention 空间复杂度是多少？
> **A**: $O(N)$。它不存储 $N \times N$ 的 Attention Matrix，反向传播时在 SRAM 里重新计算（Recomputation），用计算换显存。
>
> **Q**: Online Softmax 解决什么问题？
> **A**: 分块 softmax 时各块的归一化因子不同（每块的 max 不一样），直接拼接会错误。Online Softmax 用额外的两个标量 `m` 和 `l` 动态更新，保证数学等价且可分块。

## 关联

- FlashAttention-2: 减少了非矩阵乘法的 FLOP，对 H100 专门优化了 work partitioning
- FlashAttention-3: 利用 Hopper 架构的 TMA (Tensor Memory Accelerator) 做异步数据搬运

## 参考

- [FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness (Dao et al., 2022)](https://arxiv.org/abs/2205.14135)
- [FlashAttention-2: Faster Attention with Better Parallelism and Work Partitioning](https://arxiv.org/abs/2307.08691)
- [ELI5: FlashAttention (Github 图解)](https://github.com/tspeterkim/flash-attention-minimal)

---

*Created: 2026-08-05 | Updated: `UPDATE INDEX.md`*
