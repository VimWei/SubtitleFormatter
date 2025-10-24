## SubtitleFormatter 脚本编排机制规划

### 背景与目标
- 现状：`text cleaning`、`sentence splitting`、`filler handling`、`line breaking` 是若干独立脚本，但以固定顺序串联，靠开关控制是否执行。
- 问题：灵活性不足（顺序不可调）、脚本耦合（输入输出不统一）、扩展难（新增脚本需要嵌入固定流程）。
- 目标：
  - 通过“编排器”实现脚本的自由组合：开/关、重排顺序、条件执行、并行或顺序执行。
  - 以“统一中间表示”（UIR）解耦脚本输入/输出，使脚本可独立演进且可复用。
  - 通过配置文件（TOML/YAML）声明式定义 pipeline；运行期由编排器解析与执行。

### 设计原则
- 独立性：每个脚本只依赖 UIR，不依赖其他具体脚本的内部结构。
- 可组合性：脚本声明其输入/输出能力，编排器做兼容性与依赖检查。
- 可观测性：统一日志、事件与度量，便于调试与回溯。
- 可测试性：脚本可单测（基于示例 UIR），pipeline 可集成测。
- 可演进性：版本化脚本与 UIR，支持向后兼容与迁移器（migrator）。

### 核心概念与统一中间表示（UIR）
建议采用结构化 UIR，覆盖文本与时间轴：
```json
{
  "version": "1.0",
  "media": { "type": "text", "language": "en" },
  "segments": [
    {
      "id": "seg-0001",
      "start": 0.00,              // 可选：纯文本时可为 null
      "end": 3.20,                // 可选
      "text": "Hello world!",
      "tokens": ["Hello", "world", "!"],
      "attributes": {             // 任意键值：清理标记、语言、置信度等
        "cleaned": true,
        "split_level": "sentence"
      },
      "flags": {                  // 布尔型状态集合
        "is_filler": false,
        "needs_review": false
      }
    }
  ],
  "metadata": {                   // 全局信息，如来源文件、脚本历史
    "source": "Bee hunting.txt",
    "history": [
      {"script": "text_cleaning", "version": "1.2.0", "ts": "2025-10-15T10:00:00Z"}
    ]
  },
  "errors": []                     // 非致命错误收集
}
```
要点：
- `segments[]` 作为核心承载；脚本应尽量保持段的稳定性（id 不随意重建）。
- 允许可选时间轴字段，兼容仅文本或含时间戳的场景。
- `attributes`/`flags` 提供扩展空间，避免频繁修改 UIR 模式。
- `metadata.history` 记录处理轨迹，便于审计与回溯。

### 脚本接口规范（Script Contract）
每个脚本暴露一致的协议（以 Python 为例）：
```python
class Script:
    name: str = "text_cleaning"
    version: str = "1.2.0"

    # 声明能力，用于编排器做静态检查
    requires: dict = {
        "segments": {"text": "required"},
        "time": "optional"  # 可选：需要时间轴能力
    }
    provides: dict = {
        "segments": {"text": "cleaned"},
        "attributes": ["cleaned", "normalized"]
    }

    def process(self, uir: dict, context: dict) -> dict:
        """纯函数式处理：输入 UIR，输出 UIR（浅拷贝+差异写入）。
        - 不做 I/O（除非通过 context.services 注入的受控 I/O）。
        - 不修改入参对象，就地修改需先拷贝。
        - 失败时抛出受控异常或在 uir.errors 记录并按策略返回。"""
        ...
```
- 纯函数倾向：降低副作用，提升可测试性与并行性。
- `requires/provides`：用于编排时的连线与兼容性检查。
- `context` 提供受控资源：
  - `logger`、`config.step`（当前步骤配置）、`services`（缓存、持久化、模型等）。

### 编排器设计
- 执行模型
  - 默认顺序执行（兼容现状）；支持基于依赖的 DAG 执行与并行。
  - 节点并行需声明无冲突（如作用于不同字段或可并发读写）。
- 配置驱动
  - 以 TOML/YAML 定义 pipeline，运行时解析为节点与边。
  - 支持开关、重排、条件执行（when）、分支（branch）、循环（map over files）。
- 兼容性与依赖检查
  - 执行前根据 `requires/provides` 做静态检查；必要时提示插入“迁移器”脚本（schema 升/降级）。
- 缓存与幂等
  - 基于输入 UIR 的内容哈希+脚本版本进行节点级缓存；
  - 要求脚本在相同输入与配置下幂等，保证可重复性。
- 错误处理策略
  - `fail-fast`：节点失败即终止；
  - `best-effort`：记录错误跳过节点继续；
  - 支持节点级重试与回退（rollback hook 可选）。
- 可观测性
  - 统一日志格式；步骤耗时、段变更统计；
  - 生成处理谱系（lineage）与最终报告。

### 配置示例（TOML）
```toml
[pipeline]
name = "default"
mode = "sequential"                 # sequential | parallel | dag
error_strategy = "fail-fast"        # fail-fast | best-effort

[[steps]]
name = "text_cleaning"
script = "text_cleaning"
enabled = true
[steps.config]
normalize_quotes = true
trim_whitespaces = "aggressive"

[[steps]]
name = "sentence_splitting"
script = "sentence_splitting"
enabled = true
[steps.config]
model = "en_core_web_md"
retain_abbrev = true

[[steps]]
name = "filler_handling"
script = "filler_handling"
enabled = false
[steps.config]
strategy = "remove"                 # remove | tag | collapse

[[steps]]
name = "line_breaking"
script = "line_breaking"
enabled = true
[steps.config]
max_chars = 42
balance = "words"
```

### 兼容旧流程的迁移策略
- 初始阶段：按当前固定顺序作为默认 pipeline，开关映射为 `enabled` 字段。
- 渐进：逐步将现有处理函数改造为遵循脚本接口的“独立脚本”。
- 保底：提供“旧流程适配器”节点，将旧入口包装成单节点，保证功能不中断。

### 开发与测试建议
- 脚本级单测：针对 UIR 样例做输入输出断言；覆盖边界与空输入。
- 管道级集测：以典型文本用例覆盖不同开关组合与顺序变更。
- 回归基线：保存关键输入的“黄金输出”，做差异比对（允许受控字段差异）。

### 实施路线图（建议）
1) 奠定基础（1-2 周）
- 定义并冻结 UIR v1（最小可用字段）；
- 产出脚本基类与上下文注入机制；
- 实现顺序编排器与 TOML 解析；

2) 迁移现有四脚本（1-2 周）
- 将 `text_cleaning` / `sentence_splitting` / `filler_handling` / `line_breaking` 改造成独立脚本；
- 引入节点级缓存与日志；

3) 增强能力（2-4 周）
- 增加 DAG/并行执行；
- 加入兼容性检查、错误策略、处理谱系报告；

4) 集成与可视化（可选，持续）
- CLI：`subtitleformatter pipeline run -c config.toml`；
- GUI：可视化 pipeline 编排（拖拽排序、启停、参数编辑）。

### 风险与权衡
- UIR 设计过度会增加脚本改造成本：从 v1 起步，按需演进。
- 并行带来的竞态与可重复性：保持纯函数式与明确字段写入约束。
- 缓存一致性：哈希需覆盖脚本版本与配置，必要时提供 cache busting。

### 待确认问题清单
- UIR v1 的最小字段集合与命名是否符合现数据流？
- 是否需要强制时间轴字段为可选或分 profile（text-only / timed）？
- 现有四脚本在 `requires/provides` 上的初版声明？
- 并行是否为近期刚需，还是先落地顺序编排？
- GUI 的编排编辑是否放在第二阶段？

---

本文为讨论草案，欢迎补充与质疑。确认后可据此展开实施。
