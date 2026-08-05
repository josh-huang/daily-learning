# Daily Learning 📋

> 日拱一卒，功不唐捐。

每天记录学习内容并 Push 到 GitHub，用输出倒逼输入。

---

## 目录结构

```
daily-learning/
├── til/                       # Today I Learned — 每日学习笔记
│   ├── ai/                    # LLM / RAG / Agent / Prompt Engineering
│   ├── python/                # Python 语法、最佳实践、标准库
│   ├── devops/                # Docker / Git / CI/CD / Linux
│   ├── sys-design/            # 系统设计 / 架构 / 分布式
│   └── template.md            # TIL 模版（复制此文件开始新笔记）
│
├── leetcode/                  # 算法刷题
│   ├── array/                 # 数组 / 双指针 / 前缀和
│   ├── dp/                    # 动态规划
│   ├── tree/                  # 树 / 图 / DFS / BFS
│   ├── stack-queue/           # 栈 / 队列 / 单调栈
│   ├── sliding-window/        # 滑动窗口
│   ├── math/                  # 数学 / 位运算
│   └── template.md            # 题解模版
│
└── scripts/                   # 辅助脚本（统计、生成目录等）
```

---

## 使用方式

### TIL — 写一篇学习笔记

1. 复制 `til/template.md` 到对应分类目录
2. 按模版填写内容
3. 文件名格式: `YYYY-MM-DD_主题.md`，如 `2026-08-05_attention-mechanism.md`

### LeetCode — 刷一道题

1. 复制 `leetcode/template.md` 到对应分类目录
2. 按模版填写题解
3. 文件名格式: `编号-题名.md`，如 `1-Two-Sum.md`

---

## 每日流程

```bash
# 1. 写笔记 / 刷题
# 2. 提交
git add .
git commit -m "til: 2026-08-05 - Attention Mechanism & LC 206"
git push
# 3. GitHub Activity 点亮 🟩
```
