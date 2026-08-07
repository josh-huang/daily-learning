---
date: 2026-08-07
tags: [llm, attention, position-encoding, rope, llama, long-context, interview]
category: ai
---

# RoPE (旋转位置编码)：数学原理与对比分析

## TL;DR

> RoPE 通过旋转矩阵将位置信息注入 Q/K 向量：高维拆分 $d/2$ 个二维子空间独立旋转，内积 $\mathbf{q}^T \mathbf{k}$ 仅取决于相对位置差 $(m-n)$，数值随距离自然衰减。相比绝对 PE：具备相对位置感知能力；相比相对 PE Bias 矩阵：无额外参数量，利于长上下文外推（YaRN / Dynamic NTK）。

## 核心概念

- **RoPE (Rotary Position Embedding)**：LLaMA 架构采用的位置编码方式，无显式可学习参数，通过复数旋转实现位置编码的注入。
- **旋转矩阵 $\mathbf{R}_{\Theta, m}$**：角度为 $m\theta$ 的 2D 旋转矩阵，$m$ 为 token 位置，$\theta_i = 10000^{-2i/d}$ 为频率。
- **相对位置不变性**：$(\mathbf{R}_m \mathbf{q})^T (\mathbf{R}_n \mathbf{k}) = \mathbf{q}^T \mathbf{R}_{n-m} \mathbf{k}$，点积仅依赖相对距离 $n-m$。
- **长上下文外推**：通过调整旋转频率（YaRN、Dynamic NTK）可将预训练的短上下文窗口扩展至更长。

## 展开

### 数学原理

将 Query/Key 的二维子向量 $\mathbf{x} = [x_1, x_2]^T$ 视为复平面上的点，通过旋转矩阵 $\mathbf{R}_{\Theta, m}$ 注入位置 $m$：

$$\mathbf{R}_{\Theta, m} = \begin{pmatrix} \cos m\theta & -\sin m\theta \\ \sin m\theta & \cos m\theta \end{pmatrix}$$

高维向量（维度 $d$）拆分为 $d/2$ 个相互正交的二维子空间，各自按不同频率 $\theta_i$ 旋转：

$$\text{RoPE}(\mathbf{x}, m) = \begin{pmatrix} \mathbf{R}_{\Theta_1, m} \mathbf{x}^{(1)} \\ \mathbf{R}_{\Theta_2, m} \mathbf{x}^{(2)} \\ \vdots \\ \mathbf{R}_{\Theta_{d/2}, m} \mathbf{x}^{(d/2)} \end{pmatrix}$$

### 内积衰减特性

关键性质：旋转后的 Q、K 点积仅依赖相对位置：

$$(\mathbf{R}_m \mathbf{q})^\top (\mathbf{R}_n \mathbf{k}) = \mathbf{q}^\top \mathbf{R}_m^\top \mathbf{R}_n \mathbf{k} = \mathbf{q}^\top \mathbf{R}_{n-m} \mathbf{k}$$

两个 token 距离越远，旋转角度差越大 → 内积自然衰减 → **天然具备远程衰减先验**。

### 三种位置编码对比

| | Absolute PE | Relative PE (Bias) | RoPE |
|---|---|---|---|
| 相对位置感知 | ❌ 无 | ✅ 显式 | ✅ 隐式 |
| 可学习参数 | 有 (Learned) / 无 (Sinusoidal) | 有 | **无** |
| 长上下文外推 | 差 | 一般 | **好** (配合 NTK/YaRN) |
| 计算开销 | 低 | 中（额外 Bias 矩阵） | 低 |
| 代表架构 | GPT-2/3 (Learned) | T5 | **LLaMA / Qwen / ChatGLM** |

### 长上下文外推方案

- **YaRN**：对高频子空间做线性插值，低频保持原样
- **Dynamic NTK**：根据实际输入长度动态缩放 $\theta$ 的 base frequency
- 优势：无需重新训练，仅修改推理时的旋转频率

## 关联

- [[2026-08-05_flashattention-io-aware-exact-attention]] — FlashAttention 优化 Attention 计算，RoPE 优化位置表示
- [[2026-08-07_rag-retrieval-drift-context-contamination]] — 同日记的 RAG 笔记

## 参考

- [RoPE 原论文: RoFormer (Su et al., 2021)](https://arxiv.org/abs/2104.09864)
- [Llama 2: Open Foundation and Fine-Tuned Chat Models](https://arxiv.org/abs/2307.09288)

---

*Created: 2026-08-07 | Updated: `UPDATE INDEX.md`*
