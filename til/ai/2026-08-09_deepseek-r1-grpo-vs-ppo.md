---
date: 2026-08-09
tags: [reinforcement-learning, grpo, ppo, deepseek, rlhf, alignment, cot, reasoning]
category: ai
---

# DeepSeek-R1 / GRPO：分组相对策略优化的核心原理

## TL;DR

> GRPO (Group Relative Policy Optimization) 摆脱了 PPO 对 Critic Model 的依赖：对同一 prompt 采样一组回答 $G$ 个，Reward Model 打分后组内归一化（减均值除以标准差）得到相对优势 $A_i$。核心收益：**显存减少 30%-50%**（无需 Critic）、消除 Critic 训练不稳定性、天然适合 CoT 推理链的自我探索。

## 核心概念

- **GRPO (Group Relative Policy Optimization)**：DeepSeek-R1 采用的 RL 对齐算法，通过组内相对比较替代 PPO 的绝对价值估计。
- **组内归一化 (Group Normalization)**：对 $G$ 个采样回答的奖励值做 $A_i = \frac{R_i - \text{mean}(R)}{\text{std}(R)}$，用组内相对排名替代 Critic 模型的绝对价值估计。
- **Critic-Free**：PPO 需要训练一个与 Actor 等参数量的 Critic（Value Model），GRPO 直接省掉。

## 展开

### 数学原理

对每个输入 Prompt $q$，Actor 模型并行采样 $G$ 个回答 $\{o_1, o_2, \dots, o_G\}$：

1. Reward Model 对 $G$ 个回答分别打分 → $\{R_1, R_2, \dots, R_G\}$
2. 组内归一化计算相对优势：

$$A_i = \frac{R_i - \text{mean}(R)}{\text{std}(R)}$$

3. 用 $A_i$ 替代 PPO 中的 Advantage，直接做 Policy Gradient 更新。

### GRPO vs PPO 对比

| 维度 | PPO | GRPO |
|------|-----|------|
| Critic Model | 需要（与 Actor 等参数量的 Value Network） | **不需要** |
| 显存开销 | Actor + Critic + Optimizer States | **Actor only** |
| 训练稳定性 | Critic 拟合不准 → Value Loss 震荡 | 组内归一化，无 Critic 不稳定问题 |
| 推理链探索 | 单样本 → 绝对奖励 | **组内对比 → 激发 CoT 自我探索** |
| 显存节省 | — | **约 30% - 50%** |

### 为什么 GRPO 适合 Reasoning / Code / Math

组内采样对比机制天然鼓励模型探索多样化的推理路径：
- 同一道数学题采样 4 条推理链 → 正确的获得正优势，错误的获得负优势
- 模型学会**自我辨别**哪些推理步骤更可能导向正确答案
- 不需要人工标注每一步的正确性 → 仅需最终结果的 Reward Signal

### PPO 中 Critic 的问题

PPO 的 Advantage 计算依赖 $A = R - V(s)$，$V(s)$ 由 Critic 估计：
- Critic 低估 → Advantage 偏高 → 策略更新过激 → 训练崩溃
- Critic 高估 → Advantage 偏低 → 策略更新不足 → 收敛缓慢
- GRPO 通过组内相对比较绕过了整个 Value Estimation 问题

## 关联

- 后续可深入：GRPO 与 DPO/ORPO 等 Offline RL 方法的对比、Reward Model 设计（Rule-based vs Model-based）
- [[2026-08-05_flashattention-io-aware-exact-attention]] — 训练显存优化的另一维度（Attention 计算）

## 参考

- [DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning](https://arxiv.org/abs/2501.12948)
- [DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models](https://arxiv.org/abs/2402.03300)

---

*Created: 2026-08-09 | Updated: `UPDATE INDEX.md`*
