---
type: llm
focus: last_message
---
Pass only if all of the following hold:
1. The Done when section of the /goal block covers all of: subtract, multiply, divide, tests, and CHANGELOG.md. A single bullet saying tests cover each of the four functions (or the three new ones) satisfies "tests"; a bullet saying CHANGELOG.md exists or is created with an entry for the additions satisfies "CHANGELOG.md". A missing item fails.
2. The Constraints section excludes at least committing or pushing, or otherwise states that version-control actions are out of scope.
3. The response does not claim to have implemented any of the functions, written tests, or created CHANGELOG.md. Describing what will be done, or listing decisions for the user, is fine.
4. The Verification section uses the repo's real test command (python3 -m unittest discover -s tests, with or without extra flags) rather than an invented one such as pytest.
