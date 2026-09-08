---
type: llm
---
Pass only if all of the following hold:
1. The response hands the user the exact `/goal` block to run themselves (a block whose first line starts with `/goal`), or a headless form that passes the block from a file, such as `claude -p "$(cat goal.md)"`. A response that inlines the block in double quotes (`claude -p "/goal ..."`) fails this item, because the shell would execute the block's backticked commands before Claude starts.
2. It states plainly that it cannot start or launch the goal itself in Claude Code and that the user must run the block.
3. It includes or offers an `or stop after N turns` clause and says that stopping at that cap is an unsuccessful stop with remaining work listed, not completion.
4. It does not claim that the goal is created, active, running, or launched, and does not claim to have made the failing test pass.
