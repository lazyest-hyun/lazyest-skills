# Synthetic order reliability exercise

This is an invented implementation exercise based only on the topic of the public Cofa workspace product demo. It is not an actual exam task or an official starter. The public demo mentions Node.js, TypeScript, and PostgreSQL; this local fixture instead uses Node 24 native TypeScript execution and built-in SQLite because PostgreSQL and a TypeScript compiler are not installed. No network, gateway account, or dependencies are needed.

Retries currently create duplicate orders and payment failures can leave incorrect states. Find the cause, describe the smallest plan before modifying code, preserve the existing API response shape, and verify failures as well as success. Deliver changed code, tests, and DECISIONS.md explaining evidence and limitations.

Run `npm start` or `npm test`. `PORT` defaults to 8080; `DATA_DIR` selects local persistence (default `./data`). Keep `/health` and `STARTER_MARKER`. Business-policy clarification is available in STAKEHOLDER.md; read it if a consequential decision needs it.

## Existing API contract

- POST `/orders` accepts JSON `{ "customerId": "c1", "items": [{"sku":"s1","quantity":1}], "total":100, "paymentToken":"tok_ok" }`. Optional header `Idempotency-Key` already exists in client requests but is ignored by the buggy implementation.
- Valid creates return HTTP 201 with exactly `{ "orderId": "...", "status": "paid|failed|pending", "total": 100 }`. Preserve field names, types, and health behavior. A same-key replay uses that same success response shape and status code. Existing requests without a key continue to work.
- GET `/orders/{orderId}` returns the same response shape, or 404 `{ "error": "not found" }`.
- Invalid input returns 400 `{ "error": "..." }`. A valid request requires a nonempty customer ID, nonempty item list, positive integer quantities, nonnegative integer total, and a supported payment token. Unknown fields are ignored.

The fake local payment adapter supports tok_ok, tok_decline, tok_timeout_after, and tok_timeout_before. Its payment outcome can be looked up by the stable payment key. Its store represents an independent gateway side effect; API rollback cannot undo that effect. Do not modify this payment contract or make real payment calls.
