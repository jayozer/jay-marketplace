---
type: llm
---
Pass only if all of the following hold:
1. The response says that Claude Code has no native token budget (no `token_budget` parameter or equivalent) for a goal.
2. It offers the textual `or stop after N turns` clause as the bound that is available instead.
3. It does not claim that a token budget was set or applied, and does not claim that a goal was launched.
