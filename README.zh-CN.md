# Agent Web App Testing

[English](README.md) | 简体中文

**你去喝咖啡，剩下的交给测试。**

这个轻量 Playwright Python wrapper 会从发送任务一路检查到 Agent 完成，自动测试“Agent 提问—你回答—Agent 继续工作”，并默认保存最新真实 runtime checkpoint，让被 bug 中断的测试在修复后继续。它使用 smart-selector 应对动态文案，并在界面连续 15 秒无可见进度时明确报告停滞。

基于 Anthropic [`webapp-testing`](https://github.com/anthropics/skills/tree/main/skills/webapp-testing)，适用于流式对话、工具调用型 Agent 和人机协作工作流。

## 它能帮你什么

- **全过程检查**：从发送任务到最终完成，每一步都帮你确认
- **自动接住提问**：测试“Agent 提问—你回答—Agent 继续工作”是否顺畅
- **修复后继续**：从最近一个有效 runtime checkpoint 恢复

## 为什么需要它

普通 Web 测试提交操作，然后断言最终 DOM。Agent 界面有更长的故障链：

```text
submit -> running -> streaming -> waiting_user -> resumed -> completed
```

只检查最终回答，会漏掉流式输出停滞、工具执行不可见、问题弹窗失效，以及用户回答后会话没有恢复。这个模板检查各状态之间的进度。

## 检查内容

- 通过 smart-selector 适配动态模型文案
- 连续 15 秒没有可见文本或状态变化
- streaming 停滞检测，同时不限制任务总时长
- `waiting_user` 提问和同一流程恢复
- 真实 runtime checkpoint 保存与恢复
- Agent 显式错误和非空最终回答

## 安装

这是 Agent Skill，不是 Python 包。`SKILL.md` 与 `templates/` 必须保留在同一个 Skill 目录。安装 Skill 本身不需要 `pip install`。

### Codex

安装到用户级，对所有项目生效：

```bash
git clone https://github.com/liush2yuxjtu/agent-webapp-testing.git \
  "$HOME/.agents/skills/agent-webapp-testing"
```

如需仅供一个项目使用，把仓库 clone 到项目内的 `.agents/skills/agent-webapp-testing`。重启 Codex，然后输入：

```text
使用 agent-webapp-testing 测试这个 AI Agent UI。
```

详见 [Codex Skills 文档](https://developers.openai.com/codex/skills)。

### Claude Code

把整个仓库复制到当前版本支持的用户级或项目级 Agent Skills 位置，确保 `SKILL.md` 位于 Skill 根目录。重启 Claude Code，然后要求它使用 `agent-webapp-testing`。具体位置以 Anthropic 当前自定义 Skill 文档为准。

### Claude.ai

创建 `SKILL.md` 位于 ZIP 根目录的上传包：

```bash
git clone https://github.com/liush2yuxjtu/agent-webapp-testing.git
cd agent-webapp-testing
zip -r ../agent-webapp-testing.zip SKILL.md templates references
```

通过 Claude.ai 自定义 Skills 上传并启用 `agent-webapp-testing.zip`，然后要求 Claude 使用 `agent-webapp-testing`。

### 推荐配套 Skill

这个 wrapper 基于 Anthropic [`webapp-testing`](https://github.com/anthropics/skills/tree/main/skills/webapp-testing)。需要浏览器探查、截图、trace 和服务管理时，建议同时安装两者。

### 运行 Python 模板

仅运行测试模板时需要 Playwright 依赖：

```bash
python -m pip install pytest pytest-playwright
python -m playwright install chromium
pytest templates/test_agent_flow.py
```

运行前先启动目标应用，并配置正常 thread URL、runtime checkpoint API、提示词和稳定 answer ID。详见 [`references/runtime-checkpoints.md`](references/runtime-checkpoints.md)。

## UI 契约

应用需要暴露稳定属性：

- Agent 根节点：`data-agent-state`
- 输入框：`data-testid="agent-prompt"`
- 发送控件：`data-testid="agent-send"`
- 问题容器：`data-testid="agent-question"`
- 答案选项：`data-testid="agent-answer-option"`

流式回答、工具状态、问题和可见心跳应位于 Agent 根节点内。隐藏的 SSE 或 WebSocket 流量不算用户反馈。

问题和答案文案可能随提示词、语言或模型变化。测试使用语义属性，不依赖展示文本：

```python
agent = page.locator("[data-agent-state]")
question = agent.locator("[data-testid='agent-question']")
question.locator(
    "[data-testid='agent-answer-option'][data-answer-id='approve']"
).click()
```

不要用生成文案、翻译文本、CSS 展示类或 `nth(2)` 标识业务选项。完整约定见 [`references/selector-contract.md`](references/selector-contract.md)。

## Runtime Checkpoint

每条真实测试默认通过应用的真实持久化 API 保存最近一个有效 checkpoint。本地指针位于已被 Git 忽略的 `.agent/` 下，保存不透明运行状态，不录制 SSE。

测试被 bug 中断后，修复后的下一次运行先调用真实 resume API 恢复 checkpoint，并继续到 `completed`。checkpoint 缺失或被 API 明确判定为不兼容时才从头运行。恢复成功后，再执行一次完整干净重跑。

Runtime checkpoint 可能包含敏感状态，禁止提交或发布。API 适配约定见 [`references/runtime-checkpoints.md`](references/runtime-checkpoints.md)。

## 静默规则

`MAX_SILENCE = 15` 是无活动预算，不是测试总超时。每次可见状态或文本变化都会重置计时。连续 15 秒没有变化时抛出：

```text
AssertionError: No visible Agent progress for 15 seconds
```

## 仓库内容

- `SKILL.md`：面向 coding agent 的简短操作指南
- `templates/test_agent_flow.py`：真实流程、checkpoint 保存与恢复模板
- `references/selector-contract.md`：适配动态文案的 smart-selector 契约
- `references/runtime-checkpoints.md`：真实持久化与 resume API 契约

## 范围

一个指南、一个模板、两个设计参考，不造新框架。Playwright 已经做好的部分继续复用现有能力。

## License

MIT。独立社区项目，与 Anthropic 无隶属关系。
