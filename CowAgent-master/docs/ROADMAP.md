# CowAgent Technical & Product Roadmap

This roadmap defines the strategic direction, architectural evolution, and engineering priorities for CowAgent. It outlines near-term enhancements, mid-term system expansions, and long-term research horizons.

---

## 🧭 Strategic Vision

CowAgent is evolving from an autonomous agent harness into an **enterprise-grade, multi-agent operating system** that seamlessly bridges human communication channels, local compute environments, and distributed AI capabilities.

```
       ┌─────────────────────────────────────────────────────────────┐
       │                   CowAgent Vision Pillars                   │
       └─────────────────────────────────────────────────────────────┘
          │                           │                           │
          ▼                           ▼                           ▼
  [Rock-Solid Reliability]     [Safe Autonomy]        [Ubiquitous Presence]
  - Deterministic execution    - Sandboxed tools       - Any channel (IM/Web/Desk)
  - Resilient context compactor- Least-privilege RBAC  - Multi-agent collaboration
  - Self-healing retries       - Audit-logged evolution- Local-first & cloud hybrid
```

---

## 🗓️ Release Horizon & Milestones

```mermaid
gantt
    title CowAgent Strategic Roadmap
    dateFormat  YYYY-Q
    axisFormat  %Y Q%q

    section Milestone 1: Security & Sandboxing
    Containerized Bash / Browser Tool Isolation :m1_1, 2026-Q3, 2026-Q4
    Fine-Grained RBAC & Tool Policy Engine      :m1_2, 2026-Q3, 2026-Q4
    Automated Secret & Credential Vault         :m1_3, 2026-Q4, 2027-Q1

    section Milestone 2: Swarm & Multi-Agent
    Bidirectional Agent Inter-Comm Bus          :m2_1, 2026-Q4, 2027-Q1
    Dynamic Sub-Agent DAG & Delegation Engine   :m2_2, 2026-Q4, 2027-Q2
    Distributed Shared Agent Memory             :m2_3, 2027-Q1, 2027-Q2

    section Milestone 3: Memory & Knowledge 2.0
    External Vector DB Adapters (Qdrant/Milvus) :m3_1, 2026-Q4, 2027-Q1
    GraphRAG Knowledge Engine & Semantic Linking:m3_2, 2027-Q1, 2027-Q2
    Continuous Streaming Memory Consolidation   :m3_3, 2027-Q1, 2027-Q2

    section Milestone 4: Omnichannel & Multimodal
    Real-Time Duplex Voice Streaming (WebRTC)   :m4_1, 2027-Q1, 2027-Q3
    Live Canvas & Interactive Artifacts UI      :m4_2, 2027-Q2, 2027-Q3
    Video Stream Understanding & OCR Tooling    :m4_3, 2027-Q2, 2027-Q4

    section Milestone 5: Local Edge & Enterprise
    Native Local Model Mesh (Ollama/vLLM/llama) :m5_1, 2027-Q2, 2027-Q4
    Enterprise Multi-Tenant Cloud Architecture  :m5_2, 2027-Q3, 2027-Q4
```

---

## 🎯 Milestone 1: Security, Sandboxing & Tool Safety (Near-Term)

### Objectives
Provide ironclad isolation for code execution, filesystem operations, and external network interactions.

### Key Deliverables
1. **Containerized Tool Sandboxing (`agent/tools/bash`, `agent/tools/browser`)**
   - Provide pluggable container execution backends: Local Docker, Podman, and lightweight microVM/Wasm runtimes.
   - Ensure file writes, bash commands, and browser automation can run completely isolated from the host OS.
   - Ephemeral container recycling per session or per turn with configurable CPU/memory quotas.

2. **Fine-Grained Access Control & RBAC Policy Engine (`agent/permission/`)**
   - Expand beyond the current three tiers (`read-only`, `workspace-write`, `full-access`) to path-level and domain-level whitelisting.
   - Interactive user-approval gates (human-in-the-loop prompts) for destructive operations (`rm -rf`, outbound HTTP POST to untrusted origins, process terminations).
   - Comprehensive audit logging of all tool invocations, inputs, hashes, and exit codes.

3. **Secure Vault for Secrets & Tool Configurations (`~/.cow/`)**
   - System keyring / encrypted keystore integration (libsecret, macOS Keychain, Windows Credential Manager).
   - Automated secret masking across all streaming tokens and persistent message logs.

---

## 🤖 Milestone 2: Swarm Coordination & Multi-Agent Teams (Mid-Term)

### Objectives
Evolve the existing subagent delegation and team roster into a true distributed multi-agent swarm capable of executing parallel, interdependent task graphs.

### Key Deliverables
1. **Bidirectional Agent Communication Bus (`agent/team.py`, `agent/subagent/`)**
   - Enable subagents to query peer agents or request clarification from the parent agent mid-task rather than only returning a final conclusion.
   - Introduce an event-driven pub/sub message bus allowing specialized agents (e.g., Planner, Researcher, Coder, Reviewer) to collaborate in shared sessions.

2. **Hierarchical Task DAG Engine**
   - Graph-based task planner that breaks complex user requests into directed acyclic graphs (DAGs).
   - Parallel task execution with checkpointing and state resumption upon failure or rate-limiting.
   - Dynamic budget allocation: distribute step counts and token limits adaptively across subagent branches.

3. **Multi-Instance IM Gateway Routing**
   - Expand channel multi-instance support from Feishu to all supported channels (Telegram, Slack, Discord, WeChat Work, DingTalk).
   - Dynamic agent-to-channel bindings managed live from the Web Console and Desktop UI without service restarts.

---

## 🧠 Milestone 3: Advanced Memory & GraphRAG Knowledge Base (Mid-Term)

### Objectives
Scale personal and organizational memory retrieval to hundreds of thousands of documents with sub-second hybrid retrieval and deep semantic reasoning.

### Key Deliverables
1. **Pluggable Vector Database Connectors (`agent/memory/vector_backend.py`)**
   - Extend beyond the local SQLite / `sqlite-vec` engine to support enterprise vector databases: **Qdrant**, **Milvus**, **Chroma**, and **pgvector**.
   - Cloud-native and distributed embedding index syncing across multiple CowAgent instances.

2. **GraphRAG Semantic Knowledge Engine (`agent/knowledge/`)**
   - Transform the Markdown wiki into an automated entity-relationship graph.
   - Community detection and multi-hop entity reasoning (e.g., linking people, projects, concepts, and temporal events).
   - Interactive 3D knowledge graph exploration in Web Console and Desktop client with direct note-editing capabilities.

3. **Continuous Streaming Memory Distillation (`agent/memory/summarizer.py`, `agent/evolution/`)**
   - Augment the nightly "Deep Dream" batch pass with lightweight, continuous background reflection.
   - Real-time fact extraction and contradiction detection: automatically detect when user preferences or project details change and update core memory accordingly.

---

## ⚡ Milestone 4: Omnichannel & Multimodal Real-Time Interaction (Long-Term)

### Objectives
Turn CowAgent into an ambient, omnipresent assistant supporting real-time voice conversations, live screen interactions, and dynamic generative UI.

### Key Deliverables
1. **Full-Duplex Voice & Audio Streaming**
   - WebRTC-based low-latency audio duplex streaming with barge-in / interruption detection.
   - Integration with OpenAI Realtime API, Gemini Multimodal Live API, and open-source streaming models (Whisper + Kokoro / XTTS).

2. **Generative UI & Interactive Artifact Canvas (`channel/web/`, `desktop/`)**
   - Dynamic component rendering (React/Vue/HTML/Mermaid widgets) rendered directly in chat streams and artifact panels.
   - Live code execution preview (web apps, charts, markdown decks) inside an isolated browser iframe.

3. **Continuous Visual Grounding & Screen Perception**
   - Real-time desktop screen watching and active cursor/keyboard steering (Computer Use protocol support).
   - High-throughput video stream analysis and document parsing with native vision models.

---

## 🏢 Milestone 5: Local Edge & Enterprise Architecture (Long-Term)

### Objectives
Empower air-gapped corporate deployments, edge computing on personal workstations, and high-concurrency cloud scaling.

### Key Deliverables
1. **Local-First Model Mesh**
   - 1-click bundled local inference through **Ollama**, **vLLM**, or embedded **llama.cpp**.
   - Zero-cloud-dependency mode: local chat, local embeddings, local ASR/TTS, and local vector search.

2. **Enterprise Multi-Tenant Backend Refactoring**
   - Decouple the monolithic Tornado/threading backend into an asynchronous FastAPI / ASGI core.
   - Distributed task execution powered by Celery / Redis / Temporal for long-running batch agent tasks.
   - Enterprise SSO integration (OIDC, SAML, OAuth2) with workspace multi-tenancy.

---

## 🛠️ Contributor & Engineering Track

For contributors looking to participate in this roadmap:

| Area | Recommended First Issues | Core Files to Read |
| :--- | :--- | :--- |
| **Tools** | Add sandboxed Docker runner for `Bash` | `agent/tools/bash/bash.py`, `agent/permission/policy.py` |
| **Memory** | Implement Qdrant vector backend | `agent/memory/vector_backend.py`, `agent/memory/storage.py` |
| **Models** | Add streaming tool-calling for new LLM providers | `models/bot_factory.py`, `models/openai_compatible_bot.py` |
| **Channels** | Expand multi-instance support to Telegram / Slack | `channel/channel_instances.py`, `channel/telegram/` |
| **UI** | Enhance artifact rendering and interactive graph views | `desktop/src/renderer/`, `channel/web/chat.html` |

