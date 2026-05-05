# OpenAI Moderation Preflight Smoke

Status: `PASS`

Budget policy:

- Budget cap: `$10`
- Allowed endpoint: OpenAI Moderation only
- Disallowed: Chat Completions, Responses API, GPT generation, CoT, embeddings, images, Azure, Perspective, jailbreak attacks

Smoke results:

1. `results/openai_moderation_smoke.json`
   - `text-moderation-stable` failed because the model is unavailable.
   - `omni-moderation-latest` could not be passed explicitly through the repo's pinned `openai==0.28.1` client.
   - Default moderation endpoint worked and returned `omni-moderation-latest`.
   - Label: `RECONSTRUCTED-CURRENT-API`

2. `results/table2_openai_mod_smoke_n2.jsonl`
   - Ran `openai_mod` on 2 examples from each Table 2 dataset.
   - Datasets: `openaimod`, `toxicchat`, `xstest`, `overkill`, `beavertail`, `ours`
   - Used `--ignore_cache --not_save --api_batch_size 2`
   - Total moderation inputs: 12
   - No score caches were written.

3. `results/table2_official_style_smoke_n10.jsonl`
   - Ran offline official-style recompute smoke on 10 OpenAI Mod examples.
   - Components: `openai_mod`, `llamaguard`, `toxicchat-T5`
   - Rows tested: Ensemble, MLN, PC-like released-code `--AC_inference`
   - No OpenAI API calls were made during this inference smoke.

Conclusion:

The endpoint, dataset loading, batching, logging, and official-style inference path all passed smoke tests. Full OpenAI Mod scoring can proceed under the stated budget cap.
