# CowAgent codebase guide and learning roadmap

This guide describes the repository as it exists in this checkout. It is for a developer who wants to understand, debug, or safely extend CowAgent rather than merely run it.

## 1. What this project is

CowAgent is a Python-based, multi-channel AI-agent runtime. A message from a web UI or an IM channel is normalized into a common context, routed to an Agent, sent to an LLM, and—when the LLM asks—executed through tools. The resulting answer and progress events are returned through the originating channel.

It also provides:

- configurable LLM providers and modality providers (chat, vision, image, ASR/TTS);
- a per-agent workspace with prompt files, memory, knowledge, skills, runs, and scheduler state;
- browser, shell, filesystem, web, MCP, scheduler, memory, delegation, and sub-agent tools;
- a traditional plugin system for channel/message hooks;
- a web console and an optional Electron + React desktop application.

The primary backend language is Python. The desktop client is TypeScript/React/Electron. It is an extensible application, not a small library: use its factories and initialization paths instead of instantiating model/channel classes ad hoc.

## 2. Mental model: one request end to end

```text
User / Web / IM platform
        |
        v
channel/<provider>  ->  Channel.build_reply_content()
        |                         |
        |                         v
        |                    Bridge.fetch_agent_reply()
        |                         |
        v                         v
normalized Context          AgentBridge + AgentInitializer
                                      |
                                      v
                         Agent(session, workspace, prompt,
                               tools, memory, skills, model adapter)
                                      |
                                      v
                         AgentStreamExecutor loop
                          |                    |
                 LLM request/stream      validate + run tool calls
                          |                    |
                          +------ repeat until final answer / limit -----+
                                      |
                                      v
                         events, Reply, persistence
                                      |
                                      v
                         originating channel / web SSE / UI
```

The important separation is:

| Layer | Responsibility | Main locations |
| --- | --- | --- |
| Process/bootstrap | Load settings and start channel threads | `app.py`, `config.py` |
| Channels | Receive/provider-specific send and message conversion | `channel/` |
| Bridge | Compatibility layer between legacy chat and Agent modes | `bridge/` |
| Agent runtime | Session lifecycle, prompt, model loop, streams, cancellation | `agent/` |
| Models | Provider-specific LLM and image/session adapters | `models/` |
| Capabilities | Tools, MCP clients, skills, plugins, voice, translation | `agent/tools/`, `plugins/`, `voice/`, `translate/` |
| Persistence | Workspace files, SQLite-backed memory/session/run state | `agent/memory/`, `agent/workspace/`, `common/state_dir.py` |
| User interfaces | Browser API/UI and desktop shell | `channel/web/`, `desktop/` |

## 3. Startup and configuration

### Startup path

Read these in order:

1. `app.py:run()` is the backend entry point. It loads configuration, determines which channels to start, synchronizes built-in skills, warms optional services, and starts every channel in its own daemon thread.
2. `app.py:ChannelManager` owns channel instances and their start/stop/restart lifecycle. It supports both legacy single channels and explicit multi-instance channel records.
3. `channel/channel_factory.py:create_channel()` converts a channel type such as `web`, `telegram`, or `feishu` into the correct class.
4. `channel/channel.py:Channel` is the common base class. Its `build_reply_content()` chooses Agent mode (`Bridge.fetch_agent_reply`) or the legacy direct-chat path (`Bridge.fetch_reply_content`).

`run.sh`, `scripts/run.ps1`, Docker files, and `cli/commands/process.py` are operational wrappers; they are useful after understanding `app.py`, but they are not the application core.

### Configuration

- `config-template.json` is the best short list of user-facing settings.
- `config.py` loads, merges, validates, masks, and exposes settings through `conf()`.
- The default runtime workspace is configured by `agent_workspace` (typically `~/cow`), not by this repository directory.
- Keep credentials out of source control. Provider keys can be held in configuration and are migrated into workspace environment state by `AgentInitializer`.

Key controls for execution are `agent`, `model`, `agent_max_steps`, `agent_max_context_tokens`, `agent_permission_mode`, `subagent`, and `mcp_tool_retrieval_enabled`.

## 4. The agent runtime—the most important area

### Building an Agent

`bridge/agent_bridge.py:AgentBridge` is the backend façade used by channels. On a request it resolves the target agent/session and calls the initializer.

`bridge/agent_initializer.py:AgentInitializer.initialize_agent()` assembles a runnable Agent:

1. Resolves the `AgentProfile` from `agent/registry.py` and chooses its workspace.
2. Ensures the workspace prompt files and directories exist through `agent/prompt/workspace.py`.
3. Creates memory services and memory tools.
4. Loads built-in and configured/MCP tools with `agent/tools/tool_manager.py`.
5. Creates a skill manager and prompt builder.
6. Selects model settings and builds an `Agent` with session-scoped runtime information.

`AgentLLMModel` in `bridge/agent_bridge.py` is the adapter that lets the modern Agent runtime use the project's provider bots. Its model precedence is: session override → per-agent profile override → global configuration; a configured fallback model can take over for the remainder of a failed run.

### Prompt construction

`agent/protocol/agent.py:Agent.get_full_system_prompt()` rebuilds the prompt each turn. This is deliberate: edits to workspace files, skills, current tools, permission mode, and runtime information can take effect without restarting.

`agent/prompt/builder.py` turns those inputs into the final system prompt. Important sources include workspace persona/rule files, tool schemas, available skills, memory/knowledge instructions, project workspace details, team information, and time/runtime data.

### The model/tool loop

`agent/protocol/agent_stream.py:AgentStreamExecutor` contains the core agent loop. It streams model output, processes tool calls, applies constraints, emits lifecycle events, appends tool results, retries appropriate failures, compacts history when needed, and ends with a final response or step/cancellation limit.

`agent/chat/service.py:ChatService` is the session-facing orchestration layer. It owns the conversation run, persistence, streaming chunks for the web UI, cancellation/steering registration, and conversion of executor events into UI-friendly events such as `tool_start`, `tool_calls`, `subagent_step`, and `artifact`.

When debugging a request, follow this chain first:

```text
specific channel's handle_text / API handler
  -> Channel.build_reply_content
  -> Bridge.fetch_agent_reply
  -> AgentBridge.agent_reply
  -> ChatService.run
  -> AgentStreamExecutor
  -> model adapter and/or BaseTool.run
```

## 5. Extension points

### Add a model provider

1. Implement a provider bot/session under `models/<provider>/` using the patterns in `models/openai/` or another close provider.
2. Add the provider route to `models/bot_factory.py`.
3. Ensure bridge model inference recognizes it, or configure a `bot_type` explicitly. The relevant logic is in `bridge/bridge.py` and `AgentLLMModel`.
4. Add settings, documentation, and tests for normal chat, streaming, tool calling, and error behavior.

For an OpenAI-compatible endpoint, start with `models/openai_compatible_bot.py` and the dynamic compatibility support in `bridge/agent_bridge.py` instead of duplicating a provider implementation.

### Add a tool

1. Add a package below `agent/tools/<tool_name>/` and implement a `BaseTool` subclass.
2. Export it from `agent/tools/__init__.py`; `ToolManager` discovers exported classes and configures their availability.
3. Make the tool's input schema, permission requirements, path containment, output limits, and error messages explicit.
4. If it operates on a project directory, make it respect the Agent’s effective working directory.
5. Add focused tests under `tests/test_<tool_name>.py`.

Do not bypass permission checks or filesystem/URL safety helpers. Existing tools demonstrate the patterns in `agent/permission/`, `agent/tools/utils/`, and the file/shell tool packages.

### Add a channel

1. Implement a `Channel`/`ChatChannel` subclass in `channel/<provider>/`.
2. Normalize inbound platform data into `Context` and use the common reply path.
3. Implement provider-specific `send()` and lifecycle `startup()`/`stop()` behavior.
4. Register the type in `channel/channel_factory.py`; support `apply_instance()`/`stamp_instance_context()` if it can run more than once.
5. Add the channel’s documentation and tests.

### Add a skill versus a plugin

Use a **skill** for a reusable agent-facing workflow described by `SKILL.md`; loader/formatting code is in `agent/skills/`, and installed/builtin assets live in `skills/` and the user workspace. Use a **plugin** for Python event hooks and command/message interception; plugin discovery and lifecycle are in `plugins/plugin_manager.py`.

MCP is a third choice: configure an external tool server rather than writing an in-process integration. The MCP registry/client code is under `agent/tools/mcp/`.

## 6. Stateful data and isolation

`common/state_dir.py` is the map for runtime state. Read it before changing a path or adding persistence. It distinguishes shared instance assets (for example skills, knowledge, MCP settings, and credentials) from agent- and user-scoped assets such as memory, output, task runs, and scheduler data.

`agent/registry.py` defines agent profiles. Multiple agents must not share a workspace. Sessions can have model, project-directory, and permission-mode preferences. `agent/workspace/` provides safe workspace editing and project storage services.

Memory code is in `agent/memory/`: the manager coordinates storage, retrieval, summarization, embeddings, chunking, and vector backends. Knowledge curation is in `agent/knowledge/`. Treat both as user data: changes require migration, privacy, and recovery thinking—not just a new field.

## 7. Web and desktop UI

`channel/web/web_channel.py` runs the browser-facing backend and APIs; static browser console assets are beside it. This is the best place to trace an HTTP or SSE issue.

`desktop/` is a separate desktop shell:

- `desktop/src/main/` is Electron process code; `python-manager.ts` starts the Python backend.
- `desktop/src/renderer/src/` is the Vite/React user interface.
- `api/client.ts` is the frontend HTTP boundary.
- `pages/`, `components/`, and `store/` organize UI flows and state.

The desktop app communicates with the backend over HTTP and SSE; it does not duplicate agent logic in TypeScript.

## 8. Testing and safe changes

Tests are pytest-style files in `tests/`. Their names describe behavior well: for example, `test_agent_routing.py`, `test_agent_stream_content_blocks.py`, `test_tool_path_and_eval.py`, `test_workspace_edit.py`, and `test_security_ssrf_*`.

Suggested commands after dependencies are installed:

```powershell
pytest -q
pytest -q tests/test_agent_routing.py
pytest -q tests/test_<area>.py
```

For desktop changes, work within `desktop/` and use `npm run dev` or the relevant build/test script from `desktop/package.json`.

Before changing a cross-cutting feature, answer these questions:

1. Is this data global, agent-scoped, user-scoped, session-scoped, or channel-instance-scoped?
2. Does the tool/model/channel need streaming, cancellation, and event propagation?
3. Is it available in every permission mode? What is the least privilege it needs?
4. What happens with malformed input, provider failures, restarts, and concurrent sessions?
5. Which focused existing test is closest, and which regression test proves the new behavior?

## 9. A practical 10-session roadmap

Each session is roughly 60–90 minutes. Do them in order; the goal is a working mental model, not memorizing every provider.

| Session | Read / trace | Hands-on result |
| --- | --- | --- |
| 1. Orientation | This guide, `README.md`, `config-template.json`, `docs/intro/architecture.mdx` | Identify the configured channel, model, workspace, and agent limits. |
| 2. Boot | `app.py`, then `channel/channel_factory.py` | Draw which channels start and where each has a thread. |
| 3. Message boundary | `channel/channel.py`, one channel implementation (start with `channel/web/`) | Trace one text message to `build_reply_content()` and back. |
| 4. Bridge and provider | `bridge/bridge.py`, `bridge/agent_bridge.py`, `models/bot_factory.py`, one configured provider | Explain why this model/provider is selected and how a fallback occurs. |
| 5. Agent assembly | `bridge/agent_initializer.py`, `agent/registry.py`, `agent/protocol/agent.py` | List the objects created for a new session and their scopes. |
| 6. Agent execution | `agent/chat/service.py`, `agent/protocol/agent_stream.py`, `bridge/agent_event_handler.py` | Follow a tool call from streamed model data to a UI event. |
| 7. Tools and safety | `agent/tools/__init__.py`, `tool_manager.py`, `base_tool.py`, read/edit/bash implementations | Add no code yet; write down validation and permission checks a new tool needs. |
| 8. Workspace, memory, skills | `common/state_dir.py`, `agent/prompt/`, `agent/memory/`, `agent/skills/` | Locate actual workspace files and explain which ones change the next prompt. |
| 9. Interfaces and extensions | `plugins/`, `agent/tools/mcp/`, `desktop/README.md` | Choose skill, plugin, MCP, tool, channel, or model for one imagined feature—and justify it. |
| 10. Tests and first change | Closest tests in `tests/` plus a small isolated bug/feature | Make a minimal change, add a regression test, run it, and inspect the diff. |

## 10. Recommended first modifications

Start with one of these low-risk changes:

- Improve a tool’s validation/error message and add a focused test.
- Add a setting display or help text that does not alter runtime behavior.
- Add a small workspace skill and verify that it appears in the constructed prompt.
- Add a provider/model catalog entry only after tracing the existing provider routing.

Avoid starting with a new channel, a memory schema change, or an executor-loop rewrite. Those touch concurrency, persistence, provider behavior, and security at the same time.

## 11. Fast reference

| If you need to… | Start here |
| --- | --- |
| Start or stop the app | `app.py`, `cli/commands/process.py`, `run.sh`, `scripts/run.ps1` |
| Change configuration loading | `config.py` |
| Diagnose model selection | `bridge/bridge.py`, `bridge/agent_bridge.py`, `models/bot_factory.py` |
| Diagnose an agent response | `bridge/agent_bridge.py`, `agent/chat/service.py`, `agent/protocol/agent_stream.py` |
| Change system prompt contents | `agent/prompt/builder.py`, `agent/prompt/workspace.py` |
| Add/change a tool | `agent/tools/`, `agent/tools/tool_manager.py` |
| Change permissions | `agent/permission/policy.py` |
| Add memory/knowledge behavior | `agent/memory/`, `agent/knowledge/`, `common/state_dir.py` |
| Add an IM integration | `channel/`, `channel/channel_factory.py` |
| Change the browser console | `channel/web/` |
| Change the desktop app | `desktop/src/main/`, `desktop/src/renderer/src/` |
| Add legacy event hooks | `plugins/plugin_manager.py`, `plugins/event.py` |

## 12. Glossary

- **Channel**: transport integration that receives/sends platform messages.
- **Bridge**: compatibility façade that connects channels to provider bots or Agent mode.
- **Agent**: a configured LLM, prompt, tools, memory, skills, and per-session message history.
- **Tool**: an executable, schema-defined capability exposed to the model.
- **Skill**: an instruction/workflow bundle that helps the Agent use tools consistently.
- **Plugin**: Python extension registered for application events or commands.
- **MCP**: an external Model Context Protocol tool server integrated at runtime.
- **Workspace**: persistent working/state directory belonging to an agent, rather than this source checkout.
- **Context**: normalized metadata accompanying a message (channel, sender, session, attachments, callbacks, routing data).

