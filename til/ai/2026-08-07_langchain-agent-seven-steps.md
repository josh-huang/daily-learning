---
date: 2026-08-07
tags: [langchain, agent, tool-use, structured-output, middleware, state-management, testing]
category: ai
---

# LangChain Agent 构建七步法：从任务边界到生产监控

## TL;DR

> LangChain Agent 构建遵循七步：**定边界 → 选模型+封 Tools → 约束行为+结构化输出 → 组装 Agent → 补状态+安全(Middleware) → 选调用方式 → 测试+Trace 监控**。核心原则：边界模糊则后续工程配置无法弥补；Tool 职责单一+Schema 清晰则模型选对概率高；Middleware 承接横切逻辑（重试/摘要/权限/审批）。

## 核心概念

- **create_agent**：LangChain 的 Agent 工厂函数，底层使用 LangGraph 在"模型判断 → 工具执行 → 结果回传"之间循环，直到模型输出最终结果。
- **Checkpointer vs Store**：Checkpointer 按 `thread_id` 保存当前线程状态（短期、续接对话），Store 管理跨线程共享信息（长期、用户偏好/事实）。
- **Middleware**：横切逻辑层，在模型调用和工具执行前后插入重试、摘要压缩、权限控制、人工审批，避免规则散落各节点。
- **response_format**：通过 Pydantic BaseModel 约束 Agent 最终输出 Schema，适用于前端渲染、工单系统、工作流等后续程序消费场景。

## 展开

### 七步全景

```
Step 1: 任务边界      → 能做什么/不能做什么/何时转人工/何谓成功
Step 2: 模型 + Tools  → Tool 拆分为职责单一、Schema 清晰的函数
Step 3: 行为约束      → system_prompt + response_format (Pydantic)
Step 4: 组装          → create_agent(model, tools, prompt, format)
Step 5: 状态 + 安全   → Checkpointer / Store / Middleware(重试/摘要/审批)
Step 6: 调用方式      → invoke | async | stream (匹配产品形态)
Step 7: 测试 + 监控   → Tool 单测 → Agent 轨迹测试 → Trace 监控
```

### Step 2: Tool 封装示例

```python
from langchain.tools import tool

@tool
def lookup_order(order_id: str) -> dict[str, str]:
    """根据订单号查询订单状态，只读，不修改订单。"""
    # 真实项目应调用经过身份校验的订单服务
    return {"order_id": order_id, "status": "已发货"}
```

Tool 设计原则：
- 名称 + docstring + 类型注解 → 模型判断能否调用的全部依据
- 职责单一：查询和退款分属两个 Tool，否则模型容易选错
- 执行端二次校验：身份 + 权限 + 幂等 + 审计

### Step 3: 结构化输出

```python
from pydantic import BaseModel, Field

class SupportReply(BaseModel):
    answer: str = Field(description="给用户的简洁答复")
    order_status: str | None = Field(default=None, description="订单状态")
    needs_human: bool = Field(description="是否需要转人工")
```

### Step 4: 组装与运行

```python
from langchain.agents import create_agent

agent = create_agent(
    model="openai:gpt-4o-mini",
    tools=[lookup_order],
    system_prompt=(
        "你是订单客服。回答订单状态前必须调用查询工具；"
        "不得猜测，无法处理时设置转人工。"
    ),
    response_format=SupportReply,
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "订单 A100 到哪了？"}]
})
reply: SupportReply = result["structured_response"]
```

### Step 5: Middleware 横切关注点

| Middleware 类型 | 作用 |
|---|---|
| 重试 | 模型/只读 Tool 临时失败时的有上限重试 |
| 摘要 | 上下文超长时，模型调用前压缩历史 |
| 权限 | 用户权限变化时动态隐藏 Tool |
| 审批 | 敏感动作执行前暂停等待人工确认 |
| 安全检查 | 模型输出后补充格式/安全校验 |

### Step 6: 调用方式选择

| 方式 | 适用场景 |
|---|---|
| `invoke` | 短任务、后台任务、等最终结果 |
| 异步调用 | 并发 I/O、异步 Web 服务 |
| `stream` | 长任务，需展示 Token/步骤/工具进度 |

> 流式输出改善的是等待体验，不会缩短工具执行时间。

### Step 7: 三层测试金字塔

```
Layer 3: E2E + Trace 监控
Layer 2: Agent 轨迹测试 (工具选择/参数/越权/结构化输出)
Layer 1: Tool 单元测试 (正常/非法/权限/超时/幂等)
```

Agent 输出具有概率性 → 不能只比较最终文本。Trace 维度：模型调用、工具参数、延迟、Token、失败率、人工转接率。

## 关联

- [[2026-08-05_prompt-optimization-long-context-agent]] — Middleware 摘要压缩与 Prefix Caching 互补
- [[2026-08-07_rag-retrieval-drift-context-contamination]] — Agent 中 RAG 检索漂移与 Middleware 权限/过滤的配合

## 参考

- [LangChain Agents Documentation](https://python.langchain.com/docs/concepts/agents/)
- [LangGraph: State Management](https://langchain-ai.github.io/langgraph/concepts/low_level/)

---

*Created: 2026-08-07 | Updated: `UPDATE INDEX.md`*
