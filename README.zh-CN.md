# Agent Web App Testing

[English](README.md) | 简体中文

面向 AI Agent Web 应用的 Playwright Python 测试：覆盖流式输出、可见进度、人机协作提问、暂停与恢复。

Agent 界面常在提交请求与最终回答之间失效：长时间静默、流式输出停滞、提问框不可操作，或用户回答后会话没有恢复。这个轻量 wrapper 在 Anthropic [`webapp-testing`](https://github.com/anthropics/skills/tree/main/skills/webapp-testing) 基础上补充这些检查。

适用于 ChatGPT 类界面、工具调用型 Agent，以及等待用户输入后继续执行的工作流。

## 检查内容

- 每 15 秒至少出现一次可见文本或状态变化
- `running -> streaming -> waiting_user -> running -> completed`
- Agent 提问暂停后，可在同一流程中恢复
- 问题与答案文案变化不会破坏 selector
- 最终回答不能为空

15 秒限制的是静默时间，不是任务总时长。任务执行五分钟也可以通过，只要用户持续看到进度；连续静默 15 秒则失败。

## 文件

- `SKILL.md`：简短操作指南
- `templates/test_agent_flow.py`：带详细注释的可运行模板

## UI 契约

应用需要暴露稳定 selector：

- Agent 根节点：`data-agent-state`
- 输入框：`data-testid="agent-prompt"`
- 发送控件：`data-testid="agent-send"`
- 问题容器：`data-testid="agent-question"`
- 答案选项：`data-testid="agent-answer-option"`

流式回答、工具状态、问题和可见心跳应位于 Agent 根节点内。隐藏的 SSE 或 WebSocket 流量不算用户可见进度。

问题文案可以动态变化。模板通过语义属性选择答案控件，不依赖展示文本。需要选择特定业务答案时，增加 `data-answer-id`。

## 使用

将 `SKILL.md` 和 `templates/` 复制到技能目录。修改 `templates/test_agent_flow.py` 中的目标 URL、提示词和 selector，然后在现有 Playwright Python 环境中运行：

```bash
pytest templates/test_agent_flow.py
```

模板使用 Playwright 的 `page` fixture。浏览器初始化、trace、截图和普通断言继续由 `webapp-testing` 或现有测试框架负责。

## License

MIT。独立社区项目，与 Anthropic 无隶属关系。
