# Specfaro end-to-end pilot fixture

This deliberately broken, public Shopify POS example is for a disposable test
repository. Its regression checks the 2026-10 Session API staff member shape.
The default-branch CI failure triggers `Specfaro pilot repair`, which asks the
live Specfaro site for one candidate. A GitHub-hosted runner verifies that the
regression fails before the patch and passes after it, then checks build and
tests. A second job opens a draft PR only for a validated artifact.

No Shopify credentials are used. The report must still say the device preview
and live provider response have not been checked when applicable.
