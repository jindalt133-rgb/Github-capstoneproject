# Implementation Prompt

Purpose: execute only the approved, unblocked work defined by the validated SDLC artifacts.
Agent: .github/agents/implementation.agent.md
Required inputs: docs/requirements.md, docs/architecture.md, docs/design-review.md, and approved docs/impl-plan.md
Expected output: implementation in src/ and tests/
Stop: validate results and stop for human approval before continuing to review or verification.
