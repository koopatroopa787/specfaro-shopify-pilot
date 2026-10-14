# Specfaro Shopify repair pilot

This public, disposable repository deliberately keeps a Shopify POS Session API
regression on `main`. The two failing Vitest files exercise staff lookup and
assignment against the 2026-10 `session.staffMember.value.id` shape. They fail
on the base commit so an autonomous worker can reproduce the error before
proposing a patch. Do not use this repository as a production Shopify app.

## Connected repair path

1. GitHub Actions fails on the default branch. The installed Specfaro GitHub
   App sends a signed `workflow_run` webhook to the controller.
2. The controller records the run and its exact commit under the repository's
   pilot consent policy. Its two-minute dispatcher wakes a private worker
   workflow. GitHub schedule remains a fallback.
3. The worker checks out the failed commit with a repository-scoped App read
   token. OpenHands with DeepSeek inspects only bounded failure context and
   current, version-matched official Shopify documentation. Project commands
   run in a credential-free, network-disabled Docker container.
4. The worker must see each identified test fail on the base and pass after a
   narrow production-code patch. Build, full tests, and an additional behavior
   check must pass. A separate GitHub runner rechecks the source and repeats
   the patch and test replay from a fresh checkout.
5. For this selected pilot repository only, a verified result can create a
   draft pull request. A person still reviews it; the worker does not merge or
   deploy it. The report states that no live Shopify response or POS device
   preview was tested.

The App uses short-lived, selected-repository tokens. The DeepSeek key stays
on the Specfaro controller; the private worker uses a job-scoped model gateway.
The pilot repair PRs are examples, not proof that arbitrary repositories can
be fixed. The current intake supports up to four discoverable Node or Vitest test files
for one exact Shopify API version and abstains when evidence is weak.

## Pilot references

- [Two-file failed CI run](https://github.com/koopatroopa787/specfaro-shopify-pilot/actions/runs/38536118137)
- [Verified draft PR #7](https://github.com/koopatroopa787/specfaro-shopify-pilot/pull/7)

This README revision also starts a fresh default-branch CI run to verify the
latest worker and controller revision against the same known regression. The
expected state of `main` remains failing until a repair PR is reviewed and
merged deliberately.
