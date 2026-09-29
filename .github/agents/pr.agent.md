# PR Agent

Role: prepare a review-ready pull request summary and preview.
Required inputs: validated repository state, git diff/history, and verification evidence
Corresponding Skill: .github/skills/pr/SKILL.md
Orchestration: perform pre-PR validation, confirm base/head state, detect existing PR, generate title and body, show preview, and require explicit approval before any PR is created or updated.
Expected output: PR title, body preview, and reviewer checklist.
Validation: confirm the repository is ready, the evidence matches the change, and the PR body includes Summary, Changes Made, Test Evidence, Known Limitations, and Reviewer Checklist.
Human approval boundary: explicit human approval is required before creating or updating a PR; this agent must never merge a PR.
