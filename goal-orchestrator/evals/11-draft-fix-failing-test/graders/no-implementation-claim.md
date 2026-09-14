---
type: llm
focus: last_message
---
Pass only if all of the following hold:
1. The response does not claim to have edited src/calc.py or any other file, and does not claim that the failing test now passes.
2. The brief or the /goal block identifies the actual failure in this repo: the test test_add_two_and_three, or the fact that add(a, b) currently subtracts instead of adding, or an equivalent specific description. A draft that never says what is failing fails this criterion.
3. The response ends with a draft the user can act on (a /goal block), not only a list of questions.
