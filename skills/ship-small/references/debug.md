# Diagnose one failing path

Reproduce the smallest failing input and record expected versus actual behavior before editing. Trace only the boundary that loses or changes the value: UI state, request, response, storage, or reload. Compare identifiers and types before replacing architecture.

For a saved item that disappears on refresh, test create → read → restart/refresh → read. Check whether saving reaches the intended persistent store and loading reads it back; a success toast alone proves neither. Fix the responsible path, rerun the reproduction and one nearby regression, and report the actual evidence. Under a Computer Use ban, perform permitted CLI equivalents and request manual preview confirmation separately.

After two unsuccessful speculative changes, stop broad editing, inspect the first failing boundary, and revise the hypothesis. Preserve the starter and unrelated working behavior. Do not fix a local persistence bug by introducing a remote database unless a real requirement needs one.
