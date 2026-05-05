# OpenAI Moderation Run Diagnosis

Status: paused for diagnosis.

Observed behavior:

- The full OpenAI Moderation run started correctly.
- The run hit `Too Many Requests` on the first dataset (`openaimod`).
- First attempt, `API_BATCH_SIZE=32`, no sleep:
  - Rate limits appeared at batches around `96:128`, `160:192`, and `256:288`.
  - Cache reached 256 examples.
- Second attempt, `API_BATCH_SIZE=8`, `API_SLEEP=0.75`:
  - Resumed from 256.
  - Still hit rate limits around `312:320`.
  - Cache reached 312 examples.
- Third attempt, `API_BATCH_SIZE=32`, `API_SLEEP=22`:
  - No new 429 was observed before the process was stopped for diagnosis.
  - Progress after 312 was not preserved because of the checkpointing issue below.

Root causes:

1. OpenAI account/project rate limit, not code failure.
   The moderation endpoint works, but the project is returning `Too Many Requests` during the full run. This is likely a request-rate or token-throughput limit for the API key/project. The old `openai==0.28.1` client reports only a short error string, so it does not expose detailed rate-limit headers in the current logs.

2. Resume checkpoint alignment bug.
   The original checkpoint logic saved only when `(idx + 1) % checkpoint_every == 0`. After resuming from 312 with batch size 32, batch ends were 344, 376, 408, etc., which never satisfy the same modulo alignment. Therefore, progress after the resume could be lost if the container stopped before the dataset finished.

Fix applied:

- `run_knowledge_models.py` now saves OpenAI Moderation scores after every successful API batch.
- This makes future resumes safe even if we intentionally stop the container.

Current preserved OpenAI score progress:

- `cache/openai_mod_openaimod_scores.json`: 312 / 1680 examples

Recommended next run:

- Resume from the 312-example checkpoint.
- Use `API_BATCH_SIZE=32`.
- Use deliberate pacing, e.g. `API_SLEEP=22` to stay under approximately 3 requests/minute.
- Keep the run in a named background container and inspect logs periodically.

Do not continue with rapid retry loops. If 429s still appear with 22-second spacing, increase `API_SLEEP` rather than decreasing batch size.
