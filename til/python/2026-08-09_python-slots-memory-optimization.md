---
date: 2026-08-09
tags: [python, memory-optimization, slots, cpython, dict, performance]
category: python
---

# Python `__slots__` 内存优化：从 `__dict__` 到固定指针数组

## TL;DR

> 标准 Python 实例用 `__dict__`（哈希表）存属性 → 空间利用率仅 ~60%，每个属性额外扛 PyObject 头开销。定义 `__slots__` 后，CPython 禁用 `__dict__`，属性存储退化为固定偏移量的指针数组 → **内存下降 60%-80%，属性访问省去哈希查找直接通过偏移量寻址**。

## 核心概念

- **`__dict__` (默认)**：每个实例维护一个动态字典存储属性。哈希表为降低冲突预留空槽，空间利用率低，且每个键值对都有 PyObject 头部开销。
- **`__slots__`**：类级别声明的属性白名单。CPython 据此为实例分配固定长度的指针数组，每个属性通过 descriptor 按固定偏移量直接读写。
- **内存布局变化**：`__dict__` 是哈希表（指针+桶） → `__slots__` 是紧凑数组（仅指针），无哈希表元数据、无空槽浪费。

## 展开

### 底层原理

```python
# 默认：每个实例都有 __dict__
class RegularUser:
    def __init__(self, name, email, age):
        self.name = name
        self.email = email
        self.age = age

# __slots__: 属性存储在固定偏移量数组
class SlottedUser:
    __slots__ = ('name', 'email', 'age')

    def __init__(self, name, email, age):
        self.name = name
        self.email = email
        self.age = age
```

CPython 层面：
- `RegularUser` 实例 → `ob_dict` 指针 → 堆上的哈希表 → 每个属性是一个 `PyDictEntry`
- `SlottedUser` 实例 → 对象尾部直接嵌入指针数组 → `descr->d_member_offset` 直接寻址

### 收益量化

| 维度 | `__dict__` (默认) | `__slots__` |
|------|------------------|-------------|
| 每实例内存 | ~152 bytes (含 dict 元数据) | ~56 bytes (仅指针数组) |
| 属性访问 | 哈希查找 O(1) + 碰撞处理 | 直接偏移量寻址 O(1) |
| `__dict__` | ✅ 可用 | ❌ 禁用 |
| `__weakref__` | ✅ 可用 | ❌ 默认禁用（需显式加入 `__slots__`） |
| 动态添加属性 | ✅ 可 | ❌ 不可 |
| 继承 | 子类自动有 `__dict__` | 子类需显式声明（否则退化为 dict） |

### 实际内存测量

```python
import sys

class Regular:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class Slotted:
    __slots__ = ('x', 'y', 'z')
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

r = Regular(1, 2, 3)
s = Slotted(1, 2, 3)

print(sys.getsizeof(r))  # 典型输出: 56 (仅对象头，不含 __dict__)
print(sys.getsizeof(r.__dict__))  # 典型输出: ~168 (哈希表本身)
# 实际总开销: 56 + 168 = ~224 bytes

print(sys.getsizeof(s))  # 典型输出: ~72 bytes (对象头 + 3 个指针)
```

> 注意：`sys.getsizeof` 只返回对象本身的大小，不递归计算引用对象。`Regular.__dict__` 是独立分配的堆对象，需单独测量。

### 使用场景与限制

**值得用：**
- 大量小对象（ORM 模型、配置对象、数据类、消息体）
- 属性集合固定且预先可知
- 内存敏感场景（缓存层、游戏实体、科学计算中间结果）

**不该用：**
- 需要动态添加属性的场景
- 多重继承复杂的类层级
- 需要使用 `__weakref__` 但忘了加入 slots

### 继承陷阱

```python
class Base:
    __slots__ = ('x',)

class Derived(Base):
    __slots__ = ('y',)  # ✅ 正确：子类也声明 __slots__

class BadDerived(Base):
    pass  # ❌ 子类没声明 → 自动获得 __dict__，slots 优化白费
```

## 关联

- [[2026-08-05_python-gil-threading-vs-multiprocessing]] — 同属 Python 性能优化的底层机制
- 后续可深入：`dataclasses(slots=True)` (Python 3.10+)、`__slots__` 与 `@property` 的交互

## 参考

- [Python `__slots__` 官方文档](https://docs.python.org/3/reference/datamodel.html#slots)
- [CPython 源码: `PyMemberDef` 与 descriptor 偏移量机制](https://github.com/python/cpython/blob/main/Objects/descrobject.c)

---

*Created: 2026-08-09 | Updated: `UPDATE INDEX.md`*
