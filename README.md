# Identifier claim audit

This offline static tool compares selected documentation statements with Python source call shapes. It never executes the inspected source or contacts a network. It reports high-severity contradictions and medium-severity test-only support.

```sh
uuid-validation-claim-audit audit . --verbose
python3 -m uuid_validation_claim_audit audit . --json
```

The optional path defaults to the current directory. Use `--ignore PREFIX` repeatedly to skip path prefixes and `--fail-on medium` to fail on test-only support. Exit status is 0 for a passing threshold, 2 for a finding at or above it, and 1 for usage or input errors. Root README prose and Markdown below a docs directory are inspected; fenced blocks are ignored and inline code counts. Matching ignores case, expands contractions, treats hyphens as spaces, and uses exact phrases. Source is parsed without execution; test files are separate from production. Symlinks, examples, fixtures and docs source are excluded.

## Differentiation

This family concerns the format of a universally unique identifier string. Other families address generic input validation, ISBN book numbers, ISSN serial numbers, IBAN bank accounts, payment processing, credit-card extraction, account authentication, password verification, password hashing, password generation, PDF encryption, email sending, SMS, document extraction, barcode scanning, email addresses, phone numbers, password strength, JSON Schema, dates, credit cards, domains, URLs, IP addresses, and hardware addresses. Account number formatting, generation, registry lookup and business identifier codes are separate. Identifier generation and component reads do not judge an input. Other claim families cover spreadsheets, word documents, presentations, PDF operations, tables, OCR, signatures, screen recording, video, QR and barcode generation, audio, speech and music.

The neighbouring checks include ISBN-10 and ISBN-13 check digits, the ISSN check digit, and the IBAN check digit. Authentication can prove account control by a one-time code or confirmation link. Other distinct operations include decoding JSON, matching a regex, splitting or fetching a web address, resolving DNS, encoding an account number in a barcode, and extracting an account number from a document. Identifier components include hex, version and variant. PDF operations include extraction, generation, merging, splitting, rotation, forms, watermarking, redaction, compression and annotation. Audio families include mixing, generation, editing, source separation, speech recognition, text-to-speech, noise suppression, music generation and transcription.

## Limitations

The following wording can refer to a database or remote lookup; human review is needed.

```text
validate uuid
```

The following wording can refer to a manual runbook step; human review is needed.

```text
check uuid
```

The following wording can refer to a roadmap item; human review is needed.

```text
uuid validation
```

The following wording can refer to a hosted page; human review is needed.

```text
uuid validator
```

The following wording can refer to reader advice; human review is needed.

```text
valid uuid
```

The following wording can refer to a successful lookup; human review is needed.

```text
uuid is valid
```

The following wording can refer to a specification section; human review is needed.

```text
uuid string validation
```

The following wording can refer to an allow-list check; human review is needed.

```text
validate uuid string
```

The following wording can refer to a registry lookup; human review is needed.

```text
verify uuid
```

The following wording can refer to a length-only check; human review is needed.

```text
detect invalid uuid
```

The following wording can refer to a theoretical discussion; human review is needed.

```text
uuid well formed
```

The following wording can refer to a generated identifier; human review is needed.

```text
is valid uuid
```

The following wording can refer to a spacing-only check; human review is needed.

```text
uuid format validation
```

The following wording can refer to a metadata version label; human review is needed.

```text
validate uuid version
```

The following wording can refer to a manual runbook step; human review is needed.

```text
uuid check
```

The following wording can refer to a specification section; human review is needed.

```text
uuid string check
```

The following wording can refer to a database lookup; human review is needed.

```text
validate universal unique identifier
```


A uuid.uuid1, uuid.uuid3, uuid.uuid4 or uuid.uuid5 call alone is excluded: it mints an identifier rather than judging input.


A component read alone is excluded: hex, int, bytes, bytes_le, fields, time, clock_seq, node, version, variant and urn do not judge input.


A uuid.getnode call alone is excluded: it obtains a hardware address.


A Pydantic UUID1, UUID3, UUID4 or UUID5 annotation or construction alone is excluded.


A regular-expression match alone is excluded.


An alias chain may be missed.


An unused import is excluded.


A roadmap claim is still a claim.


A changelog claim is still a claim.


A TODO claim is still a claim.


An unlisted denial may be missed.


A top-level changelog is outside the documentation scope.


Evidence split between modules is missed.


Locally defined names shadow imported routes.


Dead code counts.


A subprocess invocation is excluded.


A generic input check alone is excluded.


An email check alone is excluded.


A phone number check alone is excluded.


A URL check alone is excluded.


An IP address check alone is excluded.


A domain check alone is excluded.


An ISBN check alone is excluded.


An ISSN check alone is excluded.


An IBAN check alone is excluded.


An extraction call alone is excluded.


A locally defined generic name is shadowed.


A generic call through an alias chain may be missed.


Exact wording is required; meaning is not inferred.


Other programming languages are invisible.


Runtime-only routes are invisible.
