# Runtime scan status — incomplete

2026-10-26: attempted an all-severity Web runtime-image scan with the existing
Trivy 0.75.0 container. Vulnerability database download/extraction failed with:

```
FATAL Fatal error: init error: DB error: failed to download vulnerability DB
write /root/.cache/trivy/db/trivy.db: cannot allocate memory
```

Scanner exit code: **1**. No clean result or zero-CVE claim is valid. The other
four local image scans were not completed. The Windows Trivy executable also
failed to start under local Application Control; no policy was changed.

Separate npm audit receipts for Cart/Catalogue are successful dependency audits,
not substitutes for OS/runtime Trivy scans. Alpine focus images were inspected
and contain musl **1.2.6-r3**. Legacy supporting upstream images (including MySQL
5.7) require separate security review and are not production approved.

Retry scanning only with a valid complete vulnerability database and sufficient
local memory. Preserve scanner warnings/errors; do not suppress vulnerabilities
or treat unavailable database results as clean.
