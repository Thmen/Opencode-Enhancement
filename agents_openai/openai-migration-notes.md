# OpenAI 迁移说明

本文档说明当前 `agents_openai/` 目录的实现范围、与原始 `agents/` 的关系，以及 OpenAI 版本示例的运行与测试方式。

## 迁移目标

- 保留原始 `agents/` 中基于 Anthropic SDK 的教学实现，继续作为对照基线。
- 在 `agents_openai/` 中，用 OpenAI Python SDK 的 `Responses API` 重写同一套教学脚本。
- 将 OpenAI 侧的响应解析、工具回传和工具循环抽成共享适配层。
- 用 `tests/agents_openai/` 验证适配层与代表性工作流，减少迁移后行为漂移。

## 当前实现范围

- `agents_openai/` 已覆盖 `s01` 到 `s12`，以及整合版 `s_full`。
- `s_full` 是 `s01` 到 `s11` 的参考整合实现。
- `s12` 聚焦“任务板 + git worktree 隔离”，作为单独教学主题保留，没有并入 `s_full`。
- `tests/agents_openai/` 已覆盖共享适配层、各 session 的代表性行为，以及全部模块的导入 smoke test。

## 目录说明

- `agents/`
  - 原始 Anthropic 版本，作为教学基线保留。
- `agents_openai/_openai_responses.py`
  - 加载 `.env`。
  - 创建 OpenAI client，并读取 `MODEL_ID`。
  - 将教学脚本里的 `input_schema` 转成 OpenAI strict function tool schema。
  - 提取 `function_call`、封装 `function_call_output`、提取最终文本。
  - 提供 `request_once()`、`execute_function_calls()`、`run_tool_loop()` 等共享循环能力。
- `agents_openai/__init__.py`
  - 对共享适配层中的核心辅助函数做统一导出。
- `agents_openai/s01_agent_loop.py`
  - 最小可运行版本，只保留 `bash` 工具和基础 agent loop。
- `agents_openai/s02_tool_use.py`
  - 在基础 loop 上加入 `read_file`、`write_file`、`edit_file` 等工具分发。
- `agents_openai/s03_todo_write.py`
  - 引入 `TodoManager` 和 `todo` 工具，并在长任务中注入 reminder。
- `agents_openai/s04_subagent.py`
  - 通过 `task` 工具启动“新上下文”的子代理。
- `agents_openai/s05_skill_loading.py`
  - 从 `skills/**/SKILL.md` 按需加载技能正文，而不是把全部说明塞进 system prompt。
- `agents_openai/s06_context_compact.py`
  - 提供 micro compact、自动压缩和手动 `compact` 三层上下文压缩机制。
- `agents_openai/s07_task_system.py`
  - 用 `.tasks/` 中的 JSON 文件持久化任务及依赖关系。
- `agents_openai/s08_background_tasks.py`
  - 用后台线程执行长任务，并在下次 LLM 调用前回灌通知。
- `agents_openai/s09_agent_teams.py`
  - 用 `.team/` 和 inbox JSONL 文件构建持久化 teammate 协作模型。
- `agents_openai/s10_team_protocols.py`
  - 在团队模型上增加 shutdown 和 plan approval 两种 request/response 协议。
- `agents_openai/s11_autonomous_agents.py`
  - 让 teammate 在 idle 阶段自动轮询 `.tasks/`、自动 claim 任务并恢复工作。
- `agents_openai/s12_worktree_task_isolation.py`
  - 检测 git repo 根目录，把任务板与 `.worktrees/` 索引、事件日志和 git worktree 生命周期关联起来。
- `agents_openai/s_full.py`
  - 组合 Todo、Skills、Subagent、Compact、Background、Tasks、Teams 等机制的参考实现。
- `tests/agents_openai/`
  - 使用 fake client / fake bus / fake background manager 验证适配层和 session 行为，不依赖真实网络调用。

## 核心 API 差异

Anthropic 版本主要调用：

```python
client.messages.create(...)
```

OpenAI 版本统一迁移到：

```python
client.responses.create(...)
```

迁移时重点处理了以下差异：

- 工具定义
  - 教学脚本仍然用 `input_schema` 描述工具。
  - OpenAI 侧会在 `convert_tool_to_openai()` 中转换成 strict function tool schema。
  - 可选字段会被规范成可空类型，并统一补进 `required`，同时设置 `additionalProperties=False`。
- 工具调用解析
  - Anthropic 常从 `response.content` 中读取 `tool_use`。
  - OpenAI 版本从 `response.output` 中扫描 `type == "function_call"` 的项。
- 工具结果回传
  - Anthropic 常回传 `tool_result`。
  - OpenAI 版本统一回传 `{"type": "function_call_output", "call_id": ..., "output": ...}`。
- 响应内容追加
  - OpenAI 版本会先把 `response.output` 中的原始 output item 追加回输入列表，再追加工具执行结果，保证多轮调用上下文完整。
- 文本提取
  - OpenAI 版本优先读取 `response.output_text`。
  - 若为空，则回退到 `response.output` 中 `message.content[].text` 的拼接结果。
- 工具循环抽象
  - 基础脚本多通过 `run_tool_loop()` 完成多轮工具执行。
  - 需要自定义行为的脚本则在本地循环里调用 `request_once()` 和 `execute_function_calls()`。
  - 默认启用 `parallel_tool_calls=True`，因此多工具同轮调用也能被统一处理。

## 共享适配层说明

当前 OpenAI 版本的共享层主要只有两部分：

- `agents_openai/_openai_responses.py`
  - 处理 OpenAI `Responses API` 的输入输出适配。
- `agents_openai/__init__.py`
  - 对共享辅助函数进行重导出。

## 运行方式

项目使用 `uv` 管理环境。首次拉取后建议先同步依赖：

```bash
uv sync
```

共享适配层会自动执行 `load_dotenv(override=True)`，运行脚本前通常需要准备以下环境变量：

- `MODEL_ID`
- `OPENAI_API_KEY`

如需接入兼容网关，也可额外设置：

- `OPENAI_BASE_URL`

常见运行示例：

```bash
uv run agents_openai/s01_agent_loop.py
```

```bash
uv run agents_openai/s12_worktree_task_isolation.py
```

```bash
uv run agents_openai/s_full.py
```

## 运行时状态目录

以下目录会在真实运行某些 session 时被创建或更新：

- `.tasks/`
  - `s07`、`s11`、`s12`、`s_full` 会用它保存任务状态。
- `.team/`
  - `s09`、`s10`、`s11`、`s_full` 会用它保存 teammate 配置和 inbox。
- `.transcripts/`
  - `s06`、`s_full` 会在上下文压缩时写入对话快照。
- `.worktrees/`
  - `s12` 会在这里维护 `index.json` 和 `events.jsonl`，并创建实际的 git worktree 目录。

这些目录属于运行时状态，不代表源码结构被额外修改。

## 测试覆盖概览

`tests/agents_openai/` 目前主要覆盖以下内容：

- `test_openai_responses.py`
  - 校验 strict schema 归一化、`output_text` 回退解析、多工具同轮调用、`function_call_output` 追加顺序，以及 `max_turns` 限制。
- `test_s01_agent_loop.py`
  - 校验最小 loop 能正确追加 `function_call` 和 `function_call_output`。
- `test_s02_tool_use.py`
  - 校验文件工具的写入行为和最终结果返回。
- `test_s03_todo_write.py`
  - 校验长任务过程中 reminder 注入逻辑。
- `test_s04_subagent.py`
  - 校验子代理摘要返回以及父代理对 `task` 工具的代理行为。
- `test_s05_skill_loading.py`
  - 校验技能正文能通过工具结果回传到对话历史。
- `test_s06_context_compact.py`
  - 校验旧工具输出压缩、自动压缩和手动 compact 流程。
- `test_s07_task_system.py`
  - 校验任务创建、状态更新与磁盘持久化。
- `test_s08_background_tasks.py`
  - 校验后台通知在 LLM 调用前被注入历史消息。
- `test_s09_agent_teams.py`
  - 校验 lead inbox 消息会先写入对话，再继续执行。
- `test_s10_team_protocols.py`
  - 校验 shutdown request 跟踪和 plan review 回传。
- `test_s11_autonomous_agents.py`
  - 校验未认领任务扫描与 claim 后状态更新。
- `test_s12_worktree_task_isolation.py`
  - 校验 worktree 创建、移除、任务绑定解除和事件日志一致性。
- `test_s_full.py`
  - 校验整合版 agent 会在回答前同时注入后台结果与团队 inbox 消息。
- `test_smoke_imports.py`
  - 校验全部 OpenAI 模块在设置 `MODEL_ID` 后都可正常导入。

这些测试绝大多数使用 fake 对象完成，不会发起真实 OpenAI 请求，也通常不要求提供真实 `OPENAI_API_KEY`。

需要区分两件事：

- 这些测试文件主要采用 `unittest` 风格编写，例如 `unittest.TestCase`、`setUp()` 和 `self.assertEqual()`。
- 项目在 `pyproject.toml` 中已经配置了 `pytest` 作为更方便的统一运行入口，而且 `pytest` 可以直接发现并执行这些 `unittest` 风格用例。

## 测试用例执行

在仓库根目录下，日常执行建议优先使用 `pytest`。

运行全部 OpenAI 迁移测试：

```bash
uv run pytest -q # 精简输出
uv run pytest tests/agents_openai -v
```

只运行共享适配层测试：

```bash
uv run pytest tests/agents_openai/test_openai_responses.py -v
```

只运行 smoke import 测试：

```bash
uv run pytest tests/agents_openai/test_smoke_imports.py -v
```

只运行 worktree 隔离相关测试：

```bash
uv run pytest tests/agents_openai/test_s12_worktree_task_isolation.py -v
```

只运行整合版 agent 测试：

```bash
uv run pytest tests/agents_openai/test_s_full.py -v
```

可选的静态编译检查：

```bash
uv run -m compileall agents_openai tests/agents_openai
```

如需使用标准库自带方式，下面的 `unittest discover` 也同样可用：

```bash
uv run -m unittest discover -s tests/agents_openai -p "test_*.py" -v
```

## 当前状态

- 原始 `agents/` 目录未被替换，仍可作为 Anthropic 版参考。
- `agents_openai/` 已经完成 `s01` 到 `s12` 的迁移，并包含 `s_full` 参考实现。
- 共享层已稳定到 `_openai_responses.py`。
- 测试当前以“共享适配层 + 代表性行为 + 轻量集成”为主，而不是调用真实模型做端到端验证。

## 已知说明

- `s09` 到 `s12` 以及 `s_full` 都包含线程、文件系统或运行时状态目录，因此测试以行为验证和 fake 组件替身为主。
- `s12` 的真实运行会使用 `.worktrees/`、`.tasks/` 和 git worktree，这是设计的一部分。
- `s_full` 目前整合到 `s11` 的能力边界；若需要任务感知的 worktree 隔离，应使用 `s12`。
