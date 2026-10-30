# Add structure only for real requirements

Data: use local in-memory or file data when that satisfies the task. If persistence or concurrent sharing is required, choose the simplest supported store. Define only needed entities, identifiers, constraints, and access boundaries. Normalize where an actual update anomaly matters; avoid speculative entities. Check migrations against disposable data before a live mutation.

Security: for auth or shared records, verify authorization at the server boundary and test a cross-user denial. For untrusted input, validate at entry and use parameterized queries. Keep secrets server-side and out of logs, browser bundles, and Git. Add only controls relevant to the exposed surface. A deadline does not permit bypassing authorization or exposing credentials.

Infrastructure: reuse the provided runtime. Introduce a service only when an acceptance condition needs it. Do not change accounts, keys, billing, security settings, or destructive production state without applicable authorization. A demo may use labeled synthetic data, but must not disguise a mock as a working integration.
