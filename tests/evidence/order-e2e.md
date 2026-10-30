# Actual synthetic order rehearsal — 2026-10-30

## Source and boundaries

The [public Cofa product workspace mock](https://www.getcofa.com/brochure-v2/workspace-mock.html) describes duplicate-order retries, safe payment-failure recovery, an unchanged API contract, and code/tests/decision evidence. It is a product demonstration, not a real assessment question, practice attempt, or downloadable official starter.

We authored a new synthetic starter and a fake local payment adapter. Concurrency and process restart are our additional checks. The demo names Node.js/TypeScript/PostgreSQL; this fixture uses Node **v24.19.0** native TypeScript execution and built-in SQLite because no PostgreSQL server or TypeScript compiler was installed. It does not validate PostgreSQL behavior or TypeScript type checking.

The natural request was a newly composed conversational Korean request to repair retry duplication and payment recovery within 180 minutes, preserving the API and doing real tests. It contained no skill name or loading path. This report paraphrases that request and publishes no personal writing samples, private task, participant link, screenshot, or real payment data.

## Execution method and initial failure

An actual CLI attempt used the existing ChatGPT login with Codex CLI **0.163.0** and requested `gpt-6.1-sol`. It exited before model execution: `failed to initialize in-process app-server client: Read-only file system (os error 30)`. We did not relocate credentials, change permissions, update the agent, or consume a limited assessment practice session.

We instead used clean native agents explicitly configured as **gpt-6.1-sol, medium**, with the installed project files and the same natural task. No additional paid API, external model connection, browser/desktop automation, or real exam runtime was used. These are native-proxy execution results, not proof of CLI-host or frozen exam-runtime skill discovery.

The first complete order run implemented a working solution, but **did not discover/read the installed skill**. Its first `npm test` passed the starter's single legacy success test, which missed the real defects. An independent HTTP oracle run against the unchanged starter failed **7 of 9** checks. The first solution's own tests passed **12/12** and the corrected independent oracle passed **9/9**, but that did not satisfy automatic-application evidence.

## Minimal correction and clean rerun

The installer now preserves existing `AGENTS.md` content and adds one approximately 50-word discovery hint. It asks for metadata inspection only for substantial deadline-driven implementation, lets trivial local text edits proceed directly, and loads only a selected body and relevant references. It does not inject every reference or name a skill in the user's request. `--no-project-guide` skips this hint.

A fresh copy of the exact original starter was installed using the revised installer. A new native Sol 6.1 agent, without the earlier solution or oracle, completed the same task. Its recorded ordering was:

1. Read ordinary project instructions, README, and package configuration.
2. Inspect only skill name/description frontmatter; select `ship-small`.
3. Read its body, then starter orders/payment/server/tests and the synthetic stakeholder answers.
4. Read data/risk/debug references for the actual contract and defect; read finish only during delivery preparation. The clarify/research references were not loaded.
5. Run the starter test (**1/1 pass**), then actually reproduce duplicate IDs and an incorrect failed status after an accepted payment timeout.
6. Implement the smallest local change, expand tests, start the actual server, and verify through loopback HTTP and process restart.

The first expanded own-test run was **11/12** because a test compared SQLite's null-prototype row object directly with an ordinary object. The solver corrected that assertion to compare the count value; this was a test-expression correction, not a product success claim. Final own tests were **13/13**. The independent oracle, never shown to the solver, passed **9/9**.

The observer's monotonic envelope was **262.894 seconds**, from **2026-10-30T16:41:05.007908Z** before dispatch to **16:45:27.901675Z** when completion was observed. This includes dispatch, tools, execution, and observer delay. It is one run, not model latency or a performance guarantee. The first run's full elapsed time was not measured.

## Independent checks and evaluator correction

The HTTP oracle checks exact response fields/status codes, legacy no-key behavior, canonical same-key replay, conflicting payloads, concurrent requests, terminal declines, timeout before/after a charge, restart persistence, invalid input, and valid zero totals. It counts accepted charges in the independent fake gateway store.

An early oracle incorrectly required the first accepted-charge timeout response to be pending. A solver can immediately query the authoritative gateway and correctly return paid, so that assertion was corrected to accept pending or paid while still requiring one accepted charge and safe same-key restart/replay. This oracle correction is disclosed; the starter still fails 7/9 under the corrected check. We did not alter the oracle to excuse duplicate orders, charges, contract changes, or unsafe failure handling.

A separate fresh Sol 6.1 negative-control run with the revised guide received only a simple Korean button-label request. It read **AGENTS.md and index.html**, changed **only index.html**, and checked complete content equality apart from the label. It did not read skill bodies/references, plan a workflow, introduce a database, or invoke security work.

## Replay without any model calls

From the preparation branch root, with Node 24 and Python 3:

```sh
cd tests/e2e/solution
npm test
cd ../../..
python3 tests/e2e/oracle.py tests/e2e/solution
```

The solution runs **13 own tests** and **9 independent HTTP checks**. To observe the original defects, run the oracle against `tests/e2e/starter`; **7 failures are expected**. The starter itself still passes its one narrow legacy test. All oracle databases and servers are disposable local fixtures. The installation tests remain `python3 tests/check.py`.

To prepare a new isolated model run, copy the starter into a fresh temporary project, run the repository installer against that project, open a fresh authorized session there, and use a natural request. Do not pass the solution, oracle, or expected results to that solver. No script here calls any model or assessment service.

## Limits

The completed solution and its [DECISIONS.md](../e2e/solution/DECISIONS.md) retain the API shape and existing stack. No new service, dependency, account, key, or background worker was added. Existing historical duplicate trades or incorrect terminal states are not automatically merged/refunded; real gateway, PostgreSQL, disk failure, and arbitrary power-loss behavior remain unverified. The crash-window fixture constructs a pending order plus gateway outcome; it is not a timed OS crash injection. Real process restart and separate-process concurrency were executed.

During the solver's startup smoke, interrupting npm left its child server alive; the solver identified and terminated that server and removed disposable data. No active server or assessment session is being maintained. Native-proxy discovery after the installation hint was observed once; automatic host discovery and the exact frozen provided version remain unverified.
