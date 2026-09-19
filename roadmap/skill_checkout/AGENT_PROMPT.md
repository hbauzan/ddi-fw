# Successor agent — copy-paste prompts

## Understand only (no edits)

```text
Read roadmap/skill_checkout/README.md and follow its mandatory reading order through 07-overapplication-risks.md.
Language of that folder is English and RFC 2119.
Do not edit .agents/ or ddi_fw/.
Then summarize in the user's language: (1) verdict, (2) three layers, (3) what must stay locked, (4) what to scope, (5) residual IDE/HF catalog risk.
Do not propose cosine-in-decide, product streaming, or deleting product axioms.
```

## Implement all remediation tickets

```text
Read roadmap/skill_checkout/09-execution-spec.md first, then 08-recommended-remediation.md.
Execute tickets SC01 through SC06 in order (SC04 and SC06 may run in parallel with SC01 because they touch other files; SC03 after SC01).
Hard non-goals in roadmap/skill_checkout/README.md apply.
Do not edit ddi_fw/. Do not merge Deletor. Do not change the BGE-M3 pin.
Do not git commit or push unless I explicitly ask.
Verify with the greps in 09-execution-spec.md §9.4.
```

## Implement one ticket

Replace SC0X with the id. Copy the “Copiable prompt” from that ticket file instead if present.

```text
Execute roadmap/skill_checkout/tickets/SC0X-*.md
Read roadmap/skill_checkout/09-execution-spec.md.
Do not expand scope. Do not touch ddi_fw/. Do not commit unless I ask.
```
