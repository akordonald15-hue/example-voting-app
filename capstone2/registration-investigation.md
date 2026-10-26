# Registration HTTP502 investigation

The Web adapter maps `/api/user/register` to User `/register`. Its error handler
returns502 when the outbound HTTP request errors, including the configured
15-second socket inactivity timeout. User and MongoDB do not generate this
particular `upstream unavailable` response. The retained failed Locust request
lasted about18.9seconds and returned502. That is consistent with a proxy timeout
on this memory/CPU-constrained workstation; old logs did not record the underlying
socket error code, so the exact historical error is not proven.

Two configuration faults were fixed separately: namespace omitted from the
load-generator manifest, and trailing-slash HOST producing double-slash routes.
Neither should be confused with a User500 response. No timeout was increased,
no request failure was suppressed, and no alternate registration route was used
by the corrected load generator.

After dependencies stabilized, independently issued direct User and Web-proxied
registrations both returned200 twice. The saved comparison records only status,
duration and endpoint; random synthetic credentials and response bodies were not
exported. `evidence/runtime/registration-direct-proxy.json` records the repeat
comparison before the bounded three-minute, one-user test. The workload still
uses registration, login, catalogue, cart, shipping and simulated payment.

User is the pinned upstream demonstration image. Its source logs request bodies
and stores demo passwords in plaintext. Never use real credentials. Do not export
raw User logs or users collections into the submission. This is not production
identity management. No AWS or Voting App resources were involved.

The subsequent bounded run registered successfully in239ms and logged two successful logins. It still failed five downstream requests: four Shipping `/codes` calls and one Cart add. Shipping source queries its SQL repository for `/codes`; its logs show the handler was entered and historical Hikari thread-starvation warnings. These establish downstream latency, but do not prove whether SQL access, pool waiting or host scheduling caused the Shipping timeout. No dependency was bypassed or proxy timeout increased.
