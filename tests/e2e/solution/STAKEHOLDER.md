# Synthetic stakeholder clarification

These are invented business answers for this exercise, not evaluation answers or statements from real people.

- If the client supplies a key, the same key plus the same accepted request values identifies one order. Object field order and ignored extra properties do not change that identity. A different accepted payload with the same key should return 409 with the existing error object shape.
- Missing keys preserve legacy independent creates. Do not infer that two similar legacy purchases must be the same order.
- A declined payment is terminal failed; same-key retry must not charge again. An uncertain timeout is pending until reconciled, not proof of failure or permission to charge a new key.
- The local gateway lookup is authoritative: paid/declined are final and not_found means no charge was accepted. A same-key retry can reconcile and, only for not_found, safely retry the same gateway key. No background service is required.
- Restart and concurrent retries must not create a second keyed order or duplicate accepted charge. Those cases are synthetic robustness extensions beyond the public demo's brief requirements.
