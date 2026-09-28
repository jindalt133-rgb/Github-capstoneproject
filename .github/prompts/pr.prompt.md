# PR Prompt

Purpose: prepare a review-ready pull request summary and preview.
Agent: .github/agents/pr.agent.md
Required inputs: validated repository state, git diff/history, and verification evidence
Expected output: PR title, body preview, and reviewer checklist
Stop: show the preview and stop for explicit human approval before creating or updating any PR.
