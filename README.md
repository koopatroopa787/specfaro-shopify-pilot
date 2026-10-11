# Specfaro end-to-end pilot fixture

This deliberately broken, public Shopify POS example is for a disposable test
repository. Its regression checks the 2026-10 Session API staff member shape.
A failed default-branch CI run can trigger `Specfaro pilot repair`. The repair
job collects the failed test log, infers the provider, version, test file, and
commands, then runs OpenHands with DeepSeek in an ephemeral GitHub-hosted runner.
It searches official documents, checks a candidate in a fresh project copy,
and can give the agent one bounded retry. No checked-in issue prompt or command
file is required. The current evaluation job does not publish a PR.

The OpenHands evaluation workflow is gated by the repository variable
`SPECFARO_OPENHANDS_EVAL_ENABLED=true` and requires the repository Actions
secret `SPECFARO_DEEPSEEK_API_KEY`. Until both are configured, the repair job
is skipped. It has read-only permissions and uploads a report and candidate
patch; it cannot open a PR. The model key is removed from the worker process
environment before the agent terminal starts. No Shopify credentials are used.
The report must still say the device preview and live provider response have
not been checked when applicable.
