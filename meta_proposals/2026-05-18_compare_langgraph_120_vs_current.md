# Meta-Loop Proposal: 2026-05-18 — compare_langgraph_120_vs_current

**Goal:** Compare LangGraph 1.2.0 vs current loop_manager.py. Score on: free provider support, simplicity, async, observability, LOC delta. Recommend keep, migrate, or hybrid.
**Generated:** 2026-05-18 14:11
**Status:** FLAGGED (below 8.5)
**Mode:** DRY-RUN (proposal only)
**Primary score:** 8.03 / 10  (provider: openrouter)
**Second opinion:** 7.73 / 10  (provider: mistral_code)

## Loop Stats

| Metric | Value |
|---|---|
| Reports analysed | 8 |
| Avg score | 8.88 / 10 |
| Common stop reasons | db_cache_hit, goal_met |
| Avg cost per run | £0.001771 |
| Slowest provider | openrouter |

## Analysis

## Analysis: LangGraph 1.2.0 vs. current loop_manager.py

**Objective:** Compare LangGraph 1.2.0 and `loop_manager.py` on free provider support, simplicity, async, observability, and LOC delta, then recommend a strategy.

---

### 1. Free Provider Support

*   **LangGraph 1.2.0:** LangGraph operates as a framework for building stateful applications, including LLM agents. It doesn't directly "ship" with provider integrations but facilitates easy integration with LLM libraries like LangChain or standalone LLM clients. Its strength lies in orchestrating complex workflows, not in providing LLM models themselves. Therefore, its ability to support "free providers" depends entirely on the LLM clients it's used with. If integrating with models accessible via free tiers or open-source libraries (e.g., Hugging Face, local models, or providers with generous free tiers), LangGraph can fully leverage them.
*   **`loop_manager.py`:** The provided snippet of `loop_manager.py` does not explicitly show LLM provider integrations. However, the `AAFLCore` and `CostGuard` imports, along with the `AGENT_SYSTEM` prompt, suggest it interacts with LLMs. The "Provider avg scores" table indicates usage of `gemini_flash`, `mistral_code`, and `openrouter`. `gemini_flash` and `mistral_code` can be accessed via free tiers or APIs that have free usage limits. `openrouter` aggregates various models, some of which are paid. Without direct code inspection, it's difficult to definitively say how it handles free vs. paid, but the presence of `CostGuard` implies cost awareness.

**Score:**
*   LangGraph 1.2.0: 4/5 (Facilitates integration, dependent on user's choice of LLM client)
*   `loop_manager.py`: 3/5 (Appears to use models with free tiers, but implementation details are unclear; might rely on specific APIs.)

---

### 2. Simplicity

*   **LangGraph 1.2.0:** LangGraph is designed to simplify the creation of complex, stateful applications and agentic workflows. It introduces concepts like nodes, edges, and graphs, which can abstract away much of the underlying orchestration logic. For developers familiar with state machines and graph-based systems, it can be highly intuitive. The learning curve involves understanding its graph paradigm and state management.
*   **`loop_manager.py`:** The current `loop_manager.py` appears to be a monolithic script implementing a specific loop: `plan → work → verify → store → cost check`. It directly imports and uses various components (`AAFLCore`, `memory_bank`, `researcher`, `cost_guard`, `evaluator`). While it has a clear purpose, the interconnectedness of these modules within a single file might make it less modular and harder to alter or extend compared to a framework designed for broader use cases. The "Minimum Viable Loop Engine" description suggests it's lean but might lack the generalized structure of a framework.

**Score:**
*   LangGraph 1.2.0: 4/5 (Higher abstraction, potentially steeper initial learning curve but simpler for complex flows)
*   `loop_manager.py`: 3/5 (Specific, likely easier to grasp for its existing function, but less modular for extension)

---

### 3. Async Support

*   **LangGraph 1.2.0:** LangGraph is built with modern Python practices in mind and fully supports asynchronous operations. It's designed to work seamlessly with `asyncio` and is compatible with async libraries for LLM interactions, enabling non-blocking execution for I/O-bound tasks like API calls.
*   **`loop_manager.py`:** The provided code snippet for `loop_manager.py` does not contain any explicit `async` or `await` keywords. It uses standard synchronous Python imports and function definitions. Unless `AAFLCore` or other imported modules handle async internally and are called in a way that facilitates non-blocking, this implementation appears to be primarily synchronous.

**Score:**
*   LangGraph 1.2.0: 5/5 (Native and robust async support)
*   `loop_manager.py`: 1/5 (Appears to be synchronous based on the provided snippet)

---

### 4. Observability

*   **LangGraph 1.2.0:** LangGraph emphasizes clear state management and node boundaries. This structure inherently aids observability by making it easier to trace execution flow through defined nodes. It integrates well with logging and tracing tools, and its state-tracking capabilities allow for detailed inspection of intermediate steps. The Habr article hint about "Node boundaries rõ ràng" directly points to this advantage. Visualizing graph execution is also a common feature in such frameworks.
*   **`loop_manager.py`:** The `loop_manager.py` provides a basic report (`_write_report`) with stop reasons, iterations, and costs. It also logs provider performance and average scores. However, it lacks explicit features for deep tracing of the *internal* execution within each phase (`plan → work → verify → store → cost check`) or intermediate state inspection beyond what the individual modules might provide. The notification function (`_notify_done`) is an example of end-of-run feedback, not mid-run observability.

**Score:**
*   LangGraph 1.2.0: 4/5 (Inherently good structure for tracing, integrates with tools)
*   `loop_manager.py`: 2/5 (Basic end-of-run reporting and some aggregate stats, but lacks detailed execution tracing)

---

### 5. LOC Delta

*   **LangGraph 1.2.0:** LangGraph is a framework. A direct LOC comparison is not applicable. However, the *expected LOC to implement a similar workflow* as `loop_manager.py` using LangGraph would involve defining nodes for planning, working, verification, storage, and cost checking, along with a graph that orchestrates them. A rough estimate might be in the range of 100-300 LOC for the core graph definition and node implementations, assuming LLM clients and other utilities are imported. This would be *in addition* to the LangGraph library itself.
*   **`loop_manager.py`:** The provided snippet is 72 lines. Estimating the full script based on imports and structure, it's likely in the range of 150-300 LOC for the core loop logic, plus dependencies.

**LOC Delta Estimate (for equivalent functionality):**
*   LangGraph 1.2.0 (implementation): +100-300 LOC (for graph and nodes)
*   `loop_manager.py` (existing): ~150-300 LOC (for monolithic loop)

The LOC delta is therefore expected to be neutral to slightly positive if migrating to LangGraph for a similar monolithic workflow, but potentially lower if LangGraph's structure allows for cleaner, more reusable components.

---

## Recommendation

**Recommendation: Migrate**

**Justification:**

1.  **Async Support:** The current `loop_manager.py` appears to be entirely synchronous, which is a significant bottleneck for modern agentic applications that rely heavily on I/O-bound operations. LangGraph's robust `async` support is a critical advantage.
2.  **Observability & Simplicity for Complexity:** While `loop_manager.py` is specific and currently manageable, LangGraph's structured approach (nodes, edges, state) offers superior observability for complex, multi-step workflows. This structure inherently simplifies debugging and understanding the agent's behavior in detail, which is crucial for iterative improvement.
3.  **Future-Proofing & Scalability:** LangGraph is a framework designed for building complex, stateful applications and agent loops. Relying on a single, monolithic script like `loop_manager.py` can lead to technical debt and make scaling or adding new features more challenging. Migrating to LangGraph provides a more scalable and maintainable architecture.
4.  **Provider Support:** While LangGraph doesn't bundle providers, its design makes it trivial to integrate with any Python LLM client, including those offering free tiers or open-source models. This flexibility aligns with the requirement for free provider support, and it will be easier to manage these integrations within a well-defined framework.

The initial investment in understanding LangGraph's paradigms will pay off in terms of development speed, debugging ease, and the overall robustness and scalability of the AAFL system. The LOC delta is comparable, suggesting a migration is feasible.

## How to Apply

If this proposal contains a `CHANGE FILE` block, pass `--apply` to meta_loop.py:
```
python meta_loop.py --apply
```
This snapshots backups/, writes the change, runs regression_test.bat,
and restores from snapshot if the regression score drops.

---
*Generated by meta_loop.py — AAFL Self-Improving Meta-Loop*