---
type: llm
focus: last_message
---
The user pasted about thirty numbered requirements (R01 to R30). Pass only if all of the following hold:
1. The /goal block does not reproduce the pasted requirements verbatim or near-verbatim. It may reference them by ID ("R01-R30", "R19, R22, R28") or summarize them in a few bullets.
2. The supporting detail lives in the brief or in a reference outside the /goal block, so the /goal block stays compact (well under 4,000 characters).
3. The /goal block has a Done when section whose bullets are observable, and its Verification section includes the repo's real test command (python3 -m unittest discover -s tests). Do not judge the quality of the evidence fields here; another grader covers that.
4. The response does not claim to have implemented anything.
