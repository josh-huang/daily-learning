# Daily Learning 📋

> 不追频率，追深度。不赌自己能记住，建系统逼自己回顾。

一个面向 LLM 应用落地与后端架构的系统化学习跟踪仓库。

---

## 核心原则

- **学到了才记** — 没有每日硬性指标。碎片放 TIL，深度主题放 Papers
- **写完必须回头看** — Weekly Review 比写新笔记更重要
- **手工索引** — 每篇笔记顺手更新 `INDEX.md`，30 篇之前不自动化

---

## 目录结构

```
daily-learning/
├── til/                       # Today I Learned — 碎片知识
│   ├── ai/                    # LLM / RAG / Agent / Prompt Engineering
│   ├── python/                # Python 语法、最佳实践、标准库
│   ├── devops/                # Docker / Git / CI/CD / Linux
│   ├── sys-design/            # 系统设计 / 架构 / 分布式
│   └── template.md
│
├── papers/                    # 深度论文笔记 — 不追求一篇一天写完
│   └── template.md
│
├── weekly-review/             # 每周回顾 — 对抗遗忘曲线的唯一手段
│   └── template.md
│
├── leetcode/                  # 算法刷题
│   ├── array/                 # 数组 / 双指针 / 前缀和
│   ├── dp/                    # 动态规划
│   ├── tree/                  # 树 / 图 / DFS / BFS
│   ├── stack-queue/           # 栈 / 队列 / 单调栈
│   ├── sliding-window/        # 滑动窗口
│   ├── math/                  # 数学 / 位运算
│   └── template.md
│
├── INDEX.md                   # 全局索引 — 每篇写完顺手加一行
└── scripts/                   # 辅助脚本
```

---

## 工作流

### TIL — 一个碎片知识点

学到一个值得记录的东西 → 写一篇。没学到 → 不写。

1. 复制 `til/template.md` → 对应分类目录
2. 文件名: `YYYY-MM-DD_主题.md`
3. 写完更新 `INDEX.md`

### Papers — 一篇深度论文

核心：不要赶在一天内写完。理解比速度重要。

1. 复制 `papers/template.md` → `papers/`
2. 文件名: `YYYY-MM_短标题.md`
3. "我的思考" 部分留到第二天写也不迟

### LeetCode — 一道题

核心：不是做出来了就完了，两周后不看答案能重写才算会。

1. 复制 `leetcode/template.md` → 对应分类目录
2. 文件名: `编号-题名.md`
3. Weekly Review 时对着题目盲写检验

### Weekly Review — 每周回顾 ⭐

**这是整个系统最重要的环节。** 不写回顾 = 笔记白写。

1. 复制 `weekly-review/template.md` → `weekly-review/`
2. 文件名: `YYYY-Wxx.md`
3. 盲区自检：不看笔记，能否独立讲出核心概念？能否重写出 LeetCode？

---

## 整理流程

写完一批笔记后（比如周末），@ Claude 帮你整理：

1. 更新 `INDEX.md` 索引
2. 检查模板完整度（TL;DR / 示例 / 参考）
3. 标记与已有笔记的关联
4. **审查技术正确性**（API 路径/参数名/公式/概念定义，发现错误直接修正）
5. **适当补充**（关键 caveat、关联知识点、可运行性验证，不做无意义扩充）
6. 指出模糊或需要补笔的地方

> 你自己写内容，Claude 做 structurer + reviewer。不要反过来。


## Commit 惯例

```
til: Attention Mechanism — Q/K/V 与 Scaled Dot-Product
leetcode: LC 206 Reverse Linked List (iterative + recursive)
paper: "Training Compute-Optimal LLMs" (Chinchilla)
review: Week 33 (2026-08-04 ~ 08-10)
```
