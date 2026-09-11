# Brief and evidence record

Use only the fields that affect this run. This record supports the five-field brief; it does not replace workspace discovery.

```text
Outcome:
Context:
Output:
Boundaries:
Verification:

Provenance:
- Workspace, branch/ref and commit; existing dirty paths and their ownership.
- Source/document path or URL, date inspected, and what it establishes.
- Facts still unverified or inferred.

Decisions needed:
- Choice or approval, who can resolve it, and which work depends on it.

Acceptance -> evidence:
- Criterion -> command/observation -> expected result -> observed result and source.
```

Remove the decisions section once every required decision is resolved. An empty placeholder is not a recorded decision. Mark checks PASS, FAIL, MANUAL, PENDING, or SKIPPED and state what each establishes. A manual criterion is complete only when the required observation or review is recorded; the helper cannot infer that review occurred.

## Iteration policy

After a meaningful attempt, capture:

```text
Attempt: hypothesis and action.
Evidence: actual output, relevant artifact, or direct observation.
Learned: what changed in the diagnosis and what remains uncertain.
Next: one useful experiment or independent task within the approved scope.
Unblock: missing input, authority, capability, or external change, if any.
```

Reference this record in the goal when the history would exceed its character limit. Keep the success criteria stable while adapting the approach. Do not rerun an unchanged failing action merely to accumulate turns; apply the chosen host's stopping rules.

## Unsuccessful stop

```text
Result: unfinished (blocked, paused, capped, failed launch, or unavailable capability).
Completed: criteria with decisive evidence.
Remaining: unmet criteria and pending manual checks.
Attempts: relevant actions, outputs, and what they ruled out.
Blocker: exact missing input or capability and who can resolve it.
Preserved state: workspace/ref, edits/artifacts, native goal state and queued work.
Next step: concrete action that enables safe continuation.
```

Do not change a success condition to describe partial progress. Retain the record and ask for direction before clearing, replacing, or restarting persistent work.
