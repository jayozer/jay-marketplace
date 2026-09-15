---
type: regex
target: last_message
match: contains
weight: 0.5
---
(?=[\s\S]*?Outcome:[\s\S]*?\n/goal )(?=[\s\S]*?Context:[\s\S]*?\n/goal )(?=[\s\S]*?Output:[\s\S]*?\n/goal )(?=[\s\S]*?Boundaries:[\s\S]*?\n/goal )(?=[\s\S]*?Verification:[\s\S]*?\n/goal )
