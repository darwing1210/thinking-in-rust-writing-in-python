# Review the article ingestion service (with design skills)

You are reviewing `src/ingest/before/` in this repository.

Read these skills first, in order:

1. `skills/python-design-review/SKILL.md`
2. `skills/explicit-error-handling/SKILL.md`
3. `skills/model-valid-states/SKILL.md`
4. `skills/intentional-immutability/SKILL.md`

Then review the before-code against those skills.

Constraints:

- Do not look at `src/ingest/after/` until you have written the review.
- Do not add dependencies.
- Do not wrap every function in Result.
- Name the trade-off for each proposed change.

The service must still handle success, missing articles, invalid titles,
upstream timeouts, enrichment, and job lifecycle.
