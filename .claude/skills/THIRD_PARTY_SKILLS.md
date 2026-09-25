# Third-party Claude Code skills

Vendored so they are available in every Claude Code session on this repository.
Both are MIT-licensed; each skill directory carries its upstream LICENSE.

| Skill(s) | Upstream | Commit |
|---|---|---|
| ui-ux-pro-max | https://github.com/nextlevelbuilder/ui-ux-pro-max-skill | dcc40ff |
| brainstorming, dispatching-parallel-agents, executing-plans, finishing-a-development-branch, receiving-code-review, requesting-code-review, subagent-driven-development, systematic-debugging, test-driven-development, using-git-worktrees, using-superpowers, verification-before-completion, writing-plans, writing-skills, diagnosing-superpowers | https://github.com/obra/superpowers | 5bf4e78 |

Superpowers' session-start hook is intentionally not installed; the skills load on demand.
To update, re-copy the skill directories from the upstream repositories at a newer commit.
