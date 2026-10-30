# Direct review of the preparation package

This review reads the actual skill, installer, synthetic task contract, solution, and decision journal; passing test counts alone are not the conclusion. It concerns this local fixture, not an unseen assessment problem or production payment service.

## Requirement → design

- **Do not duplicate a keyed request.** The solution normalizes only accepted fields, reads/reserves under SQLite `BEGIN IMMEDIATE`, and commits before awaiting the gateway. Same-key requests through this service therefore select the same persisted order, including across processes. No-key requests deliberately retain legacy independent-create behavior. This is justified by the invented stakeholder contract, not inferred from the brief public demo.
- **Keep the API contract.** The response helper still returns exactly orderId/status/total, creation/replay remains 201, existing GET/health behavior remains, and conflict uses the existing error-object shape with 409. Ignored extra fields do not accidentally change identity. The gateway and server starter files were preserved.
- **Recover payment state safely.** The persisted order ID is the gateway's stable key. Pending requests look up the gateway before charging. A known paid/declined result becomes paid/failed; a timeout with no accepted result remains pending. State updates only target pending rows so a stale uncertain observation cannot erase a final result.

These mechanisms are visible in [orders.ts](../e2e/solution/src/orders.ts), not merely in assertions. The [synthetic stakeholder policy](../e2e/starter/STAKEHOLDER.md) explicitly supplies the meaning of same-key, conflicts, legacy requests, and authoritative not_found.

## Failure paths and what the evidence does not prove

- The gateway is a separate SQLite side effect, so rolling back an order transaction cannot pretend to undo an accepted payment. The solution correctly reconciles that boundary instead of inventing rollback of money movement.
- An immediate authoritative lookup may resolve an accepted-charge timeout as paid. Requiring an intermediate pending response would be an invented rule; the oracle was corrected accordingly and that correction is disclosed.
- The fake gateway promises authoritative not_found and key-based charge deduplication. A real gateway with delayed lookup visibility would need its own contract; this exercise does not justify applying the same retry policy blindly to it.
- Historical duplicate transactions and incorrect terminal statuses are left alone. The solution reuses an existing first keyed row but cannot reverse past independent charges. Its journal says so; it is not a data-repair or refund tool.
- The database does not have a new UNIQUE constraint for request_key. All create paths in this service serialize their lookup/insert, which the separate-process checks exercise. A direct writer bypassing that service is outside that protection. This is an explicit fixture boundary, not a claim of schema-wide enforcement.
- The unchanged starter server maps unexpected errors to a 400 object. Real DB outage classification, body limits, credential handling for a real gateway, disk exhaustion, and arbitrary power loss are not established by these tests. The crash-window test constructs saved state rather than injecting an OS crash at an exact instruction.

## Simplicity

Only the order implementation, tests, and decisions changed in the completed exercise. No new package, auth system, cloud service, worker queue, distributed lock, external deployment, or background repair system was introduced. SQLite is used because the synthetic task really requires persistence and cross-process reservation. This does not turn database work into a requirement for static data or small UI edits.

The installed skill remains a short router with six conditional references. The actual rerun loaded data/risk/debug and later finish; it did not load clarify/research. Those selected references match the observed payload, persistence, failure, and delivery concerns. No latency improvement is claimed from this single run.

## Ordinary use and assessment fit

The first full native order run did not read the installed skill, so the original install-only approach was insufficient evidence for automatic use. The correction is a short conditional project-discovery hint, preserving the existing AGENTS content. The rerun used the same ordinary task request without a skill name and recorded metadata selection before body/reference reads. A separate small-label task with that hint read only project instructions and HTML.

This is observed native-proxy behavior, not CLI-host discovery. The actual CLI failed during app-server initialization on a read-only filesystem before the model ran. AGENTS overrides or a frozen host with different instruction discovery can still change the result; the exact provided environment was not entered or upgraded. The package's default instructions now use natural requests, with explicit invocation retained only as an optional diagnostic fallback.

The fixture is self-contained and uses fake local payments; it neither exports task content nor drives a browser. No assessment session, limited practice attempt, real question, private repository, personal key, or post-submission prohibited writing was used. The public product mock is clearly labeled as inspiration, not a public copy of a real assessment.

## Evidence quality for the parent reviewer

Read the [task](../e2e/starter/README.md), [synthetic policy](../e2e/starter/STAKEHOLDER.md), [actual solution](../e2e/solution/src/orders.ts), [solver journal](../e2e/solution/DECISIONS.md), [independent oracle](../e2e/oracle.py), and [rehearsal report](order-e2e.md) together. The solver journal is a self-reported execution record, not an exported raw host trace. The supervising evaluator independently reran the published solution's own tests and the hidden-during-solving HTTP oracle, and verified that the unchanged starter fails seven oracle cases. Raw per-tool native-host trace export was not available in this workflow; do not describe the journal as that export.

The fake gateway is not success-only: it has paid, declined, timeout before acceptance, and timeout after acceptance branches. The own tests and independent oracle exercise all four. A pending-plus-gateway-receipt fixture covers the external-success-before-order-state-save boundary without claiming a timed crash injection.

After this rehearsal, direct review made three narrow instruction changes: batch consequential clarification questions; distinguish expressly permitted in-environment model selection from external provider connections while preserving bans; and add three conditional sentences about external side-effect atomicity, stable keys/payload conflicts, and unknown timeout outcomes. These final wording changes were statically checked; no extra model rerun is claimed for them.

The useful result is narrower than “all cases are solved”: natural-request discovery improved in the tested proxy, the synthetic API works under its stated contract, and the remaining runtime/payment/migration limitations are exposed for direct review.
