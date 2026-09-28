# Copilot Instructions

- Approved artifacts are the source of truth: requirements, architecture, design review, implementation plan, and verification evidence.
- Use the SDLC workflow in this order: Prompt -> Agent -> Skill -> Validate -> Human Approval.
- Later phases consume only approved earlier artifacts; do not silently modify approved requirements.
- Keep changes minimal, scoped, and relevant to the current phase.
- Ask only blocking questions; do not expand scope beyond approved requirements.
- Never expose secrets or sensitive values in prompts, artifacts, or reports.
- Read only files relevant to the current phase.
- Stop between SDLC phases for explicit human approval.
- Never create, update, or merge a PR without explicit human approval.
- Do not implement application code until approved SDLC artifacts exist.
- Keep framework files concise and token-efficient; avoid repeating the same rules across Prompt, Agent, and Skill.
