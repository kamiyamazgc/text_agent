# Codex Manual Summary

- Codex is a cloud-based software engineering agent that automates tasks such as bug fixing, code review, refactoring, and responding to user feedback.
- To use Codex, first connect your GitHub repository by authenticating with your GitHub account through the ChatGPT web interface, granting permissions to clone and push pull requests.
- Once connected, submit tasks through the Codex web interface, choosing between:
  - "Ask" mode (for advice, audits, or architecture questions)
  - "Code" mode (for automated code changes, refactors, or bug fixes)
- When a task is submitted:
  - Codex launches a Docker container
  - Clones your repository
  - Runs any setup scripts
  - Disables network access for security
- The agent iteratively writes code, runs tests, and checks its work, following any lint or test commands defined in an AGENTS.md file.
- After completing the task, Codex presents a code diff or follow-up tasks, allowing you to open a pull request or request further changes.
- For best results, provide clear, specific prompts and point Codex at particular files or packages.
- Advanced users can customize the environment and setup commands to fit their project’s needs.
