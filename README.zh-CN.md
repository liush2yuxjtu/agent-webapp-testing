# Agent Web App Testing

[English](README.md) | 简体中文

**不怕动态文案，让每一次无声卡死都变成明确失败。**

Agent 可能不报错、不结束，也不再产生输出。这个轻量 Playwright Python wrapper 在界面连续 15 秒无可见进度时抓住它，同时避免使用模型生成文案作为 selector。

基于 Anthropic [`webapp-testing`](https://github.com/anthropics/skills/tree/main/skills/webapp-testing)，适用于流式对话、工具调用型 Agent 和人机协作工作流。

## 为什么需要它

普通 Web 测试提交操作，然后断言最终 DOM。Agent 界面有更长的故障链：

```text
submit -> running -> streaming -> waiting_user -> resumed -> completed
```

只检查最终回答，会漏掉流式输出停滞、工具执行不可见、问题弹窗失效，以及用户回答后会话没有恢复。这个模板检查各状态之间的进度。

## 检查内容

- 通过稳定语义 selector 适配动态模型文案
- 连续 15 秒没有可见文本或状态变化
- streaming 停滞检测，同时不限制任务总时长
- `waiting_user` 提问和同一流程恢复
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
zip -r ../agent-webapp-testing.zip SKILL.md templates
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

运行前先启动目标应用，并修改 `templates/test_agent_flow.py` 中的 URL、提示词和稳定 selector。

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
question = page.locator("[data-testid='agent-question']")
question.locator("[data-testid='agent-answer-option']").first.click()
```

需要选择特定业务答案时，增加 `data-answer-id`。

## 静默规则

`MAX_SILENCE = 15` 是无活动预算，不是测试总超时。每次可见状态或文本变化都会重置计时。连续 15 秒没有变化时抛出：

```text
AssertionError: No visible Agent progress for 15 seconds
```

## 仓库内容

- `SKILL.md`：面向 coding agent 的简短操作指南
- `templates/test_agent_flow.py`：代码简单、注释详细的测试模板

## 范围

一个指南、一个模板、不造新框架。Playwright 已经做好的部分继续复用现有能力。

## License

MIT。独立社区项目，与 Anthropic 无隶属关系。
