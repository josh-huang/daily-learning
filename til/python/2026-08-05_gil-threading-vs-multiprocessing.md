---
date: 2026-08-05
tags: [gil, threading, multiprocessing, concurrency, cpython]
category: python
---

# Python GIL 与并发模型：Threading vs Multiprocessing

## TL;DR

> GIL 是 CPython 的全局解释器锁，导致多线程无法真正并行执行 CPU 密集型任务。I/O 密集型用 `threading`，CPU 密集型用 `multiprocessing`。Python 3.13 通过 PEP 703 正在移除 GIL。

## 核心概念

- **GIL (Global Interpreter Lock)**：CPython 中的互斥锁，保证任一时刻只有一个 OS 线程执行 Python 字节码
- **Reference Counting**：引入 GIL 的根源 — CPython 用引用计数管理内存，无锁保护下多线程并发修改 `ob_refcnt` 会导致竞态条件，引发内存泄漏或悬空指针
- **PEP 703 (Python 3.13 自由线程)**：通过 Biased Reference Counting、Mimalloc 分配器、Per-object Locks 逐步移除 GIL，实现真正的硬件级多核并行

## 深入

### I/O 密集型 vs CPU 密集型

| | I/O 密集型 | CPU 密集型 |
|---|---|---|
| 典型场景 | 网络请求、文件读写、爬虫 | 科学计算、数据处理、图像处理 |
| GIL 影响 | 小 — I/O 等待时主动释放 GIL | 大 — 线程频繁争抢 GIL，性能反低于单线程 |
| 推荐方案 | `threading` / `ThreadPoolExecutor` | `multiprocessing` / `ProcessPoolExecutor` |

### Threading vs Multiprocessing

| 维度 | threading | multiprocessing |
|---|---|---|
| 绕过 GIL | ❌ 否 | ✅ 是（独立解释器 + 独立 GIL） |
| 内存开销 | 小（共享内存空间） | 大（每进程独立内存 + 载入解释器） |
| 通信方式 | 简单（共享变量 + Lock） | 繁琐（Queue / Pipe / Manager IPC） |
| 启动速度 | 极快 | 较慢（进程创建 + 序列化开销） |

### 代码示例

**I/O 密集型 — 多线程**

```python
import threading
import time

def download_file(file_id):
    thread_name = threading.current_thread().name
    print(f"[{thread_name}] 开始下载文件 {file_id}...")
    time.sleep(2)  # 模拟 I/O 阻塞
    print(f"[{thread_name}] 文件 {file_id} 下载完成！")

if __name__ == "__main__":
    start_time = time.time()
    threads = []

    for i in range(1, 4):
        t = threading.Thread(target=download_file, args=(i,), name=f"Thread-{i}")
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print(f"\n总耗时: {time.time() - start_time:.2f} 秒")
    # 约 2 秒 — 3 个线程并发等待 I/O
```

**ThreadPoolExecutor — 推荐方式**

```python
from concurrent.futures import ThreadPoolExecutor
import time

def fetch_url(url):
    time.sleep(2)
    return f"Data from {url}"

urls = ["https://example.com/a", "https://example.com/b", "https://example.com/c"]

if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(fetch_url, urls))
    print(results)
```

**CPU 密集型 — 多进程**

```python
from concurrent.futures import ProcessPoolExecutor

def calc_square(n):
    return sum(i * i for i in range(n))

numbers = [20_000_000, 20_000_000, 20_000_000]

if __name__ == "__main__":
    # 仅需将 ThreadPoolExecutor 替换为 ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(calc_square, numbers))
    print(results)
```

## 关联

- 后续可深入：`asyncio` 协程模型 vs 线程模型的对比（事件循环、上下文切换开销）

## 参考

- [PEP 703 – Making the Global Interpreter Lock Optional](https://peps.python.org/pep-0703/)
- [Python 3.13 What's New – Free-threaded CPython](https://docs.python.org/3.13/whatsnew/3.13.html#free-threaded-cpython)

---

*Created: 2026-08-05 | Updated: `UPDATE INDEX.md`*
